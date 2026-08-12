# Gobernanza de documentación

## Jerarquía de fuentes de verdad propuesta

### Nivel 1 - Estado ejecutable

1. Git (`main` remoto actualizado).
2. Migraciones Alembic.
3. Código + tests.

### Nivel 2 - Decisiones vigentes

4. ADRs aceptados.
5. `docs/PROJECT_STATUS.md` actualizado al cierre de cada bloque de trabajo.
6. `docs/BACKLOG.md` único y depurado.

### Nivel 3 - Objetivo de producto

7. Especificación MVP/arquitectura.
8. Documentos comerciales y de oportunidad.

### Nivel 4 - Historia

9. Notas de sesiones fechadas.
10. prompts antiguos, estados diarios y documentos de transición.

Un archivo histórico nunca debe contradecir o sobreescribir el estado ejecutable.

## Regla de actualización

Al cerrar un PR importante:

- actualizar `PROJECT_STATUS.md` solo si cambió una capacidad del sistema;
- actualizar `BACKLOG.md` si se cerró/abrió trabajo;
- crear/actualizar ADR solo si cambió una decisión arquitectónica;
- no crear otro “estado-fecha.md” en la raíz salvo que vaya directamente a `docs/archive/`.

## Archivos a evitar como fuentes paralelas

- múltiples copias del mismo plan en distintas carpetas;
- `schema.sql` manual que pretende competir con Alembic;
- instrucciones de una IA que contengan el estado completo del producto;
- bitácoras de sesión como backlog permanente.
