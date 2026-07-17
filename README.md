# CumpleIA

SaaS para la adecuación de PYMEs chilenas a la **Ley N° 21.719** de Protección de Datos Personales (vigente desde el 1 de diciembre de 2026).

Automatiza el "sprint de adecuación": diagnóstico, inventario de tratamientos (RAT), bases de licitud, generación de documentos y carpeta de evidencia inmutable. Diseñado para micro y pequeña empresa: simple, económico y autoservicio.

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

## Levantar en local (próximamente)

> Esta sección se completará cuando estén listos los Dockerfiles y la configuración de desarrollo.

```bash
# Próximamente...
```

---

## Estructura del repositorio

```
/frontend        # Next.js (App Router)
/backend         # FastAPI
  /app
    /api         # Routers por recurso
    /core        # Config, seguridad, dependencias
    /db          # Modelos SQLAlchemy, sesión
    /services    # Lógica de negocio (RAG, ingesta, etc.)
    /schemas     # Esquemas Pydantic
  /alembic       # Migraciones de base de datos
  /scripts       # Ingesta de conocimiento, seeds
  /tests         # Tests automatizados
/db              # Extras de esquema y políticas RLS
/infra           # Dockerfiles, docker-compose, CI
/docs            # Documentación del proyecto
  /fuentes       # Archivos fuente para RAG (Ley 21.719, guía CCS, etc.)
CLAUDE.md        # Contexto permanente para Claude Code
README.md
.env.example     # Plantilla de variables de entorno (sin valores reales)
schema.sql       # Esquema de referencia de la base de datos
```
