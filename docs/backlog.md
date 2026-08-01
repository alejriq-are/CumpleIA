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

### Deuda técnica menor detectada en la revisión de PR #11 (no bloqueante)

- [ ] `recalcular_diagnostico` indexa `hallazgos_existentes` por `pregunta_id`: si algún módulo futuro (RAT, etc.) llegara a crear un `Finding` con `diagnostic_id` seteado pero `pregunta_id=None`, dos de esas filas colisionarían en el dict y la de cierre automático podría marcar como `cerrado` un hallazgo que no le corresponde. Hoy no hay ningún escritor de `Finding` en esa combinación — revisar si Tarea 4/RAT llega a crearla.
- [ ] `_construir_actual_out` (app/api/diagnostico.py) reutiliza `obtener_config_por_id`, que trae `peso_por_seccion`/`riesgo_por_pregunta`/el `Profile` de `creado_por` sin necesitarlos (solo usa `secciones`/`preguntas`). Irrelevante en latencia a esta escala; una función de solo-lectura más liviana sería más prolija si el catálogo crece.
- [ ] `_limpiar_diagnostico*_org_a` está duplicada entre `tests/test_api_diagnostico.py` y `tests/test_diagnostico_service.py` (ambas necesarias por el `UNIQUE` nuevo en `diagnostics.organization_id`). Candidata a moverse a `conftest.py` como fixture compartida.
- [ ] El umbral de "diagnóstico completado" (`len(respuestas_input) >= len(config.preguntas)`) depende del tamaño *actual* del catálogo global (`Pregunta`), no de uno fijado al crear el diagnóstico — hoy es inofensivo porque el catálogo se trata como contenido fijo (Tarea 0), pero si alguna vez se vuelve editable habría que pinnear también el conteo de preguntas, no solo pesos/riesgo.

## Capa de IA del Autodiagnóstico (Fase 1, Módulo 1, Tarea 4)

Tarea 4 completa: `POST /diagnostico/informe` (solo con el diagnóstico `completado`, 409 si no) genera la narrativa vía `app/services/diagnostico_ia.py`, anclada por RAG a `ley_21719`/`guia_ccs` (`app/services/rag.py::search_chunks(sources=...)`, `ley_19628` excluida a pedido explícito) con tool-calling forzado (`LLMClient.generate_structured`, `app/services/providers/llm.py`). El riesgo y el mapeo a las 8 obligaciones **no los decide el LLM**: siguen siendo 100% deterministas (motor de puntaje de la Tarea 2 + cadena `Pregunta→Seccion→Obligacion` del catálogo de la Tarea 0) — el LLM solo redacta sobre datos ya resueltos.

Guardarraíl verificado con una llamada real (no solo mockeada): cualquier cita que no corresponda a un fragmento efectivamente recuperado por RAG, o un `finding_id` que no pertenezca al diagnóstico, se descarta en silencio (log) antes de persistir `Diagnostic.informe_ia`. En la corrida de verificación real, el modelo devolvió 4 citas y el guardarraíl descartó 3 por no calzar con los fragmentos recuperados — comportamiento esperado, no un bug.

### Backlog derivado — Capa de IA

- [ ] **Aprobación/revisión humana formal del informe:** hoy el informe se muestra como salida de un diagnóstico ya completado (borrador implícito), pero no hay un flujo explícito de "revisar y aprobar" como el que tendrán los documentos generados del Módulo 4 (`Document.status`: borrador/aprobado/archivado). Evaluar si el informe del Autodiagnóstico necesita ese mismo flujo o si basta con la revisión editorial que ya permite regenerar (`POST /informe` sobrescribe).
- [ ] **Regeneración sin versionado:** cada `POST /diagnostico/informe` sobrescribe `informe_ia` — no hay historial de versiones del informe. Aceptable para el MVP ("simple, económico"); revisar si se necesita conservar informes anteriores cuando exista carpeta de evidencia (Módulo 5).
- [ ] **Costo/latencia de RAG por informe:** hoy se hace una sola consulta de retrieval agregada (no una por hallazgo) — correcto para costo, pero no se ha medido con diagnósticos de muchas brechas simultáneas (hasta 50). Revisar si `top_k=12` sigue siendo suficiente/necesario a esa escala.
- [ ] **Capa 3 del ADR 0002 (`reference_documents`)** sigue sin endpoint de carga (ver sección de Tarea 3 arriba) — el informe de la Tarea 4 no los referencia todavía porque no hay ninguno cargado.
