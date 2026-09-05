# Estado actual del proyecto

## Snapshot Git observado

| Elemento | Valor observado |
|---|---|
| Repositorio de trabajo | `P_CumpleIA` |
| Rama checkout | `fix/modulo1-tarea6-backlog-y-tests-onupdate` |
| HEAD | `fcf5315` |
| `main` local | `4cedff1` |
| `origin/main` en el snapshot | `4cedff1` |
| Archivos trackeados | 142 |
| Migraciones Alembic | 9 |
| Archivos de tests backend | 16 |
| Python trackeado | 64 archivos |
| TSX trackeado | 20 archivos |
| TS trackeado | 7 archivos |

La rama actual contiene tres archivos modificados respecto de `main`: dos archivos de tests y `docs/backlog.md`.

## Inconsistencia a verificar en GitHub

El documento fechado **10-08-2026** afirma que el PR #20 quedó mergeado a `main`. Sin embargo, los refs Git incluidos en el ZIP muestran:

- `main` / `origin/main`: `4cedff1` - PR #19.
- rama `fix/modulo1-tarea6-backlog-y-tests-onupdate`: `fcf5315`.

Esto puede significar que el PR #20 fue mergeado después del último `fetch`, o que el documento anticipó el merge. No debe resolverse por memoria: al retomar, hacer `git fetch` y verificar el estado real remoto.

## Estado funcional por fases

### Fase 0 - Cimientos

**Completada según código y notas históricas.** Incluye:

- monorepo frontend/backend;
- autenticación con Supabase;
- aprovisionamiento JIT de perfiles;
- organizaciones y membresías;
- aislamiento multi-tenant con PostgreSQL RLS;
- rol runtime `app_user` sin `BYPASSRLS`;
- CI backend/frontend;
- RAG con pgvector;
- ingesta de fuentes legales;
- abstracción de proveedor LLM y embeddings.

### Fase 1 - Módulo 1 Autodiagnóstico

**Construido en el código del snapshot.** Incluye:

- catálogo versionado del cuestionario;
- 10 secciones y 50 preguntas según el seed vigente;
- panel superadmin para pesos y riesgo por pregunta;
- scoring determinista;
- hallazgos por riesgo;
- API de diagnóstico;
- narrativa de informe con IA y guardarraíles;
- RAG limitado a Ley 21.719 + guía CCS para el informe;
- exportación HTML;
- wizard frontend;
- dashboard de puntajes y hallazgos;
- generación/regeneración del informe;
- descarga del informe HTML;
- edición de datos de organización.

## Verificación de tests

No se ejecutó la suite completa durante esta revisión porque el entorno de análisis no tenía instalada la dependencia `pgvector`; `compileall` sí pasó para `app`, `scripts` y `tests`.

La nota del 10-08-2026 reporta **129/129 tests** como criterio esperado. El árbol fuente contiene 123 funciones de test directas; la diferencia puede corresponder a parametrizaciones. Antes de desarrollar, debe ejecutarse la suite real en el entorno del proyecto.

## Estado de la base de conocimiento RAG

La nota del 30-07-2026 reporta 198 chunks con embedding:

- `guia_ccs`: 76
- `ley_19628`: 31
- `ley_21719`: 91

Ese dato es **histórico**, no una consulta al Postgres actual. Debe verificarse en la base al retomar si es importante para la siguiente tarea.

## Checkpoint de entorno local - 31-08-2026

Se reconstruyó y validó el entorno local de desarrollo de CumpleIA en el nuevo equipo HP OMEN, utilizando WSL2 con Ubuntu 24.04 y Docker Desktop con integración WSL.

Estado verificado:

- repositorio en rama `main`, sincronizado con `origin/main` y working tree limpio antes de registrar este checkpoint;
- PostgreSQL 16 + pgvector operativo mediante Docker;
- migraciones Alembic aplicadas correctamente hasta `d2e3f4a5b6c7`;
- rol runtime `app_user` operativo, sin privilegios `SUPERUSER` ni `BYPASSRLS`;
- autenticación de `app_user` contra PostgreSQL validada desde el entorno Python local;
- políticas RLS verificadas en las tablas multi-tenant;
- seed del Módulo 1 ejecutado correctamente:
  - 8 obligaciones;
  - 10 secciones;
  - 50 preguntas;
  - configuración versión 1 activa;
- backend levantado correctamente y endpoint `/health` con estado `ok`;
- suite completa de backend ejecutada en el entorno local:
  - **129 tests collected**;
  - **129 passed**;
  - **0 failed**;
  - tiempo observado: **10.75 s**.

Este checkpoint reemplaza, para efectos del entorno local actual, la observación anterior de este documento que indicaba que la suite completa no había podido ejecutarse.

**Estado:** baseline local estable y validado para continuar el desarrollo y las pruebas.

**F1.16 — Sandbox Runtime:** completada y validada con resultado **PASS**.

La política SRT pre-final quedó documentada en:

`docs/benchmark/F1.16_SRT_validacion_2026-08-31.md`

La validación confirmó, entre otros controles, aislamiento de red, bloqueo de localhost y sockets Unix, protección de rutas sensibles y de `.git/config`, ejecución de Claude Code dentro de SRT y aislamiento de su configuración runtime.

**Próximo paso:** continuar con la etapa siguiente del Benchmark RAT posterior a F1.16.

**F1.17 — Managed Settings de Claude Code:** completada y validada con resultado **PASS**.

La política administrada quedó documentada en:

`docs/benchmark/F1.17_Managed_Settings_validacion_2026-08-31.md`

La configuración versionada utilizada por el benchmark se encuentra en:

`docs/benchmark/runner/managed-settings.json`

SHA-256 de referencia:

`f51e229df07d539fc1367654110ba028c64261f577e7477dae115049b66f2a0f`

La validación confirmó carga efectiva como `Enterprise managed settings (file)`, modo `dontAsk`, bloqueo de WebFetch y WebSearch, neutralización de bypass de permisos y bloqueo de sideload de MCP, custom agents y plugins.

**Próximo paso:** continuar con **F1.18 — transporte y backend de modelo**, revisando el diseño original del benchmark para incorporar de forma controlada tanto modelos remotos como una eventual LLM local en el HP OMEN.

**F1.18A — Contrato común de transporte:** implementada documentalmente; la validación de backends permanece pendiente.

El contrato neutral para candidatos cloud y local quedó documentado en:

`docs/benchmark/F1.18A_Contrato_comun_transporte_2026-09-01.md`

Sus archivos de configuración de referencia son:

- `docs/benchmark/runner/transport-contract.schema.json`;
- `docs/benchmark/runner/candidate-transport.example.json`.

El contrato fija nombre lógico, clase de backend, proveedor, endpoint, model ID, referencia de credencial y timeout. Las credenciales no se versionan: solo se declara el nombre de su variable de entorno, o `null` cuando el backend no requiere autenticación.

Python **3.12.3** permanece como baseline común. F1.18A no instala Ollama/Qwen, no selecciona modelos definitivos y no modifica la política SRT, la allowlist de red ni los managed settings de F1.17.

**Próximo paso:** continuar con **F1.18B — validación de transporte cloud** y posteriormente F1.18C para el transporte local controlado.

**F1.18B — Transporte cloud Anthropic:** completada y validada con resultado **PASS**.

La validación quedó documentada en:

`docs/benchmark/F1.18B_Transporte_cloud_Anthropic_validacion_2026-09-01.md`

Se confirmó una inferencia real de Claude Code hacia Anthropic dentro de SRT, manteniendo accesibles únicamente los dominios Anthropic previamente autorizados. El acceso a Internet general permaneció bloqueado mediante allowlist.

No fue necesario modificar la política SRT ni Managed Settings y no se incorporaron componentes de transporte local.

**Próximo paso:** validar el siguiente backend cloud del Benchmark RAT, verificando previamente endpoint, model ID, autenticación y allowlist mínima. La arquitectura de transporte local se abordará posteriormente como una etapa separada.
**F1.18C — Transporte cloud DeepSeek:** completada y validada con resultado **PASS**.

La validación quedó documentada en:

`docs/benchmark/F1.18C_Transporte_cloud_DeepSeek_validacion_2026-09-01.md`

Se validó DeepSeek como segundo backend cloud mediante tres niveles independientes: API nativa, interfaz Anthropic-compatible mediante SDK y ejecución real de Claude Code dentro de SRT utilizando DeepSeek como backend.

La política SRT fue ampliada exclusivamente con `api.deepseek.com`. Internet general permaneció bloqueado y no se habilitaron Unix sockets ni local binding.
Durante la ejecución con Claude Code 2.1.252 se observaron advertencias `unrecognized_model` asociadas a los identificadores DeepSeek utilizados por llamadas internas de Claude Code. Estas advertencias quedaron documentadas como una limitación de compatibilidad a vigilar, pero no impidieron completar correctamente la inferencia solicitada.

Las credenciales permanecen fuera del repositorio y al finalizar las pruebas no quedaron variables de autenticación persistentes en el entorno.

**Próximo paso:** definir y validar la arquitectura de transporte para un backend LLM local antes de instalar Ollama u otro runtime o descargar un modelo. El diseño deberá permitir la comunicación controlada desde SRT sin habilitar localhost, local binding o Unix sockets de forma general.
### F1.18D-A — Arquitectura de transporte local seguro

- Estado: PASS arquitectónico.
- Se descartó el diseño basado en Unix Domain Socket selectivo bajo SRT/Linux.
- No se habilitó `allowAllUnixSockets`.
- Se validó transporte local mediante hostname dedicado y proxy/allowlist SRT.
- `llm-local.cumpleia` autorizado alcanza un servicio loopback local.
- Acceso directo a `127.0.0.1` desde SRT continúa bloqueado.
- Un hostname alternativo no autorizado hacia el mismo servicio devuelve HTTP 403.
- `allowUnixSockets` permanece vacío.
- `allowLocalBinding` permanece en false.
- No se instalaron todavía llama.cpp, Ollama ni modelos locales.
- Próximo paso: validar el transporte con un runtime LLM real y posteriormente F1.18D-B para Claude Code.
### F1.18D-A2 — Validación del transporte con runtime LLM real

- Estado: **PASS**.
- Se instaló CUDA Toolkit 13.1 dentro de WSL, sin instalar drivers NVIDIA Linux.
- Se compiló `llama.cpp` tag `b10516`, commit `b95502b`, con `GGML_CUDA=ON` y arquitectura CUDA `120`.
- Se validó `llama-server` utilizando la NVIDIA GeForce RTX 5060 Laptop GPU.
- Modelo de validación: `Qwen3.5-0.8B-Q4_0.gguf`.
- El modelo se almacena físicamente en `D:\CumpleIA-LLM\models` y se accede desde el runtime mediante `~/runtime/local-llm/models`.
- Se endureció el transporte asignando `llm-local.cumpleia` al loopback dedicado `127.77.18.1`.
- `llama-server` escucha exclusivamente en `127.77.18.1:18080`.
- Se confirmó inferencia real fuera de SRT con resultado `F1.18D-A2-LOCAL-OK`.
- Se confirmó inferencia real dentro de SRT con resultado `F1.18D-A2-SRT-OK`.
- El acceso directo desde SRT a `127.0.0.1:18080` permanece bloqueado (`HTTP=000`).
- `nvidia-smi` confirmó `/llama-server` como proceso CUDA y aproximadamente 829 MiB de VRAM asignada durante la validación.
- No se detectaron listeners locales wildcard en `0.0.0.0` ni `[::]`.
- Se comprobó que `allowedDomains` de SRT controla hostname pero no puerto; por ello la ausencia de listeners wildcard pasa a ser un invariante de seguridad del benchmark.
- La evidencia completa quedó registrada en `docs/benchmark/F1.18D-A2_Validacion_runtime_LLM_local_2026-09-02.md`.

### F1.18D-B — Integración Claude Code con LLM local — PASS

- Se confirmó que `llama-server` expone un endpoint Anthropic-compatible `/v1/messages`.
- La primera integración con Claude Code falló por incompatibilidad del chat template original de Qwen3.5 (`System message must be at the beginning`).
- Se resolvió utilizando `--chat-template chatml`, sin introducir proxy o adaptador adicional.
- La ventana inicial de 4096 tokens fue insuficiente para Claude Code; se amplió a `16384`.
- Claude Code ejecutado fuera de SRT devolvió correctamente `F1.18D-B-CLAUDE-LOCAL-OK`.
- Dentro de SRT fue necesario redirigir `TMPDIR` a `/home/cumplebench/runtime/tmp`, evitando habilitar escritura general en `/tmp`.
- Claude Code ejecutado dentro de SRT devolvió correctamente `F1.18D-B-SRT-LOCAL-OK`.
- Se confirmó nuevamente que el acceso directo desde SRT a `127.0.0.1:18080` permanece bloqueado (`HTTP=000`).
- El identificador lógico `local` continúa generando el aviso no fatal `unrecognized_model`; para esta validación se utilizó temporalmente `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1`.
- El modelo `Qwen3.5-0.8B-Q4_0.gguf` se mantiene como modelo de validación de transporte, no como candidato definitivo para generación de código.
- La evidencia completa quedó registrada en `docs/benchmark/F1.18D-B_Integracion_Claude_Code_LLM_local_2026-09-02.md`.

**Próximo paso:** iniciar **F1.19 — harness reproducible y confiable**, encargado de preparar/resetear el workspace y ejecutar fuera del sandbox del agente las verificaciones de confianza del benchmark.

### F1.19B — Workspace reproducible y aislamiento — PASS

- El workspace se materializa como clon Git independiente, sin hardlinks,
  alternates ni remotes, en detached HEAD del baseline exacto.
- La política SRT por corrida permite escritura solo en el workspace y runtime
  correspondientes; repositorio canónico y evidencia trusted quedan fuera.
- El preflight rechaza colisiones de workspace/runtime/evidencia y opera
  fail-closed.
- F1.19C reutilizó el mecanismo en una corrida integral y la regresión pasó.

### F1.19C — Reset de estado y verifier trusted `rat-default` — PASS

- PostgreSQL `pgvector/pg16` efímero sobre la red Docker internal
  `cumpleia-benchmark-net`.
- Runner mínimo con Python 3.12.3, filesystem read-only, sin Docker socket y
  workspace candidato montado read-only durante Alembic.
- Loader trusted del fixture Módulo 1 protegido por SHA-256, con IDs
  deterministas, 8 obligaciones, 10 secciones, 50 preguntas, v1 activa, 10
  pesos que suman 100 y 50 riesgos válidos.
- Tenants A/B, memberships y diagnósticos centinela deterministas.
- Verifier trusted de contenido, configuración, privilegios y aislamiento RLS.
- Generación fail-closed de `verification.json` y `tests.log` fuera del
  workspace, modo `0600`.
- Corrida integral `f119c-validation2-20260904`: PASS en los seis grupos de
  checks; PostgreSQL efímero eliminado al finalizar.

Documentación: `docs/benchmark/F1.19C_Reset_estado_verificacion_trusted_2026-09-04.md`.

**Próximo paso:** integrar la ejecución candidata y el perfil `rat-default` en
el ciclo completo que genera `result.json` y `manifest.sha256`.

### F1.19D — Ciclo completo, resultado y manifest — PASS

- `run-config` incorpora `taskFile`; tarea efectiva y hashes quedan preservados
  en evidencia.
- Preflight estricto de run, transport, baseline, tarea, perfil, timeout,
  credencial declarada y managed settings efectivos.
- Claude Code 2.1.252 se ejecuta dentro de SRT con entorno mínimo, runtime por
  corrida, timeout de grupo de procesos y sin acceso de lectura/escritura al
  repositorio canónico ni a evidencia trusted.
- Logs concurrentes limitados a 16 MiB, con redacción de la credencial efectiva
  antes de persistir y permisos `0600`.
- Estado final derivado únicamente por el harness: `PASS`, `FAIL`, `TIMEOUT` o
  `HARNESS_ERROR`.
- `result.json` autoritativo y `manifest.sha256` ordenado sobre toda la evidencia.
- Validaciones: ciclo controlado PASS, ejecutable externo bloqueado/FAIL,
  timeout real/TIMEOUT, manifest íntegro y 8 tests unitarios PASS.

Documentación:
`docs/benchmark/F1.19D_Ciclo_completo_resultado_manifest_2026-09-04.md`.

**Próximo paso:** F1.19E — retención/limpieza segura, validación de evidencia
cerrada y procedimiento operativo para rondas comparables entre candidatos.

### F1.19E — Retención, limpieza y cierre de evidencia — PASS

- Política versionada: workspace/runtime se eliminan solo después del cierre;
  evidencia se conserva y su borrado no está soportado.
- Validador independiente de cobertura y hashes del manifest, estructura JSON,
  coherencia cruzada, estados, tiempos, baseline, tarea y política SRT.
- Snapshot de managed settings incorporado a la evidencia.
- Cierre automático `0500` para el directorio y `0400` para sus archivos.
- Cualquier inconsistencia de cierre degrada el resultado a `HARNESS_ERROR`.
- Limpieza con dry-run por defecto y `--execute` explícito; objetivos derivados
  únicamente del runId bajo las raíces efímeras conocidas.
- Validación real: TIMEOUT coherente, evidencia PASS antes y después de limpiar,
  workspace/runtime eliminados y evidencia retenida.
- Suite trusted: 11 passed.

Documentación:
`docs/benchmark/F1.19E_Retencion_limpieza_evidencia_2026-09-04.md`.

**Próximo paso:** definir y ejecutar la primera ronda benchmark real con tarea,
candidatos, baseline y presupuesto comparables.

### F1.20A — Preflight de la primera ronda — PASS técnico

- Las imágenes Python 3.12.3 y pgvector/pg16 quedaron fijadas por digest.
- Los contenedores del runner eliminan todas las capacidades y aplican
  `no-new-privileges`, límite de 128 procesos y 256 MiB de memoria.
- La integración directa `f119f-hardening-20260904` repitió los seis grupos
  trusted con PASS y sin PostgreSQL residual.
- El ciclo completo `f119f-full-hardening-20260904` produjo TIMEOUT controlado,
  checks trusted PASS, evidencia cerrada/validada y limpieza efectiva.
- Dos pruebas de regresión cubren el pinning de imágenes y los argumentos de
  seguridad; la suite trusted completa terminó con 13 passed.
- Se estableció un gate funcional: `rat-default` valida infraestructura y
  baseline, pero no puede puntuar por sí solo una tarea nueva porque una
  solución vacía también puede superarlo.

Documentación:
`docs/benchmark/F1.20A_Preflight_primera_ronda_2026-09-04.md`.

**Próximo paso:** confirmar tarea y candidatos definitivos; después construir
el task file y verifier trusted específicos antes de consumir presupuesto de
modelos.

### F1.20B — Tarea y verifier N/A por sección — PASS

- La primera tarea funcional quedó fijada en
  `docs/benchmark/runner/tasks/na-section-v1.md`.
- El contrato exige conteos API `respondidas`/`no_aplica`, representación en
  dashboard y HTML, fórmula intacta, tests y alcance acotado.
- El perfil `rat-na-section-v1` encadena los seis checks de `rat-default` con
  cuatro pruebas funcionales aisladas y una validación trusted del diff.
- El código candidato se prueba sin red, secretos ni DB, en workspace
  read-only y con los límites de seguridad del runner.
- Validación negativa: el baseline intacto fue rechazado mientras los seis
  checks de infraestructura permanecieron en PASS.
- Validación positiva: una solución dorada temporal obtuvo 4 passed y superó
  el control de alcance; luego fue eliminada.
- Suite trusted: Ruff PASS, Black PASS, 15 passed y 1 skipped contextual.

Documentación:
`docs/benchmark/F1.20B_Tarea_y_verifier_NA_por_seccion_2026-09-04.md`.

**Próximo paso:** fijar este checkpoint como baseline y decidir candidatos,
timeout y presupuesto de la primera ronda.

### F1.20D — Cierre de la primera ronda RAT — CERRADA

- Tarea: `rat-na-section-v1` sobre el baseline común
  `f7d8eb223b8adbb97d7a042a24f7c9297447e99c`.
- Claude Sonnet 5: **FAIL**, 3/4 tests, 308.498130 s; faltó la
  representación explícita requerida de ambos conteos en dashboard.
- DeepSeek V4 Pro: **PASS**, 4/4 tests, 532.326318 s.
- Qwen3-4B local: **FAIL**, 1/4 tests, 60.880742 s; implementación incompleta
  en API, exportación HTML y contrato TypeScript/dashboard.
- Las tres evidencias y sus manifests pasaron el validador independiente
  trusted sin repetir corridas ni modificar evidencia o workspaces.
- Baseline, tarea, configuración y verifier de la ronda permanecen preservados.
- Una sola tarea no permite inferir un ranking general entre modelos.

Documentación:
`docs/benchmark/F1.20D_Cierre_primera_ronda_RAT_2026-09-04.md`.

**Próximo paso:** diseñar una segunda tarea representativa y fijar su verifier
trusted antes de ejecutar nuevos candidatos.

### F1.21A — Diseño de segunda tarea funcional — PASS

- Se fijó la tarea `organization-current-v1`: implementar
  `GET /organizations/current` con selección por `X-Organization-Id`, permiso
  `view_content`, lectura permitida a `viewer` miembro y rechazo de cruce
  entre tenants.
- El baseline actual no expone esa ruta, por lo que la validación negativa no
  dependerá de introducir una vulnerabilidad artificial.
- Aún no se ejecutaron candidatos ni se eligió/descargó un modelo local nuevo.
- F1.21B completó el perfil trusted y validó baseline negativo y solución
  dorada temporal.

Documentación:
`docs/benchmark/F1.21A_Diseno_segunda_tarea_organizacion_actual_2026-09-04.md`.

### F1.21B — Verifier trusted de organización actual — PASS

- Perfil `rat-organization-current-v1` encadenado a `rat-default`.
- Contenedor sin red, credenciales ni acceso de escritura al workspace.
- Contrato: 4/4 PASS con solución dorada temporal; 4/4 FAIL con baseline
  intacto, resultado esperado.
- Suite del harness: 17 passed, 2 skipped.
- La solución dorada y sus copias temporales fueron eliminadas tras validar.
- No se ejecutaron candidatos ni se modificaron evidencias existentes.

Documentación:
`docs/benchmark/F1.21B_Verifier_organizacion_actual_2026-09-04.md`.

**Próximo paso:** F1.21C — fijar commit baseline, hashes, candidatos, timeout
y presupuesto antes de ejecutar la segunda ronda.

### F1.21C — Configuración de segunda ronda RAT — PASS técnico

- Baseline: `4b3b4b74d71a312096b9329c6e80f5a31c40f03d`.
- Perfil: `rat-organization-current-v1`; tarea y hashes del verifier fijados.
- Candidatos comparables: Claude Sonnet 5, DeepSeek V4 Pro y Qwen3-4B local.
- Una ejecución por candidato, timeout común de 1.800 segundos y sin reintentos.
- No se incorpora aún un modelo local mayor: la RTX 5060 Laptop tiene 8 GiB
  de VRAM y Qwen3-8B ya resultó operacionalmente inviable en este transporte.
- Seis configuraciones validadas, preflight local PASS y suite trusted:
  21 passed, 2 skipped.

Documentación:
`docs/benchmark/F1.21C_Configuracion_segunda_ronda_RAT_2026-09-04.md`.

**Próximo paso:** autorizar explícitamente una ejecución autoritativa por cada
candidato de la segunda ronda.

### F1.21D — Reparación de sockets puente SRT — PASS

- Las corridas Qwen/Claude de segunda ronda no alcanzaron a ejecutar agentes:
  ambas reportaron fallo de creación de bridge sockets.
- Causa identificada: el `TMPDIR` por `runId` dejaba insuficiente margen bajo
  el límite Unix de 108 bytes para `cc-socks`.
- El harness ahora deriva un TMPDIR corto con hash, lo limita en SRT y lo
  elimina mediante limpieza trusted.
- Suite tras el cambio: 22 passed, 2 skipped; Ruff y Black PASS.
- Sonda aislada con TMPDIR corto y transporte local: PASS (`OK`), sin bridge
  socket error; sus directorios temporales fueron eliminados.

Documentación:
`docs/benchmark/F1.21D_Reparacion_sockets_SRT_2026-09-04.md`.

### F1.21E — Cierre de la segunda ronda RAT — CERRADA

- Tarea: `organization-current-v1` sobre baseline
  `4b3b4b74d71a312096b9329c6e80f5a31c40f03d`.
- Claude Sonnet 5: **PASS**, 4/4 tests, 261.639231 s.
- Qwen3-4B local: **FAIL**, 0/4 tests, 106.626028 s; no expuso la ruta y
  modificó un activo protegido de migración.
- DeepSeek V4 Pro: **FAIL**, 0/4 tests, 201.262959 s; no expuso la ruta ni
  agregó o modificó pruebas backend.
- Las tres evidencias efectivas y sus manifests pasaron el validador trusted.
- Los intentos previos cerrados por infraestructura o credencial permanecen
  preservados y no se usan como resultados comparables.
- Dos tareas aún no permiten inferir un ranking general entre modelos.

Documentación:
`docs/benchmark/F1.21E_Cierre_segunda_ronda_RAT_2026-09-04.md`.

**Próximo paso:** diseñar y validar una tercera tarea funcional independiente
antes de concluir rankings o reemplazar candidatos.

### F1.22A — Diseño de tercera tarea funcional: selector de organización activa — PASS

- Tarea `active-organization-selector-v1`: resolver la selección explícita de
  tenant en las pantallas de organización y autodiagnóstico para usuarios con
  múltiples membresías.
- El contexto activo viaja en el parámetro URL `organization`, se valida contra
  la lista obtenida por el servidor y nunca se reenvía un UUID ajeno al backend.
- Alcance independiente de F1.20/F1.21: Next.js, TypeScript, UI accesible y
  propagación de contexto existente; no cambia backend, RLS ni migraciones.
- F1.22B deberá probar baseline negativo, selector accesible, propagación del
  UUID válido y fallback seguro ante UUID ajeno.

Documentación:
`docs/benchmark/F1.22A_Diseno_tercera_tarea_selector_organizacion_2026-09-04.md`.

**Próximo paso:** F1.22B — implementar y validar el verifier trusted de la
tercera tarea antes de fijar candidatos.

### F1.22B — Verifier trusted de selector de organización activa — PASS

- Perfil `rat-active-organization-selector-v1` aislado y encadenado a
  `rat-default`.
- Baseline: 4 fallos esperados; solución dorada temporal: 6/6 PASS.
- Suite trusted: `23 passed, 3 skipped`; worktree dorado eliminado.

Documentación:
`docs/benchmark/F1.22B_Verifier_selector_organizacion_2026-09-04.md`.

**Próximo paso:** F1.22C — fijar baseline, hashes y candidatos.

### F1.22D — Cierre de tercera ronda RAT — CERRADA

- Qwen3-4B local: FAIL, 2/6, 112.377609 s.
- Claude Sonnet 5 r2: FAIL, 3/6, 350.831602 s.
- DeepSeek V4 Pro: FAIL, 2/6, 206.228365 s.
- Las tres evidencias efectivas pasaron validación trusted; la primera corrida
  de Claude se preserva como incidencia de etiqueta incorrecta.

Documentación:
`docs/benchmark/F1.22D_Cierre_tercera_ronda_RAT_2026-09-04.md`.

## 2026-09-02 — F1.19A cerrado: contrato y estructura del harness reproducible

Se completó F1.19A del benchmark.

Resultado: PASS.

Artefactos incorporados:

- `docs/benchmark/F1.19A_Contrato_harness_2026-09-02.md`
- `docs/benchmark/runner/run-config.schema.json`
- `docs/benchmark/runner/run-result.schema.json`
- `docs/benchmark/runner/run-config.example.json`

El diseño establece:

- separación explícita entre harness trusted y candidato untrusted;
- workspace efímero controlado por el harness;
- baseline identificado por commit Git completo;
- reutilización independiente del contrato de transporte F1.18A;
- estados autoritativos `PASS`, `FAIL`, `TIMEOUT` y `HARNESS_ERROR`;
- resultado estructurado `result.json`;
- evidencia por corrida con manifest SHA-256;
- prohibición de persistir secretos en configuración, logs o resultados;
- regla fail-closed ante fallas del entorno trusted;
- invariantes de reproducibilidad para comparación entre candidatos.

Los schemas fueron validados con JSON Schema Draft 2020-12.

Pruebas realizadas:

- configuración válida aceptada;
- resultado válido aceptado;
- commit corto rechazado;
- campo adicional rechazado;
- estado inválido rechazado;
- campo obligatorio faltante rechazado;
- ejemplo de configuración validado contra el schema.

La ubicación del workspace no es controlable por la configuración de corrida; será determinada exclusivamente por el harness trusted.

Siguiente etapa: F1.19B — workspace reproducible y aislamiento del repositorio canónico.
