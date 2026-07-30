# Prompt para Claude Code — Módulo 1: configuración versionada del cuestionario

Copia los tres archivos a `docs/modulo1/` en el repo antes de pegar este prompt:
`cuestionario_autodiagnostico_config.json`, `schema_modulo1_cuestionario.sql`, `SPEC_admin_config_cuestionario.md`.

---

Implementa la configuración versionada del cuestionario de autodiagnóstico (Módulo 1) usando los archivos en `docs/modulo1/`.

Antes de empezar: revisa `schema_modulo1_cuestionario.sql` y ajusta los FKs a `organizaciones` y `usuarios` si en nuestro esquema real de Fase 0 se llaman distinto.

Avanza en este orden, deteniéndote a esperar mi confirmación entre cada paso:

1. Convierte el DDL de `schema_modulo1_cuestionario.sql` en una migración Alembic.
2. Escribe un script de seed que cargue `cuestionario_autodiagnostico_config.json` en `obligaciones`, `secciones`, `preguntas`, y cree `config_versiones` v1 (activa=true) con sus filas de `config_seccion_pesos` y `config_pregunta_riesgo`. El JSON es la fuente de verdad, no inventes valores.
3. Implementa el endpoint de lectura (config activa completa) y el de guardado (nueva versión). En el guardado, valida en el service layer — antes de abrir la transacción — que las 10 secciones tengan peso, que sumen exactamente 100, y que las 50 preguntas tengan riesgo asignado. Si falla, responde 400 sin tocar la base de datos.
4. Implementa las dos pantallas de administrador según `SPEC_admin_config_cuestionario.md` (pesos por sección, riesgo por pregunta), protegidas por rol `superadmin`.
5. Test de RLS: confirma que un usuario sin rol `superadmin` recibe 403 al intentar guardar, y que las tablas tenant-scoped (`autodiagnosticos`, `autodiagnostico_respuestas`) siguen aislando por organización como en Fase 0.
