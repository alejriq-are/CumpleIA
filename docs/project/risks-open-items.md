# Riesgos, inconsistencias y asuntos abiertos

## Prioridad alta - ordenar antes de seguir mucho más

### 1. Drift de `CLAUDE.md` — RESUELTO (2026-09-15)

Verificado en [`CLAUDE.md`](../../CLAUDE.md), secciones 1/2/8: remite a `AGENTS.md` y `docs/project/`, declara Fase 0 completada, reconoce el MVP funcional del Módulo 1 y distingue los Módulos 2-5 pendientes. La instrucción desactualizada que originó este riesgo ya fue corregida.

**Cierre:** verificación documental sobre `origin/main` (`146428e`); no requiere cambios adicionales para resolver este riesgo específico.

### 2. Estados contradictorios de `docs/backlog.md` — RESUELTO (2026-09-15)

Verificado en [`docs/backlog.md`](../backlog.md): Autodiagnóstico declara Tareas 0-6 completadas para el MVP; Tareas 4/5 y Tarea 6 figuran con `[x]` y tienen secciones de implementación. La contradicción de estados señalada ya fue corregida.

**Cierre:** verificación documental sobre `origin/main` (`146428e`). Se conservan las mejoras pendientes del backlog y los demás riesgos vigentes; este cierre no equivale a una depuración general del documento.

### 3. `schema.sql` quedó en Fase 0

No contiene suscripciones, configuración del cuestionario, reference documents ni varias correcciones RLS posteriores.

**Acción:** etiquetarlo explícitamente como histórico o regenerar un esquema de referencia desde las migraciones. La fuente de verdad seguirá siendo Alembic.

### 4. Estado del PR #20 no coincide entre documento y refs Git

**Acción:** `git fetch` + verificar GitHub antes de iniciar otra rama.

## Seguridad/higiene

### 5. ZIP contiene secretos locales aunque Git los ignore

Se encontraron `.env.local` en la copia subida. No se copiaron a este repositorio de conocimiento ni se leyeron sus valores.

**Acción:** excluirlos también del proceso de compresión/backup compartido.

### 6. Carpetas de sesión de Claude en la raíz

`Claude_17_julio_2026/`, `Claude_22_julio_2026/`, `Fase 1/` y `Modulo 1/` están untracked en el snapshot y mezclan fuentes, outputs, estados y prompts.

**Acción:** conservar solo lo útil bajo `docs/archive/` y eliminar duplicados/temporales de la carpeta activa.

## Producto/técnico

### 7. Un solo Diagnostic por organización

Bloquea re-evaluaciones e histórico.

### 8. `reference_documents` sin endpoint

Modelo existe; carga/vinculación no está construida.

### 9. Sin testing frontend

No es un bug inmediato, pero cualquier crecimiento de UI aumentará riesgo de regresión.

### 10. Proveedor de IA parcialmente desacoplado

La interfaz es portable, pero solo Anthropic y Voyage tienen adaptador. Cambiar a otro proveedor requiere implementar el adaptador.

### 11. Dimensión fija de embeddings

`Vector(1024)` hace que un cambio de modelo con otra dimensión requiera trabajo de datos/migración.

### 12. Módulos 2-5: modelos no equivalen a funcionalidad

El scaffolding temprano es útil pero puede inducir a un agente a asumir que esos módulos ya existen. Debe comprobar endpoints/servicios/UI antes de afirmar que una feature está construida.
