-- ============================================================================
-- CumpleIA · Módulo 1 (Autodiagnóstico) — Cuestionario, obligaciones y versionado
-- de parámetros de negocio (peso_pct por sección, riesgo por pregunta).
--
-- Supuestos sobre lo ya construido en Fase 0 (ajustar nombres si difieren):
--   - organizaciones(id UUID PK)   -> el tenant
--   - usuarios(id UUID PK)         -> con columna de rol ('superadmin', 'admin_pyme', 'usuario')
--   - Todas las tablas tenant-scoped usan RLS con current_setting('app.tenant_id')
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. CONTENIDO ESTRUCTURAL (global, NO tenant-scoped, NO versionado)
--    Fiel a la guía CCS. Cambiarlo es una decisión de producto/legal, no un
--    ajuste operativo: se modifica por migración de código, no desde el panel.
-- ----------------------------------------------------------------------------

CREATE TABLE obligaciones (
    id              TEXT PRIMARY KEY,              -- 'OB1'..'OB8'
    numero_guia     TEXT NOT NULL,                  -- '1.1'..'1.8', cita a la guía CCS
    nombre          TEXT NOT NULL,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE secciones (
    id              TEXT PRIMARY KEY,              -- 'S1'..'S10'
    numero_romano   TEXT NOT NULL,                  -- 'I'..'X'
    nombre          TEXT NOT NULL,
    obligacion_id   TEXT NOT NULL REFERENCES obligaciones(id),
    orden           SMALLINT NOT NULL,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE preguntas (
    id              TEXT PRIMARY KEY,              -- 'S1Q1'..'S10Q5'
    seccion_id      TEXT NOT NULL REFERENCES secciones(id),
    texto           TEXT NOT NULL,
    orden           SMALLINT NOT NULL,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 2. PARÁMETROS DE NEGOCIO VERSIONADOS (peso_pct, riesgo)
--    Editables desde el panel de administrador. Append-only: nunca se
--    actualiza una versión existente, solo se crea una nueva y se activa.
-- ----------------------------------------------------------------------------

CREATE TABLE config_versiones (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_version  INT NOT NULL UNIQUE,            -- 1, 2, 3... incremental
    activa          BOOLEAN NOT NULL DEFAULT false,
    nota            TEXT,                           -- comentario opcional del admin
    creado_por      UUID NOT NULL REFERENCES usuarios(id),
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Garantiza que solo una versión esté activa a la vez
CREATE UNIQUE INDEX ux_config_versiones_activa ON config_versiones (activa) WHERE activa;

CREATE TABLE config_seccion_pesos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id      UUID NOT NULL REFERENCES config_versiones(id),
    seccion_id      TEXT NOT NULL REFERENCES secciones(id),
    peso_pct        NUMERIC(5,2) NOT NULL CHECK (peso_pct >= 0 AND peso_pct <= 100),
    UNIQUE (version_id, seccion_id)
);

CREATE TABLE config_pregunta_riesgo (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id      UUID NOT NULL REFERENCES config_versiones(id),
    pregunta_id     TEXT NOT NULL REFERENCES preguntas(id),
    riesgo          TEXT NOT NULL CHECK (riesgo IN ('Alto', 'Medio', 'Bajo')),
    UNIQUE (version_id, pregunta_id)
);

-- Nota de aplicación: Postgres no valida sumas agregadas en un CHECK de fila.
-- La regla "suma de peso_pct de una version_id = 100" se valida en el service
-- layer (backend) ANTES del commit que crea la versión, junto con "las 50
-- preguntas deben tener riesgo" y "las 10 secciones deben tener peso".

-- ----------------------------------------------------------------------------
-- 3. RLS de las tablas de configuración: lectura abierta, escritura solo
--    superadmin, y sin UPDATE/DELETE (append-only real).
-- ----------------------------------------------------------------------------

ALTER TABLE config_versiones ENABLE ROW LEVEL SECURITY;
ALTER TABLE config_seccion_pesos ENABLE ROW LEVEL SECURITY;
ALTER TABLE config_pregunta_riesgo ENABLE ROW LEVEL SECURITY;

CREATE POLICY config_versiones_select ON config_versiones
    FOR SELECT USING (true);
CREATE POLICY config_versiones_insert ON config_versiones
    FOR INSERT WITH CHECK (current_setting('app.rol', true) = 'superadmin');

CREATE POLICY config_seccion_pesos_select ON config_seccion_pesos
    FOR SELECT USING (true);
CREATE POLICY config_seccion_pesos_insert ON config_seccion_pesos
    FOR INSERT WITH CHECK (current_setting('app.rol', true) = 'superadmin');

CREATE POLICY config_pregunta_riesgo_select ON config_pregunta_riesgo
    FOR SELECT USING (true);
CREATE POLICY config_pregunta_riesgo_insert ON config_pregunta_riesgo
    FOR INSERT WITH CHECK (current_setting('app.rol', true) = 'superadmin');

-- Deliberadamente no se crean políticas de UPDATE ni DELETE para estas tres
-- tablas: sin política definida, RLS deniega el acceso por defecto.

-- ----------------------------------------------------------------------------
-- 4. DIAGNÓSTICOS (tenant-scoped) — referencian la versión de config vigente
--    al momento de generarse, para que el informe sea reproducible aunque el
--    admin ajuste pesos/riesgo después (principio de evidencia).
-- ----------------------------------------------------------------------------

CREATE TABLE autodiagnosticos (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES organizaciones(id),
    config_version_id   UUID NOT NULL REFERENCES config_versiones(id),
    estado              TEXT NOT NULL DEFAULT 'en_progreso'
                            CHECK (estado IN ('en_progreso', 'completado')),
    puntaje_global      NUMERIC(5,2),               -- calculado al completar, con la fórmula del config
    creado_por          UUID NOT NULL REFERENCES usuarios(id),
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT now(),
    completado_en       TIMESTAMPTZ
);

CREATE TABLE autodiagnostico_respuestas (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    autodiagnostico_id      UUID NOT NULL REFERENCES autodiagnosticos(id) ON DELETE CASCADE,
    pregunta_id             TEXT NOT NULL REFERENCES preguntas(id),
    respuesta               TEXT NOT NULL CHECK (respuesta IN ('Sí', 'Parcial', 'No', 'N/A')),
    respondido_en           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (autodiagnostico_id, pregunta_id)
);

ALTER TABLE autodiagnosticos ENABLE ROW LEVEL SECURITY;
ALTER TABLE autodiagnostico_respuestas ENABLE ROW LEVEL SECURITY;

CREATE POLICY autodiagnosticos_tenant_isolation ON autodiagnosticos
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY autodiagnostico_respuestas_tenant_isolation ON autodiagnostico_respuestas
    USING (
        autodiagnostico_id IN (
            SELECT id FROM autodiagnosticos
            WHERE tenant_id = current_setting('app.tenant_id', true)::uuid
        )
    );

-- ----------------------------------------------------------------------------
-- 5. Flujo de guardado desde el panel admin (referencia para el backend, no
--    ejecutable como está — resume la transacción que dispara "Guardar cambios"):
--
--   BEGIN;
--     INSERT INTO config_versiones (numero_version, nota, creado_por, activa)
--       VALUES (<max(numero_version)+1>, <nota>, <usuario_id>, true);
--     INSERT INTO config_seccion_pesos (version_id, seccion_id, peso_pct) ...   -- 10 filas
--     INSERT INTO config_pregunta_riesgo (version_id, pregunta_id, riesgo) ...  -- 50 filas
--     UPDATE config_versiones SET activa = false
--       WHERE id <> <nueva_version_id> AND activa = true;
--   COMMIT;
--
--   Validación previa en el backend (antes del BEGIN): suma(peso_pct) = 100,
--   10 secciones presentes, 50 preguntas presentes. Si falla, se rechaza con
--   400 y no se abre transacción.
-- ----------------------------------------------------------------------------
