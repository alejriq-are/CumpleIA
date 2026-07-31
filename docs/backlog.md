# Backlog — CumpleIA

> Primer archivo de backlog trackeado en git. Hasta ahora el seguimiento de tareas vivía en archivos `Claude_*`/`Fase 1`/`Modulo 1` sin trackear (`git status` los marca `??`); este archivo empieza a fijar en el repo los ítems con criterios de aceptación explícitos, empezando por el de este trabajo.

## Modelo de organizaciones, roles y suscripción

Ver `docs/adr/0001-modelo-organizaciones-roles-suscripcion.md`.

- [x] Existen las entidades `Organization`, `Profile` (usuario), rol de organización (`Membership.role`), admin de plataforma (`profiles.is_superadmin`) y `Subscription`, migradas y documentadas.
- [x] Toda tabla nueva de este trabajo (`subscriptions`) incluye `organization_id` con RLS.
- [x] Existe una función de autorización (`has_permission`/`role_has_permission`, `app/services/authorization.py`) y una de estado de suscripción (`get_subscription_status`/`is_subscription_active`, `app/services/subscriptions.py`), ambas con tests unitarios.
- [x] Existe una organización semilla con un admin para desarrollo (`scripts/seed_dev.py`), ahora también con su `Subscription`.
- [x] El ADR está commiteado y referenciado desde este backlog.
- [x] No se tocó ninguna pantalla de administración de organizaciones ni integración de pagos (fuera de alcance).

### Backlog derivado — fase de Monetización (no construir todavía)

- [ ] Integración con pasarela de pago real (Stripe/Mercado Pago) que actualice `subscriptions.status` según el resultado de cobro.
- [ ] Job/flujo de dunning: mover `active` → `grace` (con `grace_until`) en compromisos anuales ante un fallo de cobro mensual aislado, y `active` → `suspended` directo en planes mensuales puros.
- [ ] UI de administración de organizaciones y de suscripción.
- [ ] Flujo de invitación de un segundo usuario a una organización existente, con asignación de rol por el admin de organización (`Permission.manage_members`, ya modelado en `app/services/authorization.py`, sin endpoint todavía).

## Autodiagnóstico (Fase 1, Módulo 1)

Ver `Fase 1/plan-fase1-modulo1-autodiagnostico.md` y `docs/adr/0002-logica-adaptativa-riesgo-remediacion.md`. Tareas 0-3 completas:

- Tarea 0: catálogo CCS versionado (50 preguntas / 10 secciones / 8 obligaciones).
- Tarea 1: modelo `Diagnostic`/`DiagnosticAnswer`/`Finding` con RLS real.
- Tarea 2: motor de puntaje determinista, sin LLM (`app/services/diagnostico_puntaje.py`).
- Tarea 3: API (`GET /diagnostico/cuestionario`, `POST /diagnostico/respuestas`, `GET /diagnostico/actual`, `app/api/diagnostico.py` + `app/services/diagnostico.py`), primer uso real de `require_permission`. "Diagnóstico vigente" es get-or-create (a lo sumo uno por organización, `diagnostics.organization_id` UNIQUE); las brechas resueltas se cierran (`status='cerrado'`), no se borran.

### Backlog derivado — Autodiagnóstico

- [ ] **Capa 1 del ADR 0002 (aplicabilidad de preguntas por rubro/tamaño):** el catálogo no tiene ese dato todavía; `GET /diagnostico/cuestionario` devuelve las 50 preguntas a toda organización por igual.
- [ ] **Catálogo `instructivo_agencia` (ADR 0002, capa 3):** catálogo global (sin `organization_id`, análogo a `Obligacion`/`Seccion`/`Pregunta`) para los instructivos que emita el Consejo Directivo de la Agencia de Protección de Datos — no antes de oct-dic 2026 (Consejo Directivo en proceso de ratificación a la fecha del ADR).
- [ ] **Endpoint de carga/vinculación de `reference_documents`:** la tabla y el modelo ya existen (migración 0005) con `tipo='politica_interna_gobernanza'`, y `GET /diagnostico/actual` ya devuelve `hallazgos[].documentos_referencia` (vacío hoy) — falta el endpoint para que una organización cree/vincule sus propios documentos.
- [ ] **Re-evaluaciones (historial de diagnósticos):** hoy una organización tiene a lo sumo un `Diagnostic` para siempre (get-or-create). Iniciar un nuevo ciclo de evaluación tras completar uno queda fuera de alcance de la Tarea 3.
- [ ] Tarea 4 (capa de IA con guardarraíles) y Tarea 5 (exportación del informe, con variación de profundidad por riesgo — capa 4 del ADR 0002) siguen pendientes según el plan original.
- [ ] Tarea 6 (frontend: wizard, dashboard, descarga del informe).
