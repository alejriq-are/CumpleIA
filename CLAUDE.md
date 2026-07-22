# CLAUDE.md — Contexto del proyecto CumpleIA

> Este archivo va en la **raíz del repositorio**. Claude Code lo lee automáticamente en cada sesión y lo usa como memoria/contexto permanente. Mantenlo actualizado.

## 1. Qué es el producto

**CumpleIA** es un SaaS multi-tenant para que PYMEs chilenas cumplan la **Ley N° 21.719** de Protección de Datos Personales (entra en vigencia el 1 de diciembre de 2026). Automatiza con IA el "sprint de adecuación": diagnóstico, inventario de tratamientos (RAT), bases de licitud, generación de documentos y una carpeta de evidencia inmutable.

Segmento objetivo: micro y pequeña empresa. Prioridades de diseño: **simple, económico, autoservicio**.

## 2. Módulos del MVP (contexto, no todos se construyen en Fase 0)

1. Autodiagnóstico inteligente (cuestionario CCS + scoring + informe de brechas).
2. Asistente de inventario (RAT) con detección de datos sensibles y transferencias internacionales.
3. Motor de bases de licitud (clasifica + justifica + genera LIA).
4. Generador de documentos (4 políticas + 2 procedimientos, Word/PDF).
5. Carpeta de evidencia (bitácora inmutable + exportación del expediente).

**Fase 0 (esta etapa)** construye SOLO los cimientos: repo, auth, multi-tenant, modelo de datos base, CI/CD e ingesta de la base de conocimiento para RAG. NO se construye la lógica de los módulos todavía.

## 3. Stack tecnológico (decidido)

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS.
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic (migraciones) + Pydantic v2.
- **Base de datos / Auth / Storage:** Supabase (PostgreSQL 16 + pgvector + Supabase Auth + Supabase Storage). Una sola cuenta cubre dev.
- **LLM:** API de Anthropic (Claude). **Embeddings:** Voyage AI (`voyage-3`, dimensión 1024). *(Alternativa: OpenAI embeddings; si cambia el modelo, ajustar la dimensión del vector.)*
- **RAG:** pgvector dentro de la misma base PostgreSQL.
- **Ingesta de PDFs:** `pypdf` (BSD, sin dependencias del sistema) para extraer texto de las fuentes legales en `docs/fuentes/` antes de chunkear (`backend/scripts/ingest.py`). No hace OCR: un PDF escaneado como imagen se reporta pero no se procesa.
- **CI/CD:** GitHub Actions.
- **Despliegue (más adelante, no en Fase 0):** Vercel (frontend) + Render/Railway/Fly (backend).

> Regla: no introducir nuevas dependencias o servicios sin dejarlos anotados aquí y justificarlos. Preferir servicios con capa gratuita.

## 4. Estructura del repositorio (monorepo)

```
/frontend        # Next.js
/backend         # FastAPI
  /app
    /api         # routers por recurso
    /core        # config, seguridad, dependencias
    /db          # modelos SQLAlchemy, sesión
    /services    # lógica (RAG, ingesta, etc.)
    /schemas     # Pydantic
  /alembic       # migraciones
  /scripts       # ingesta de conocimiento, seeds
  /tests
/db              # schema.sql de referencia y políticas RLS
/infra           # Dockerfiles, docker-compose, CI
/docs            # documentación del proyecto
CLAUDE.md
README.md
.env.example     # NUNCA committear .env real
```

## 5. Reglas de arquitectura

- **Monolito modular:** un solo backend; separar por módulos con límites claros. No microservicios.
- **Multi-tenant estricto:** toda tabla de negocio lleva `organization_id`. El aislamiento se refuerza con **Row-Level Security (RLS)** en PostgreSQL. Ninguna consulta debe poder cruzar organizaciones.
- **Campos de auditoría** en toda tabla: `id` (uuid), `organization_id`, `created_at`, `updated_at`, `created_by`, `updated_by`.
- **IA con anclaje (RAG):** el LLM nunca genera texto legal libre. Siempre recupera fragmentos de la Ley 21.719 / guía CCS + plantillas, y produce salidas estructuradas (JSON schema / tool calling). Revisión humana obligatoria antes de marcar un documento como aprobado.
- **Evidencia inmutable:** la tabla `evidence_events` es append-only con hash encadenado (cada evento guarda el hash del anterior). Nunca se actualiza ni borra un evento.

## 6. Reglas de seguridad (críticas — no relajar)

- Secretos SOLO por variables de entorno / gestor de secretos. Nunca en el código ni en el repo. Mantener `.env.example` con claves vacías.
- Cifrado en tránsito (TLS) y en reposo (Supabase lo provee).
- Validar el JWT de Supabase en el backend en cada request; derivar `organization_id` y rol del usuario, nunca confiar en lo que envíe el cliente.
- Escribir **tests de aislamiento multi-tenant**: un usuario de la organización A jamás debe leer datos de la B. Esto es requisito de aceptación, no opcional.
- No loguear datos personales ni secretos.

## 7. Convenciones de código

- Python: PEP8, `ruff` + `black`, type hints obligatorios, funciones pequeñas.
- TypeScript: ESLint + Prettier, tipado estricto.
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`…).
- Tests: `pytest` (backend). Toda funcionalidad de seguridad/tenant lleva test.
- Todo el texto de cara al usuario en **español (Chile)**.

## 8. Qué NO hacer

- No construir la lógica de los 5 módulos en Fase 0 (solo cimientos).
- No inventar contenido legal: los textos de la ley y la guía CCS los provee la usuaria; el sistema los ingesta y cita, no los redacta de memoria.
- No crear cuentas de terceros ni manejar claves reales; dejar `.env.example` y pedir a la usuaria que complete.
- No usar `localStorage`/`sessionStorage` para datos sensibles.
