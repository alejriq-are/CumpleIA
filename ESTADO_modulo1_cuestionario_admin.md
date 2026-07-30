# Estado — Módulo 1: config del cuestionario + panel admin (28 jul 2026)

## Diseño cerrado (no rehacer)

Las 8 obligaciones no son invento de CumpleIA: están literales en la guía CCS, sección 1 (1.1-1.8). Gobernanza (sección I) y Capacitación (sección IX) no figuran ahí como obligación propia — se agrupan junto con Evidencia (X) bajo la Obligación 8 "Responsabilidad demostrable", con base en la FAQ N°19 de la misma guía.

Pesos por sección, ya ajustados y vigentes en el JSON: Gobernanza 6, Inventario 14, Bases de licitud 14, Transparencia 8, ARSOP-B 13, Seguridad 16, Incidentes 12, Proveedores 12, Capacitación 2, Evidencia 3 (suma 100).

Archivos fuente (en `docs/Modulo1/` del repo): `cuestionario_autodiagnostico_config.json` (50 preguntas reales, pesos, riesgo), `schema_modulo1_cuestionario.sql` (DDL de referencia), `SPEC_admin_config_cuestionario.md` (spec del panel).

## Construido por Code (pasos 1-4 del prompt)

Migración Alembic `0002_modulo1_cuestionario_config.py`, seed idempotente (`backend/scripts/seed_modulo1_cuestionario.py`), endpoints `GET/POST /cuestionario-config` con guard de superadmin y validación completa antes de escribir (`app/services/cuestionario_config.py`), y las dos pantallas de admin (pesos con validación de suma en vivo, riesgo por pregunta en acordeones). 51/51 tests backend pasando, build/lint/typecheck frontend limpios.

Code encontró y corrigió un error real en mi pseudocódigo de referencia (el orden debía ser desactivar-versión-vieja-antes-de-activar-nueva, no al revés, por el índice único parcial) — **falta actualizar el comentario en `schema_modulo1_cuestionario.sql` para que no confunda a futuro**.

Todo esto sigue **sin commitear** en `main` (`git status` mostraba solo cambios locales). Antes de seguir construyendo encima, hay que decidir si se commitea directo o se mueve a una rama — esto último es lo que dice nuestro propio flujo de trabajo (agentes en rama separada, revisión de diff antes de merge), que no se siguió esta vez.

## Bloqueo de hoy — sin resolver

No se pudo entrar a `http://localhost:3000/admin/cuestionario-config`. Se resolvió en el camino: PowerShell (execution policy + sintaxis rm/npm), `.env` con `DATABASE_URL` vacío en la raíz del repo (ya corregido, ahora apunta a `postgresql+asyncpg://postgres:postgres@localhost:5432/cumpleia`), migración aplicada, seed confirmado (ya existía v1, corrido por Code contra el mismo Postgres local), y el `UPDATE profiles SET is_superadmin = true WHERE email = 'alejandro.riquelme91@gmail.com'` — pero no se confirmó que ese último UPDATE haya afectado 1 fila (el primer intento falló por usar un email de ejemplo en vez del real; no llegamos a ver el resultado del segundo intento antes de cortar por hoy).

**Primer paso de mañana**, en este orden:
1. Confirmar el UPDATE con `docker exec -it cumpleia_db psql -U postgres -d cumpleia -c "SELECT email, is_superadmin FROM profiles;"` — ver si de verdad quedó en `true`.
2. Si sí quedó en `true` y sigue sin entrar: abrir la consola del navegador (F12) → pestaña Network, recargar `/admin/cuestionario-config`, y mirar el código de estado de la petición a la página y a `GET /cuestionario-config` (¿302 a login? ¿403? ¿404? ¿500?). Ese código dice exactamente dónde mirar después.
3. Si es 404: puede que la ruta de Next.js no se esté generando (revisar que `frontend/app/admin/` tenga la estructura de carpetas correcta para App Router).
4. Si es 403: el guard de superadmin en el backend no está viendo el flag — revisar `app/core/deps.py` y si el backend necesita reiniciarse para tomar el cambio en la fila de `profiles`.

## Pendiente de decidir con Code

Paso 5 (test de RLS a nivel de base de datos para `autodiagnosticos`/`autodiagnostico_respuestas`) — se le dio luz verde pero no hay confirmación de resultado en esta conversación; preguntarle a Code cómo quedó.

"Ver historial de versiones": la spec lo menciona pero no hay endpoint — decidir si se construye ahora o se saca de la spec.

Limpieza de archivos sueltos que aparecieron como untracked en el repo y no deberían commitearse tal cual: `body.json`, `ccs_extracted.txt`, `extract_ccs.py`, `mvp_docx_extracted.txt`, `Claude_17_julio_2026/`, `Claude_22_julio_2026/` — parecen artefactos de trabajo, revisar antes de hacer commit.
