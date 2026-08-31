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
