# AGENTS.md - Instrucciones neutrales para agentes de IA

## 1. Antes de tocar código

1. Ejecuta `git fetch` y verifica rama/HEAD/estado.
2. Lee `docs/PROJECT_STATUS.md` o, si aún no fue incorporado al repo activo, el `PROJECT_STATUS.md` de este paquete.
3. Lee los ADR vigentes.
4. Revisa `docs/backlog.md`, pero confirma cualquier afirmación contra código/Git porque el snapshot revisado contiene drift documental.
5. No tomes notas históricas fechadas como estado vivo.

## 2. Arquitectura que no debes romper

- Monorepo Next.js + FastAPI.
- PostgreSQL/Supabase multi-tenant.
- Runtime DB con `app_user` sin `BYPASSRLS`.
- RLS como segunda barrera de aislamiento.
- `X-Organization-Id` siempre validado en servidor.
- Scoring del diagnóstico determinista, sin LLM.
- IA legal anclada a RAG y con validaciones.
- Proveedores IA accedidos mediante `app/services/providers/`, no importando SDKs desde lógica de negocio nueva.

## 3. Seguridad

- Nunca leas, imprimas, commitees o copies secretos reales.
- No uses `DATABASE_URL` del dueño de tablas como conexión runtime.
- Toda tabla de dominio nueva debe definir `organization_id`/tenant y RLS si corresponde desde la primera migración.
- Agrega tests de aislamiento cuando una tarea introduce acceso a datos por organización.
- No confíes en autorización implementada solo en frontend.

## 4. Flujo de trabajo

- Nueva tarea -> rama `feature/...`.
- Fix de revisión -> rama `fix/...`.
- No mezclar cambios sin relación.
- Migraciones nuevas son append-only; no reescribir migraciones históricas aplicadas.
- Antes de merge: lint, formato, migraciones, tests backend, type-check/lint frontend y una prueba real del flujo afectado cuando sea razonable.

## 5. IA/RAG

- `LLM_PROVIDER` es una abstracción, pero solo usa proveedores con adaptador registrado.
- No inventes citas ni reglas legales.
- Preferir cálculo estructurado/determinista para scoring, clasificación y reglas de negocio reproducibles.
- Si cambias embeddings y cambia la dimensión, diseña explícitamente la migración/reingesta.

## 6. Estado funcional asumible solo tras verificar código

Módulo 1 está construido en este snapshot. Módulos 2-5 tienen modelos/scaffolding, no funcionalidad completa. Nunca declares una feature “hecha” solo porque existe una tabla.

## 7. Documentación

Cuando una tarea cambia capacidad del sistema, actualiza documentación neutral. Evita crear otro archivo de estado fechado en la raíz; usa `docs/archive/` para historia.
