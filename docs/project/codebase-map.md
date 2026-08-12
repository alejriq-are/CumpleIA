# Mapa del código

## Raíz

- `.github/workflows/ci.yml` - CI backend/frontend.
- `.env.example` - contrato de configuración del backend.
- `docker-compose.yml` - Postgres + backend.
- `README.md` - instrucciones generales, hoy parcialmente desactualizadas.
- `CLAUDE.md` - contexto para Claude, hoy desactualizado respecto de Fase 1.
- `schema.sql` - referencia de Fase 0; **no es el esquema autoritativo actual**.

## Backend

### API

| Prefix | Operaciones observadas |
|---|---|
| `/health` | salud |
| `/me` | perfil, organizaciones, membresía |
| `/organizations` | crear y actualizar organización |
| `/rag` | búsqueda semántica |
| `/cuestionario-config` | leer/crear versión de configuración; superadmin |
| `/diagnostico` | cuestionario, respuestas, estado, informe, exportación |

### Servicios

- `authorization.py` - permisos por rol.
- `subscriptions.py` - estado de suscripción.
- `cuestionario_config.py` - catálogo/configuración versionada.
- `diagnostico_puntaje.py` - scoring puro y brechas.
- `diagnostico.py` - persistencia y recálculo.
- `diagnostico_ia.py` - narrativa LLM + RAG + guardarraíles.
- `diagnostico_exportacion.py` - HTML del informe.
- `rag.py` - recuperación de chunks.
- `providers/` - contratos de LLM y embeddings.

### Base de datos

`backend/app/db/models.py` contiene 20 modelos ORM agrupados en núcleo, configuración, diagnóstico, scaffolding de módulos futuros y RAG.

### Migraciones

`backend/alembic/versions/0001` a `0009` son la fuente de verdad del esquema y políticas. `schema.sql` solo documenta la base inicial.

## Frontend

### Rutas principales

- `/login`
- `/forgot-password`
- `/reset-password`
- `/dashboard`
- `/dashboard/autodiagnostico`
- `/dashboard/organizacion`
- `/admin/cuestionario-config`

### Componentes clave

- `AutodiagnosticoWorkspace.tsx`
- `Cuestionario.tsx`
- `ResultadosDashboard.tsx`
- `OrganizacionForm.tsx`
- `CuestionarioConfigEditor.tsx`

## Tests

Hay pruebas de autenticación, provisioning, autorización, suscripciones, RAG, scoring, servicio/API del diagnóstico y aislamiento RLS/tenant. No existe framework de testing frontend instalado todavía.
