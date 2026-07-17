# CumpleIA

SaaS para la adecuación de PYMEs chilenas a la **Ley N° 21.719** de Protección de Datos Personales (vigente desde el 1 de diciembre de 2026).

Automatiza el "sprint de adecuación": diagnóstico, inventario de tratamientos (RAT), bases de licitud, generación de documentos y carpeta de evidencia inmutable. Diseñado para micro y pequeña empresa: **simple, económico y autoservicio**.

---

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 15 (App Router) + TypeScript + Tailwind CSS |
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic |
| Base de datos / Auth / Storage | Supabase (PostgreSQL 16 + pgvector + Auth + Storage) |
| LLM | Anthropic Claude (API) |
| Embeddings | Voyage AI (`voyage-3`, dimensión 1024) |
| RAG | pgvector dentro de PostgreSQL |
| CI/CD | GitHub Actions |

---

## Prerrequisitos

- **Docker Desktop** (para Postgres local con pgvector)
- **Python 3.12** y `pip`
- **Node.js 20** y `npm`
- **Git**
- Cuentas de terceros (solo para funcionalidad completa, no para el inicio):
  - [Supabase](https://supabase.com) — Auth, DB en la nube y Storage
  - [Voyage AI](https://www.voyageai.com) — embeddings para el RAG
  - [Anthropic](https://console.anthropic.com) — LLM Claude

---

## Levantar en local

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd CumpleIA
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y completa **al menos** estas variables para el desarrollo local básico:

```env
# Obligatorias para levantar el backend sin Supabase en la nube
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cumpleia
SECRET_KEY=una-clave-larga-y-aleatoria

# Requeridas para autenticación real con Supabase
SUPABASE_URL=https://<tu-proyecto>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_JWT_SECRET=<jwt-secret>   # Project Settings > API > JWT Secret

# Requeridas para el RAG
VOYAGE_API_KEY=<clave-voyage-ai>

# Requeridas para generación de documentos con IA
ANTHROPIC_API_KEY=<clave-anthropic>
```

> Las variables del frontend van en `frontend/.env.local` (copia `frontend/` y rellena `NEXT_PUBLIC_*`).

### 3. Levantar la base de datos local (Docker)

```bash
docker compose up -d postgres
```

Esto levanta **PostgreSQL 16 con pgvector** en el puerto `5432`.

Verificar que está sana:

```bash
docker compose ps        # Estado: healthy
```

### 4. Instalar dependencias del backend

```bash
cd backend
pip install -r requirements.txt
```

### 5. Aplicar migraciones

```bash
# Desde el directorio backend/
alembic upgrade head
```

Esto crea todas las tablas, extensiones, enums, índices y políticas RLS.

### 6. Crear datos de prueba (seed de desarrollo)

```bash
python -m scripts.seed_dev
```

Crea una organización "Organización Demo" y un perfil `dev@cumpleia.cl` con rol `owner`.

### 7. Levantar el backend

```bash
uvicorn app.main:app --reload --port 8000
```

- API disponible en `http://localhost:8000`
- Swagger en `http://localhost:8000/docs`
- Health check: `GET http://localhost:8000/health`

### 8. Instalar dependencias del frontend

```bash
cd frontend
npm install
```

Crea `frontend/.env.local` con las variables `NEXT_PUBLIC_*`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://<tu-proyecto>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 9. Levantar el frontend

```bash
npm run dev
```

Aplicación disponible en `http://localhost:3000`.

### 10. Ingestar base de conocimiento RAG (opcional)

Deposita archivos `.txt` o `.md` en `/docs/fuentes/` con nombres que contengan `ley_21719` o `guia_ccs`, luego ejecuta:

```bash
cd backend
python -m scripts.ingest --embed          # con Voyage AI
python -m scripts.ingest --examples       # fragmentos de prueba sin Voyage AI
```

Probar la búsqueda:

```bash
curl -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "bases de licitud consentimiento", "top_k": 3}'
```

---

## Levantar todo con Docker Compose

Para levantar backend + Postgres en un solo comando:

```bash
docker compose up -d
```

El backend usará `DATABASE_URL` del `.env`. Hot-reload activo (el volumen `./backend` está montado).

---

## Correr los tests

Los tests requieren Postgres activo con la migración aplicada.

```bash
cd backend
pytest tests/ -v
```

Tests incluidos:
- **`test_tenant_isolation.py`** — aislamiento multi-tenant (requisito de aceptación): verifica que usuario B no puede leer datos de la organización A, y viceversa.
- **`test_rag.py`** — validación del endpoint RAG.

Para correr solo los tests de aislamiento:

```bash
pytest tests/test_tenant_isolation.py -v
```

---

## CI/CD

GitHub Actions corre en cada `push` y `pull_request` hacia `master`/`main`:

| Job | Pasos |
|---|---|
| **Backend** | `ruff` lint → `black` formato → migraciones → `pytest` (incluye tests de aislamiento) |
| **Frontend** | `npm install` → `eslint` → `prettier` |

Postgres 16 + pgvector corre como servicio en el runner de CI.

---

## Estructura del repositorio

```
/frontend                    # Next.js (App Router)
  /app
    /login                   # Página de autenticación
    /dashboard               # Dashboard protegido (requiere sesión)
  /components/auth           # LoginForm
  /lib/supabase              # Clientes browser y server de Supabase
  /lib/api                   # Cliente tipado del backend
  middleware.ts              # Protección de rutas

/backend                     # FastAPI
  /app
    /api                     # Routers: health, me, rag
    /core                    # Config (Pydantic Settings), seguridad, dependencias
    /db                      # Modelos SQLAlchemy, sesión, base declarativa
    /services                # Lógica RAG (embeddings, búsqueda)
    /schemas                 # (próximos pasos)
  /alembic                   # Migraciones de BD
  /scripts                   # seed_dev.py, ingest.py
  /tests                     # Tests de aislamiento multi-tenant y RAG

/db                          # Extras de esquema
/infra                       # Dockerfile.backend
/docs
  /fuentes                   # Archivos fuente para RAG (Ley 21.719, guía CCS)
/docs

.github/workflows/ci.yml     # GitHub Actions CI
docker-compose.yml           # Postgres 16 + pgvector + backend
schema.sql                   # Esquema SQL de referencia
CLAUDE.md                    # Contexto permanente para Claude Code
.env.example                 # Plantilla de variables (nunca committear .env real)
```

---

## Variables de entorno — referencia completa

| Variable | Descripción | Requerida para |
|---|---|---|
| `DATABASE_URL` | URL asyncpg de PostgreSQL | Backend (siempre) |
| `SUPABASE_URL` | URL del proyecto Supabase | Auth en la nube |
| `SUPABASE_ANON_KEY` | Clave anónima de Supabase | Frontend + backend |
| `SUPABASE_SERVICE_ROLE_KEY` | Clave de rol de servicio | Operaciones admin |
| `SUPABASE_JWT_SECRET` | Secret para validar JWTs | Backend auth |
| `ANTHROPIC_API_KEY` | API key de Anthropic | LLM (Fase 1+) |
| `VOYAGE_API_KEY` | API key de Voyage AI | Embeddings RAG |
| `SECRET_KEY` | Clave interna del backend | Siempre |
| `ENVIRONMENT` | `development` / `production` | Configuración |
| `NEXT_PUBLIC_SUPABASE_URL` | URL Supabase (frontend) | Login/registro |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Clave anónima (frontend) | Login/registro |
| `NEXT_PUBLIC_API_URL` | URL del backend desde el browser | Llamadas API |

---

## Git workflow

```bash
# Formato de commits (Conventional Commits)
git commit -m "feat: descripción del cambio"
git commit -m "fix: corrección de bug"
git commit -m "chore: tarea de mantenimiento"
git commit -m "docs: actualización de documentación"
```
