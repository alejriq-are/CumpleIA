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
