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

### Deuda técnica menor detectada en la revisión del PR #13 (no bloqueante)

Los hallazgos #1 (RLS de `org_visibility` bloqueaba a un superadmin sin membresía) y #2 (informe obsoleto en silencio tras reabrir respuestas) de esa revisión se trataron como fix prioritario, no como backlog — ver migración `0007_org_visibility_superadmin.py` y la invalidación en `app/services/diagnostico.py::recalcular_diagnostico`. Quedan como backlog legítimo (bajo esfuerzo, bajo riesgo):

- [ ] **Narrativas duplicadas por `finding_id` no se deduplican:** el schema de `generate_structured` no impone unicidad de `finding_id` dentro de `narrativas[]`; si el LLM devolviera dos entradas para el mismo hallazgo, el guardarraíl actual (que solo valida pertenencia, no unicidad) dejaría pasar ambas.
- [ ] **Falta test del filtro `Finding.status != FindingStatus.cerrado`** en `generar_informe`: ningún test de `test_diagnostico_ia.py` cubre un hallazgo ya cerrado — si ese filtro se rompiera en un refactor futuro (narrando también brechas resueltas), ningún test lo detectaría hoy.

## Exportación del informe (Fase 1, Módulo 1, Tarea 5)

`GET /diagnostico/informe/exportar` (`app/services/diagnostico_exportacion.py`) sirve el informe ya generado (Tarea 4) como HTML autocontenido y descargable — resumen ejecutivo, puntaje global y por sección, y el detalle de cada hallazgo (riesgo, sección, narrativa con sus citas, acción correctiva, responsable). 404 sin diagnóstico vigente, 409 si el informe todavía no fue generado (mismo contrato que `POST /informe`), solo requiere `view_content`. Empieza simple a propósito (HTML imprimible a PDF desde el navegador, sin agregar WeasyPrint u otro motor de PDF todavía) — ver la Tarea 5 del plan. Todo texto que no viene del catálogo fijo (nombre de organización, resumen/narrativas del LLM, descripción/acción/responsable de un hallazgo) se escapa con `html.escape`, verificado con un intento de `<script>` real en la verificación en vivo.

### Backlog derivado — Exportación

- [ ] **PDF real:** sigue pendiente para cuando el Módulo 4 (generador de documentos) exista o si una PYME lo pide antes — hoy el usuario debe usar "Imprimir → Guardar como PDF" del navegador sobre el HTML exportado.
- [x] **Descarga desde el frontend:** resuelto en la Tarea 6 (`ResultadosDashboard.tsx::handleDescargar`, fetch con Bearer token + Blob URL, ya que el navegador no puede mandar el header `Authorization` desde un `<a href>` plano).
- [ ] **Respuestas crudas no incluidas:** decisión explícita (no diferida por falta de tiempo): el anexo con el detalle de las 50 respuestas se reserva para la Carpeta de Evidencia (Módulo 5, de pago) en vez de regalarse en el informe gratuito del Módulo 1 (freemium) — ver nota de estrategia más abajo. El dashboard en pantalla (`ResultadosDashboard.tsx`) ya muestra un aviso "Anexo de respuestas — disponible en la Carpeta de Evidencia" a modo de preview del upsell.

## Frontend del Autodiagnóstico (Fase 1, Módulo 1, Tarea 6)

Wizard del cuestionario por sección + dashboard de resultados + descarga del informe, bajo `/dashboard/autodiagnostico` (`frontend/components/autodiagnostico/`: `AutodiagnosticoWorkspace`, `Cuestionario`, `ResultadosDashboard`). Decisiones tomadas antes de construir (sin selector de organización ni tests de frontend preexistentes en el repo):

- **Organización activa:** se asume una sola organización por usuario (`GET /me/organizations`); si hay más de una se muestra un `<select>` local sin contexto global — no hay onboarding ni selector persistente todavía, y no era el alcance de esta tarea construirlo.
- **Navegación del wizard:** una sola ruta con estado interno en React (tabs/paso actual), sin URL por sección — el catálogo es chico (50 preguntas) y no había precedente de rutas dinámicas en el repo.
- **Sin tests automatizados de frontend:** consistente con que todo el proyecto no tenía ningún framework de testing de frontend configurado antes de esta tarea (ni Jest, ni Vitest, ni Playwright) — verificación manual en navegador real.

### Backlog derivado — Frontend

- [ ] **Selector/contexto global de organización:** si alguna vez un usuario pertenece a más de una organización de verdad, el `<select>` local de `AutodiagnosticoWorkspace` no escala a otras pantallas futuras — evaluar un contexto de React reusable en ese momento.
- [ ] **Testing de frontend:** no hay ningún framework instalado; si se decide adoptar uno, es una decisión de alcance mayor (nueva dependencia a justificar en `CLAUDE.md`) que aplica a todo el proyecto, no solo a este módulo.

## Mejoras al informe de Autodiagnóstico (revisión manual, 2026-08-10)

Origen: `Claude_22_julio_2026/mejoras-informe-autodiagnostico.md` (revisión manual de un informe real exportado). De los 9 ítems + 1 bug del documento, se resolvieron en esta ronda:

- **BUG-01 (desfase entre conteo narrativo y hallazgos listados):** el resumen ejecutivo del LLM podía declarar un número de brechas que no coincidiera con `len(hallazgos)` — dos fuentes de verdad para el mismo dato. La regla 5 del system prompt (`app/services/diagnostico_ia.py`) le pide al LLM que no declare esa cifra, pero **verificado en producción que la instrucción sola no bastó** (el modelo siguió declarando un número, ej. "35" cuando el real era 34). Fix definitivo: `_quitar_conteo_de_brechas` (guardarraíl determinista con regex, no solo la instrucción) quita del texto libre cualquier número seguido de "brecha(s)"/"hallazgo(s)" antes de persistirlo — cubierto por `test_generar_informe_quita_conteo_de_brechas_declarado_por_el_llm`. El conteo exacto sigue viviendo solo en el bloque determinista del informe exportado (ítem 2).
- **Ítem 1 (encabezado de identificación):** agregado solo al HTML exportado (`app/services/diagnostico_exportacion.py`), no al dashboard en pantalla — nombre, RUT, rubro y tamaño de la organización, quién respondió (perfil `updated_by` del diagnóstico) y su rol de membresía como proxy de "cargo" (no existe un campo de puesto/cargo real en `Profile` todavía), ID del diagnóstico y fecha. "Tamaño" muestra el valor libre `organizations.size`, no una clasificación PYME/gran empresa por umbral legal (esa clasificación no existe en el código).
- **Ítem 2 (conteo de hallazgos por riesgo):** bloque determinista Alto/Medio/Bajo/Total en el informe exportado, antes de la tabla por sección. Solo el total global, sin desagregado por sección ni gráfico (barras/donut) — se prefirió mantenerlo simple; ver backlog derivado abajo.
- **Ítem 3 (trazabilidad respuesta + riesgo base/ajustado):** `HallazgoOut` (API) y el HTML exportado ahora muestran la respuesta original de la pregunta y, cuando "Parcial" degrada el riesgo, tanto el riesgo base del catálogo como el ajustado ("Riesgo Medio — base Alto, ajustado por respuesta Parcial"). Se agregó también una sección de Metodología (escala de respuesta, cálculo de puntaje, regla de degradación) en el HTML exportado.
- **Trazabilidad de quién respondió (pedido del usuario, no del documento original):** `diagnostic_answers` ahora tiene `created_by`/`updated_by`/`updated_at` (migración `0008_diagnostic_answers_auditoria.py`); `Diagnostic.updated_by` se actualiza en cada `POST /diagnostico/respuestas`, y `Diagnostic`/`Finding.updated_at` tienen `onupdate=func.now()`. Antes de este fix, ninguna tabla del Autodiagnóstico registraba quién editó una respuesta ni cuándo — brecha real respecto a la convención de auditoría de `CLAUDE.md`.

### Backlog derivado — Mejoras al informe (ítems 4-9 del documento, diferidos por decisión explícita del usuario)

- [ ] **Ítem 2 (fase 2):** desagregado del conteo de hallazgos por sección y/o gráfico simple (barras o donut) — se implementó solo el total global.
- [ ] **Ítem 4 — Contenido accionable:** recomendación de acción concreta, responsable (rol) y plazo indicativo por severidad (Alto=30 días, Medio=90, Bajo=180) por hallazgo; exportar como plan de acción independiente (Excel/tabla) es fase 2 dentro del ítem.
- [ ] **Ítem 5 — Nota de DPD en autodesignación:** detectar cuando el Gerente General (u otro cargo directivo) se autodesigna delegado de protección de datos y agregar una nota sobre la alternativa de designar a un tercero (incluyendo que CumpleIA puede prestar ese servicio).
- [ ] **Ítem 6 — Fundamento legal por hallazgo:** citar el artículo específico de la Ley N.° 21.719 en hallazgos de riesgo Alto (al menos), extensible a todos si el catálogo llega a tener ese mapeo.
- [ ] **Ítem 7 — Preguntas N/A:** mostrar por sección cuántas preguntas quedaron en N/A vs. respondidas, para no leer un puntaje de sección como si estuviera completo cuando no lo está.
- [ ] **Ítem 8 — Comparación histórica (fase 2):** requiere que exista más de un `Diagnostic` por organización — hoy es get-or-create, a lo sumo uno (ver backlog de Autodiagnóstico más arriba, "Re-evaluaciones").
- [ ] **Ítem 9 — Cierre formal:** bloque de validación/firma (nombre, cargo, fecha) del responsable que revisa, y etiqueta de clasificación de confidencialidad del documento.

### Nota de estrategia — freemium vs. Carpeta de Evidencia (decisión del usuario, 2026-08-10)

El anexo de respuestas crudas y, en general, cualquier bitácora de auditoría fina (quién respondió qué y cuándo) se reserva deliberadamente para la Carpeta de Evidencia (Módulo 5, de pago) en vez de incluirse gratis en el informe del Autodiagnóstico (Módulo 1, "gancho freemium"). El resumen + puntajes + hallazgos ya bastan para mostrarle a la PYME que tiene brechas; el valor probatorio detallado (evidencia formal ante la Agencia) es lo que debería empujar la conversión a suscripción. Los campos de auditoría (`created_by`/`updated_by`/`updated_at`) sí se construyeron ya en el modelo de datos porque son la base necesaria para que el Módulo 5 los explote más adelante — no se exponen todavía como anexo en el informe gratuito.
