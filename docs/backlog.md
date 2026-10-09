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

Ver `Fase 1/plan-fase1-modulo1-autodiagnostico.md` y `docs/adr/0002-logica-adaptativa-riesgo-remediacion.md`. Tareas 0-6 completadas para el MVP del Módulo 1:

- Tarea 0: catálogo CCS versionado (50 preguntas / 10 secciones / 8 obligaciones).
- Tarea 1: modelo `Diagnostic`/`DiagnosticAnswer`/`Finding` con RLS real.
- Tarea 2: motor de puntaje determinista, sin LLM (`app/services/diagnostico_puntaje.py`).
- Tarea 3: API (`GET /diagnostico/cuestionario`, `POST /diagnostico/respuestas`, `GET /diagnostico/actual`, `app/api/diagnostico.py` + `app/services/diagnostico.py`), primer uso real de `require_permission`. "Diagnóstico vigente" es get-or-create (a lo sumo uno por organización, `diagnostics.organization_id` UNIQUE); las brechas resueltas se cierran (`status='cerrado'`), no se borran.

### Backlog derivado — Autodiagnóstico

- [ ] **Capa 1 del ADR 0002 (aplicabilidad de preguntas por rubro/tamaño):** el catálogo no tiene ese dato todavía; `GET /diagnostico/cuestionario` devuelve las 50 preguntas a toda organización por igual.
- [ ] **Catálogo `instructivo_agencia` (ADR 0002, capa 3):** catálogo global (sin `organization_id`, análogo a `Obligacion`/`Seccion`/`Pregunta`) para los instructivos que emita el Consejo Directivo de la Agencia de Protección de Datos — no antes de oct-dic 2026 (Consejo Directivo en proceso de ratificación a la fecha del ADR).
- [ ] **Endpoint de carga/vinculación de `reference_documents`:** la tabla y el modelo ya existen (migración 0005) con `tipo='politica_interna_gobernanza'`, y `GET /diagnostico/actual` ya devuelve `hallazgos[].documentos_referencia` (vacío hoy) — falta el endpoint para que una organización cree/vincule sus propios documentos.
- [ ] **Re-evaluaciones (historial de diagnósticos):** hoy una organización tiene a lo sumo un `Diagnostic` para siempre (get-or-create). Iniciar un nuevo ciclo de evaluación tras completar uno queda fuera de alcance de la Tarea 3.
- [x] Tarea 4 (capa de IA con guardarraíles) y Tarea 5 (exportación HTML del informe) completadas. Ver las secciones específicas más abajo.
- [x] Tarea 6 completada: frontend con wizard, dashboard y descarga del informe. Ver la sección específica más abajo.


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

## Módulo 2 — M2-T3.0, activación del RAT

- [x] `Treatment` guarda declaraciones explícitas `si`/`no`/`pendiente` para sistemas, terceros/proveedores y transferencias internacionales; `null` representa ausencia de declaración.
- [x] Activación server-side exige nombre, rol, una finalidad, categoría de datos, categoría de titulares, fuente de datos, regla de conservación y las tres declaraciones.
- [x] Transiciones permitidas: borrador→activo, activo→borrador, activo→archivado, borrador→archivado y archivado→activo; ambas activaciones validan requisitos.
- [x] M2-T3.1: listado RAT y navegación frontend.

## Módulo 2 — M2-T3.1, listado RAT y navegación frontend

**Estado:** DONE (2026-09-16)

- [x] Vista `/dashboard/rat`.
- [x] Integración con `GET /rat/treatments`.
- [x] Selector de organización.
- [x] Estados loading, empty y error.
- [x] UX específica para HTTP 402 y 403.
- [x] CTA `Nueva actividad`.
- [x] Navegación a `/dashboard/rat/nuevo`.
- [x] Navegación a `/dashboard/rat/[treatmentId]`.
- [x] Tarjeta RAT habilitada en dashboard.
- [x] TypeScript PASS.
- [x] Next production build PASS.

**M2-T3.2 completado. Siguiente:** M2-T3.3 — finalidades, categorías de datos, titulares y fuentes.

## Módulo 2 — M2-T3.2, información general RAT

**Estado:** DONE (2026-09-16)

- [x] Crear actividad desde `/dashboard/rat/nuevo`.
- [x] Cargar detalle desde `/dashboard/rat/[treatmentId]`.
- [x] Editar y guardar información general.
- [x] Integración con `POST`, `GET` y `PATCH /rat/treatments`.
- [x] Nombre, descripción, área de negocio y rol de la organización.
- [x] Descripción general del flujo de datos.
- [x] Fecha de inicio y próxima revisión.
- [x] Regla de conservación y método de eliminación.
- [x] Decisiones automatizadas y descripción condicional.
- [x] Barra de preparación basada en 10 requisitos de activación.
- [x] Estado visual `borrador` → `Registro en preparación`.
- [x] Advertencia de que el avance no representa cumplimiento legal.
- [x] Prueba funcional de creación, edición y listado.
- [x] TypeScript PASS.
- [x] Next production build PASS.

**Siguiente:** M2-T3.3 — finalidades, categorías de datos, titulares y fuentes.


## Módulo 3 — M3-T1, persistencia y reglas de bases de licitud

**Estado:** EN PROGRESO (revisión 2026-10-06).

Matriz de implementación, evidencia y brechas en
[Revisión de aceptación M3-T1](project/m3-t1-revision-aceptacion.md).
Diseño y alcance en [Bases de licitud](project/modulo3-licitud-diseno.md).
Última suite completa registrada: 2234 passed (§58); no acredita cierre integral.

- [x] Núcleo persistente, alcance por finalidad, snapshot/hash, RLS y lifecycle.
- [x] Seis bases ordinarias; geolocalización y consentimiento expreso sensible
  del titular con preparación, asociaciones y barreras de confirmación.
- [x] Screening EIPD; positivos/pendientes mantienen bloqueo.
- [x] Completar evidencia HTTP conjunta sensible/geolocalización (4 casos
  focalizados aprobados: pérdida de preparación, EIPD y conservación/reemplazo).
- [x] Ampliar concurrencia con constructor RAT real: consentimiento con
  sensibilidad/geolocalización, 8 casos nuevos; otras cinco bases conservan
  cobertura de concurrencia con RAT simulado.
- [x] Priorizar próximo régimen: salud/perfil biológico; primer alcance
  documental por consentimiento expreso, diseño §31.
- [x] Definir contrato/matriz documental de salud (§32).
- [x] Implementar schema de salud y pruebas (§33: 49 pruebas nuevas).
- [x] Persistencia/exposición de salud y asociaciones compatibles (§34).
- [x] Evaluador de salud y readiness (§35).
- [x] Integración del gate de salud para primer soporte; restricciones y EIPD conservados (§36).
- [x] HTTP conjunto salud/sensible/geolocalización y concurrencia de salud con RAT real
  por consentimiento_art12/contexto otro (§37: 18 casos nuevos; 35 verificaciones focalizadas).
- [x] Revisar alcance de representación sensible y criterios de cierre M3-T1 (§38);
  revisión no equivale a cierre ni habilita representación.
- [x] Verificar por HTTP representante_legal/mandatario en sensible, con y sin salud:
  rechazo, conservación del vigente y reparación a titular.
- [x] Validación integral posterior a representación (§39): 1429 passed.
- [x] Revisión focalizada de cambios y cadena Alembic (§40): head aplicado,
  46 archivos con formato/lint correctos; tablas M3 sin diferencias autogenerate.
- [x] Investigar/corregir drift global de metadata sin eliminar índices (§41):
  29 índices declarados y nombre de unique alineado; alembic check aprobado.
- [x] Preparar propuesta concreta de entrega inicial y pendientes (§42):
  [Propuesta de alcance](project/m3-t1-propuesta-entrega.md).
- [x] Decisión explícita: continuar alcance integral (§43); entrega inicial no
  adoptada como recorte de cierre.
- [x] Actualizar aceptación según decisión integral (§43).
- [x] Biometría: contrato/matriz de primera ruta consentimiento expreso (§44).
- [x] Biometría: schemas y pruebas (§45: 53 casos nuevos; 150 contratos aprobados).
- [x] Biometría: persistencia/API/asociaciones compatibles (§46): diez casos HTTP;
  suite integral 1492 passed y Alembic check aprobado.
- [x] Biometría: evaluador puro/readiness (§47): 73 pruebas puras y un caso HTTP
  nuevos; suite integral 1566 passed.
- [x] Biometría: integrar gate/EIPD y HTTP de primera ruta (§48): 19 pruebas
  transversales nuevas; suite integral 1585 passed.
- [x] Biometría: HTTP seis bases y concurrencia con RAT real (§49): 22 casos
  nuevos; 58 verificaciones focalizadas. Concurrencia real: consentimiento_art12.
- [x] Delimitar primera excepción biométrica: derechos art16ter -> art16bis(d),
  con dependencia sensible art16d y barrera EIPD conservada (§50).
- [x] Diseñar contratos/matriz de excepción sensible y biométrica de derechos (§51).
- [x] Implementar schemas/pruebas de ambas excepciones (§52): 102 casos nuevos,
  252 contratos seleccionados aprobados.
- [x] Persistencia/API de ambas excepciones (§53), con barrera explicita
  mientras falta cobertura de asociaciones y tres casos HTTP aprobados.
- [x] Asociaciones especiales v10/EIPD v11 de ambas excepciones (§54), con
  comparadores historicos, obsolescencia y reaporte explicito; 118 casos nuevos.
- [x] Evaluador puro de preparacion/aplicabilidad sensible de derechos (§55);
  172 casos aprobados, sin habilitar confirmacion.
- [x] Readiness e integracion sensible en detector/gates (§56), residualidad
  explicita en ambos sentidos y EIPD conservado; doce casos nuevos.
- [x] Evaluador puro biometrico de derechos y vinculos sensibles (§57),
  208 casos aprobados, sin habilitar confirmacion.
- [x] Readiness e integracion biometrica en detector/gates (§58), residualidad
  explicita y EIPD conservado; doce casos nuevos, sin confirmar excepciones.
- [x] Delimitar resolucion EIPD acotada (§59): registro externo, revision humana
  trazable y gate separado; screening positivo conservado, sin habilitacion actual.
- [ ] Contratos/matriz, schemas, persistencia/eventos y evaluadores de resolucion
  EIPD; aislamiento, obsolescencia y concurrencia antes de habilitar la frontera.
- [ ] Verificar/registrar listas y orientaciones oficiales aplicables antes de
  desbloquear confirmaciones; busqueda acotada no acredita inexistencia.
- [ ] Completar demás excepciones biométricas dentro del alcance integral.
- [ ] Completar representación, excepciones sensibles/salud y contextos restringidos,
  infancia/adolescencia, investigación y alcance granular según diseño propio.
- [ ] Validación y revisión final del alcance integral antes de declarar DONE.

Workflow completo EIPD diferido; frontend M3 no se agrega como requisito de
esta tarea mediante esta revisión. Sin cierre DONE ni commit.

- [x] M3-T1 §60: contratos/matriz de resolucion EIPD, documento parcial, condicionales y revision humana con campos de servidor definidos (solo diseño).
- [x] M3-T1 §61: schemas separados de resolucion/revision EIPD y 111 pruebas de contrato implementados; 419 pruebas de schemas aprobadas.
- [x] M3-T1 §62: asociacion/hash de resolucion v1 puros implementados; 89 pruebas nuevas y 296 focalizadas aprobadas.
- [x] M3-T1 §63: persistencia JSONB y eventos append-only/RLS de resolucion EIPD; migracion b51d3f6a9c20 y 36 casos PostgreSQL, suite integral 2470 passed.
- [x] M3-T1 §64: API documental/binding de resolucion EIPD; 25 HTTP con RAT real y suite integral 2495 passed, historial conservado.
- [x] M3-T1 §65: evaluador puro de preparacion documental EIPD; 159 pruebas nuevas y 455 focalizadas aprobadas, sin habilitar confirmacion.
- [x] M3-T1 §66: readiness documental y vigencia de ultima revision EIPD; 18 pruebas nuevas aprobadas, sin habilitar confirmacion.
- [x] M3-T1 §67: prerequisitos puros de revision EIPD; 38 pruebas nuevas y 215 focalizadas aprobadas; continuar bloqueado por frontera/fuentes pendientes.
- [x] M3-T1 §68: accion autenticada de revision EIPD, campos de servidor, historial y relectura bajo lock; 15 pruebas nuevas aprobadas.
- [ ] M3-T1: frontera/gates, concurrencia ampliada y fuentes pendientes antes de habilitar confirmacion.

- [x] M3-T1 §69: registro trazable de busqueda/fuentes EIPD y propuesta temporal; listas/orientaciones no verificadas, requisito global pendiente.

- [x] M3-T1 §70: base normativa fija autorizada por usuario y matriz/contrato de primera frontera EIPD, sin dependencia de fecha de entrada en vigor.
- [x] M3-T1 §71: evaluador puro de frontera §70 implementado; 106 pruebas nuevas y 695 focalizadas aprobadas, screening v1 preservado.
- [x] M3-T1 §72: deteccion EIPD v2 pura y nucleo compartido con v1; positivos e historia conservados, 56 pruebas nuevas.
- [x] M3-T1 §73: readiness v2/frontera separado y versionado, contexto RAT actual y contratos cerrados; 14 pruebas nuevas.
- [ ] M3-T1: composicion compartida, fuentes complementarias/aceptacion antes de habilitar continuar.

- [x] M3-T1 §74: contrato/matriz de composicion comun EIPD y separacion revision/confirmacion, sin circularidad.
- [x] M3-T1 §75: composicion pura §74 implementada; 80 pruebas nuevas y 468 focalizadas aprobadas, sin habilitar gates.
- [x] M3-T1 §76: composicion orientativa en readiness, contratos cerrados y 17 pruebas nuevas; bloqueos conservados.
- [x] M3-T1 §77: composicion compartida bajo lock en revision positiva/confirmacion; barreras conservadas y seis casos nuevos.
- [x] M3-T1 §78: concurrencia real de confirmacion y HTTP seis bases ordinarias para composicion; ocho casos adicionales.
- [x] M3-T1 §79: revision de aceptacion acotada y revalidacion registrada de fuentes; frontera no habilitada, instrumento complementario no verificado.
- [x] M3-T1 §80: HTTP preparado de ambas rutas protegidas con/sin negativa previa; cuatro casos nuevos y barreras conservadas.
- [x] M3-T1 §81: concurrencia real de ambas rutas protegidas preparadas, revision/confirmacion y commit/rollback; ocho casos nuevos.
- [x] M3-T1 §82: aceptacion §§80-81 actualizada y contrato de politica/gate v2 exclusivo de servidor, sin habilitar.
- [x] M3-T1 §83: politica pura y composicion v2 con contratos cerrados, identidad de evento/politica y 104 pruebas nuevas; v1 conservado.
- [x] M3-T1 §84: identidad de politica nullable en eventos, migracion c62e407bad31, contratos/mapper y 35 pruebas nuevas; historicos/RLS conservados.
- [x] M3-T1 §85: resolver fijo deshabilitado y readiness v2/identidad; una consulta de historial y 26 pruebas nuevas, gates v1 conservados.
- [x] M3-T1 §86: prerequisitos puros de revision v2, negativos parciales y positivos con composicion/politica; 110 pruebas nuevas y suite completa 3299 passed.
- [x] M3-T1 §87: revision autenticada v2 bajo lock con politica deshabilitada/metadatos de servidor; diez HTTP nuevos y suite completa 3309 passed.
- [x] M3-T1 §88: decision transversal/confirmacion v2 bajo lock, alcance ordinario conservado; once HTTP nuevos, concurrencia ampliada y suite completa 3320 passed.
- [x] M3-T1 §89: contrato de publicacion inmutable/selector auditado, orden de locks, revocacion y evidencia atomica de confirmacion; solo diseno.
- [x] M3-T1 §90: contratos/evaluadores puros de publicacion/seleccion/evidencia, coherencia/hash y 65 pruebas nuevas; suite completa 3385 passed.
- [x] M3-T1 §91: persistencia de control global, migracion d73f518cbe42, privilegios/RLS y consistencia diferida; 44 PostgreSQL nuevas y suite completa 3429 passed.
- [x] M3-T1 §92: evidencia append-only tenant, migracion e84a629dcf53, FK/RLS y 29 PostgreSQL nuevas; suite completa 3458 passed.
- [x] M3-T1 §93: servicios internos de publicacion/seleccion deshabilitada y lectura validada, bootstrap/seleccion concurrentes; 24 PostgreSQL nuevas y suite completa 3482 passed.
- [x] M3-T1 §94: resolver transaccional/bloqueo compartido limitado, migracion f95b73aed064; 15 PostgreSQL nuevas y suite completa 3497 passed.
- [x] M3-T1 §95: revision humana con selector auditado deshabilitado, identidad real y nueve PostgreSQL nuevas (cuatro concurrencias); Suite completa: 3506 passed en 313.64 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §96: readiness/confirmacion con selector auditado y orden compatible, ordinario sin selector conservado; 13 PostgreSQL nuevas; Suite completa: 3519 passed en 329.62 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §97: evidencia atomica conectada antes de reemplazo, guardia productiva conservada y 12 PostgreSQL nuevas de exitos sinteticos/fallos; Suite completa: 3531 passed en 334.47 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §98: confirmaciones exitosas concurrentes y revocacion conservan evidencia; 12 PostgreSQL nuevas; Suite completa: 3543 passed en 343.50 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §99: exitos independientes/aislamiento y PATCH concurrente; 12 PostgreSQL nuevas; Suite completa: 3555 passed en 345.51 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §100: contrato de autoridad personal (JWT/superadmin/canal separado), precondicion de proteger perfiles y matriz; solo documentacion.
- [x] M3-T1 §101: auditoria efectiva local y proteccion de identidad/autoridad de perfiles, migracion a06c84bf175e; 12 PostgreSQL nuevas; Suite completa: 3567 passed en 431.30 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §102: barrera personal limitada perfil/rol/lock, migracion b17d95c0286f y nueve PostgreSQL nuevas; 45 focalizadas aprobadas, sin conexion a escritores.
- [x] M3-T1 §103: escritores personales con actor derivado y 11 PostgreSQL nuevas; 44 focalizadas aprobadas; Suite completa: 3587 passed en 348.04 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §104: pool separado y dependencia JWT/sub local/autoridad, 17 pruebas nuevas; 47 focalizadas aprobadas. Suite completa: 3604 passed en 352.09 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §105: endpoints administrativos con JWT verificado/pool real, 38 HTTP nuevas; 85 focalizadas aprobadas. Suite completa: 3642 passed en 355.96 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §106: doce HTTP concurrentes (revocacion/rollback/cancelacion/seleccion/unicidad); 97 focalizadas aprobadas. Suite completa: 3654 passed en 369.30 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §107: revalidacion documental de fuentes base/busqueda complementaria y matriz de trazabilidad a commits; sin cambio de gates ni nueva suite.
- [x] M3-T1 §108: procedimiento de provision deshabilitada preparado, JSON de ejemplo validado; sin provision real ni cambios de gates.
- [x] M3-T1 §109: preflight readonly limitado y seis pruebas nuevas; 23 focalizadas aprobadas, sin escrituras/provision operativa.
- [x] M3-T1 §110: permisos efectivos de grupo/login/public/RLS en preflight e informe v1; ocho nuevas, 31 focalizadas aprobadas.
- [x] M3-T1 §111: expediente inicial con configuracion ausente/preflight failed esperado y head local comprobados; sin provision real.
- [x] M3-T1 §112: usuario selecciona local; inspeccion readonly y accion de provision concreta preparada, sin ejecutar tras rechazo automatico.
- [x] M3-T1 §113: provision tecnica local explicitamente autorizada, login limitado/credencial privada; preflight pending_selector (2), sin bootstrap.
- [x] M3-T1 §115: superadmin global local explicitamente autorizado y confirmado en perfil existente; sin cambios Supabase/politicas.
- [x] M3-T1 §116: UID aportado contrastado con perfil local autorizado; backend/rutas registrados, rechazo anonimo 401 probado.
- [x] M3-T1 §117: proceso local separado con secreto en memoria, health/401 y Supabase/JWKS 200; vinculo staff externo verificado por consulta admin.
- [ ] M3-T1: sesion/JWT personal real y humo autenticado, publicacion/seleccion deshabilitada y validacion/retirada operativas; fuentes/aceptacion pendientes.

## M3-T1 §118 — acceso personal local (2026-10-09)

- [x] Endpoint administrativo de lectura y pantalla local de comprobacion; 40 pruebas API y checks frontend aprobados.
- [x] Comprobar acceso con sesion personal real: resultado confirmado en captura aportada por el usuario (2026-10-09).
- [ ] Validar publicacion/seleccion de politica deshabilitada y auditoria con sesion personal.
- [ ] Completar fuentes complementarias, aceptacion y validacion operacional integral; activacion excepcional bloqueada.

## M3-T1 §119 — registro operacional

- [x] Consulta administrativa autenticada del snapshot validado y pantalla de revision; 54 pruebas focalizadas aprobadas.
- [x] Consulta con sesion personal confirmada por captura: revision 0, publicaciones 0, selecciones 0 (2026-10-09).
- [ ] Preparar publicacion deshabilitada y comprobar persistencia/auditoria; luego seleccionar con revision vigente.

## M3-T1 §120 — publicacion local deshabilitada

- [x] Propuesta fija autenticada, vista revisable y publicacion explicita con comprobacion posterior; 56 pruebas focalizadas aprobadas.
- [x] Publicacion con sesion personal confirmada por captura: 1 publicacion deshabilitada, 0 selecciones, revision 0 (2026-10-09).
- [ ] Preparar seleccion explicita con revision vigente y verificar evento/selector en la auditoria.

## M3-T1 §121 — seleccion deshabilitada

- [x] Preparar seleccion con revision vigente y comprobar evento/hash/selector; checks frontend y 56 pruebas API aisladas aprobadas.
- [x] Seleccion personal confirmada por capturas y snapshot tecnico readonly coherente: revision 1, 1 publicacion y 1 seleccion deshabilitada (2026-10-09).
- [ ] Revisar cierre operacional y pendientes de provision/rotacion/retiro y aceptacion integral; activacion bloqueada.

## M3-T1 §122 — cierre delimitado de validacion local

- [x] Consolidar secuencia personal deshabilitada, coherencia persistida y preflight posterior ok; head verificado.
- [x] Separar pendientes operacionales y juridicos en docs/project/m3-t1-eipd-cierre-validacion-local.md.
- [x] Preparar ejecutor focalizado que exige base aislada antes de pytest: §123, 60 pruebas aprobadas. Pytest directo no queda protegido por el wrapper.
- [ ] Validar rotacion/retiro y recuperacion, fuentes/aceptacion y alcance integral; M3-T1 EN PROGRESO.

## M3-T1 §123 — pruebas aisladas

- [x] Ejecutar suite focalizada mediante guardas de destino/head/roles/estado, con 60 aprobadas.
- [x] Ejecutar ensayo aislado de rotacion/retiro y recuperacion §124: 63 pruebas aprobadas; snapshot de pruebas sin cambios.
- [ ] Validar ciclo de vida del canal provisionado con historial real y renovacion segura de procesos; no ejecutado en §124.

## M3-T1 §125 — rotacion real preparada

- [x] Verificar canal/destino/head y preparar drenaje, reemplazo privado, recuperacion y comprobacion posterior.
- [x] Rotacion real local ejecutada §126: credencial anterior rechazada en conexion nueva; nuevo canal ok y snapshot completo intacto.
- [x] Acceso personal tras reinicio confirmado por captura y copia privada anterior retirada (§126).

## M3-T1 §127 — retiro reversible real

- [x] Drenar canal real, comprobar NOLOGIN con conexion nueva, restaurar LOGIN y verificar snapshot completo intacto/revision 1.
- [x] Acceso personal tras reinicio de recuperacion confirmado por captura §127. Retiro definitivo no ejecutado.

## M3-T1 §128 — investigacion documental

- [x] Delimitar primer incremento de investigacion con datos no sensibles/adultos y LIA, completitud/aplicabilidad y fuente primaria.
- [x] Implementar schema/evaluador puro §129; sin persistencia ni gates, can_confirm=false.
- [x] Ampliar aplicabilidad/limites §130: 20 casos nuevos; suite aislada 107 aprobadas.
- [x] Implementar binding independiente de investigacion y chequeo de obsolescencia §131; 119 pruebas aisladas aprobadas. Historicos intactos, sin conversion automatica.
- [x] Delimitar persistencia/API §132 en docs/project/m3-t1-investigacion-integracion.md.
- [x] Schema/modelo/migracion nullable sin backfill §133; 121 pruebas aisladas, upgrade/check en ambas bases y auditoria EIPD intacta.
- [x] Integrar servicios/API create/GET/PATCH con binding de servidor y pruebas de acceso §134; nuevas asociaciones especiales/EIPD pendientes.

### M3-T1 §134 — API del expediente de investigacion

- [x] Create/GET/PATCH con binding de servidor y omision/null/reaporte; contratos cliente cerrados.
- [x] 127 pruebas focalizadas aprobadas y 174 HTTP existentes de compatibilidad aprobadas; estados historicos protegidos.
- [x] Readiness documental/asociacion de investigacion §135. Confirmacion sigue bloqueada; M3-T1 EN PROGRESO.
- [ ] Nuevas versiones especiales/EIPD que cubran investigacion y aceptacion revisada antes de habilitar el gate.

### M3-T1 §135 — Readiness de investigacion

- [x] Completitud, aplicabilidad y asociacion vigentes/obsoletas expuestas sin escrituras; bloqueo compartido de confirmacion incluso con expediente completo.
- [x] 303 pruebas ampliadas aisladas aprobadas; Black/Ruff aprobados.
- [ ] Nuevas versiones de binding especial/EIPD e integracion posterior; M3-T1 EN PROGRESO y activacion bloqueada.

### M3-T1 §136 — Asociaciones para investigacion

- [x] Delimitar versiones sucesoras especiales V11/EIPD V12, material, compatibilidad y orden PATCH.
- [x] Implementar contratos/funciones puras nuevos con pruebas de hashes historicos intactos §137; 145 focalizadas aprobadas.
- [ ] Dispatch y servicio/API, luego contexto de resolucion/revision y aceptacion. Confirmacion investigacion/EIPD bloqueadas.

### M3-T1 §137 — Asociaciones puras sucesoras

- [x] Contratos cerrados especiales V11/EIPD V12 y hash/bind de expediente completo sin reparar bindings research.
- [x] 16 casos nuevos y 145 focalizados aprobados; funciones historicas verificadas intactas, Black/Ruff aprobados.
- [x] Dispatch evaluador y falta de cobertura historica §138; escritura API pendiente. Gates siguen bloqueados.

### M3-T1 §138 — Evaluacion versionada de investigacion

- [x] Dispatch especiales V11/screening V12 y falta de cobertura independiente para versiones anteriores con investigacion.
- [x] 8 casos nuevos; suite ampliada aislada 327 aprobadas, Black/Ruff aprobados.
- [x] Generacion API de asociaciones sucesoras y pruebas de orden PATCH §139. Confirmacion investigacion/EIPD bloqueadas.

### M3-T1 §139 — API de asociaciones sucesoras

- [x] Create/PATCH especiales V11/screening V12 con valores finales y conservacion de asociaciones omitidas.
- [x] Dos casos HTTP nuevos; 329 ampliadas y 162 regresiones frontera/screening V2 aprobadas.
- [ ] Revisar cobertura versionada del contexto de resolucion/revision EIPD de investigacion; gates bloqueados.

### M3-T1 §140 — Resolucion/revision EIPD de investigacion

- [x] Revisar cobertura V1 y delimitar contratos V2, compatibilidad historica y frontera de revision/eventos.
- [ ] Implementar contexto/binding/Stored V2 y funciones puras con pruebas V1 intactas.
- [ ] Dispatch, frontera/composicion, metadatos de eventos y escritura API posteriores; gates bloqueados.
