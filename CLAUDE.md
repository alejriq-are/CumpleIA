# CLAUDE.md - Adaptador para Claude

Reglas comunes y gobernanza: `AGENTS.md`. Estado vigente: `docs/HANDOFF.md` y
`docs/project/status.md`. Contrato de relevo: `docs/ai/handoff-contract.md`.
Arquitectura: `docs/project/architecture.md`.
Este archivo no contiene estado, roles activos ni autorizaciones: solo contexto estable.

## Producto

**CumpleIA** es un SaaS multi-tenant para que PYMEs chilenas cumplan la Ley N° 21.719
de Protección de Datos Personales (vigente desde el 1 de diciembre de 2026).
Segmento: micro y pequeña empresa. Prioridades: simple, económico, autoservicio.

## Stack

- Frontend: Next.js (App Router) + TypeScript + Tailwind CSS.
- Backend: Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2.
- Datos: Supabase (PostgreSQL 16 + pgvector, Auth, Storage).
- LLM: API de Anthropic. Embeddings: Voyage AI (`voyage-3`, dimensión 1024). RAG con pgvector.
- CI/CD: GitHub Actions.
- No introducir dependencias o servicios sin anotarlos aquí y justificarlos.

## Estructura

```
/frontend   Next.js
/backend    FastAPI (app/{api,core,db,services,schemas}, alembic, scripts, tests)
/db         schema.sql de referencia y políticas RLS
/infra      Dockerfiles, docker-compose, CI
/docs       documentación del proyecto
```

## Además de AGENTS.md

- No inventar contenido legal: los textos de la ley y la guía CCS los provee la usuaria;
  el sistema los ingesta y cita, no los redacta de memoria.
- No crear cuentas de terceros ni manejar claves reales; `.env.example` con claves vacías
  y NUNCA committear `.env` real.
- Frontend e2e: `@playwright/test` (solo desarrollo) verifica login y flujos reales en
  Chromium. Configuración y operación en `docs/project/frontend-e2e.md`.
