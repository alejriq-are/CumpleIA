# AGENTS.md - Instrucciones neutrales para agentes de IA

## 1. Antes de tocar código

1. Ejecuta `git fetch` y verifica rama/HEAD/estado.
2. Lee `docs/HANDOFF.md` y el contrato de la tarea activa; estado amplio en `docs/project/status.md`.
3. Lee los ADR vigentes aplicables, incluido `docs/adr/0003-handoff-chatgpt-deepseek.md`.
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

El estado funcional se verifica en Git/pruebas y se resume en `docs/HANDOFF.md` y `docs/project/status.md`. Nunca declares una feature “hecha” solo porque existe una tabla.

## 7. Documentación

Cuando una tarea cambia capacidad del sistema, actualiza documentación neutral. Evita crear otro archivo de estado fechado en la raíz; usa `docs/archive/` para historia.

## 8. Gobernanza y handoff

Roles activos: usuario, ChatGPT/Codex y Deepseek. Aplicar
`docs/ai/handoff-contract.md`: separar jerarquia de reglas de evidencia; accesos
por sesion; un responsable por tarea. Deepseek entrega parches acotados; Codex
revisa/valida/publica solo con autorizacion del usuario. EIPD bloqueada, datos
ficticios y ningun merge/despliegue. No inferir permisos por una CI aprobada.
Reglas comunes antes distribuidas en CLAUDE.md: monolito modular; TLS en transito
y cifrado en reposo; metadatos auditables segun contrato; no loguear
secretos/datos personales; no almacenar sensibles en localStorage/sessionStorage;
validar JWT/permisos en servidor; contenido legal anclado con revision humana;
texto visible en espanol Chile; Python ruff/black, TypeScript ESLint/Prettier;
commits Conventional Commits. No agregar cuentas, servicios/dependencias ni
credenciales sin necesidad y autorizacion aplicable. Mantener evidencia append-only.
