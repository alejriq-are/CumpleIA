# Desarrollo, Git y CI

## Flujo Git observado

Convenciones usadas:

- `feature/moduloN-tareaM-...`
- `fix/moduloN-tareaM-...`
- PR por tarea/fix.
- Revisión de CI antes de merge.

El historial muestra PRs incrementales para RLS, scoring, API, IA, exportación y frontend.

## CI actual

### Backend

- Python 3.12
- Postgres 16 + pgvector como servicio
- `ruff check .`
- `black --check .`
- `alembic upgrade head`
- seed/config necesario para tests
- `pytest tests/ -v --tb=short`

### Frontend

- Node 20
- `npm install`
- `npm run lint`
- `npm run type-check`

No hay test runner frontend.

## Checklist recomendado antes de una nueva tarea

1. `git fetch` y confirmar `main` remoto.
2. `git status` limpio.
3. `docker compose up -d`.
4. `alembic upgrade head`.
5. backend: lint + format-check + tests.
6. frontend: type-check + lint.
7. health check real.
8. crear rama nueva desde `main` actualizado.

## Regla operativa aprendida

El proyecto ya sufrió casos donde CI verde no detectaba un fallo real porque ciertos tests usaban un rol que bypassaba RLS. Por eso, cambios sensibles a tenant deben probarse con el rol restringido real y, cuando corresponda, con dos usuarios/dos organizaciones.
