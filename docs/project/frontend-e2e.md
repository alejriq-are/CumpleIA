# Pruebas E2E del frontend — RAT

Playwright ejecuta Chromium contra Next.js, FastAPI y Supabase Auth reales. No hay
mocks, JWT fabricados ni bypass de permisos/RLS. La suite mínima cubre el acceso
sin sesión y un ciclo autenticado del RAT.

## Preparación

Desde el repositorio canónico y la rama de trabajo, usar el entorno Node del
proyecto (Node 22+ recomendado por las dependencias actuales de Supabase;
el cargador de `.env` requiere como mínimo Node 20.12).

1. Mantener `E2E_USER_EMAIL` y `E2E_USER_PASSWORD` exclusivamente en `.env` de la
   raíz. No usar variables `NEXT_PUBLIC_*` para estas credenciales. No copiar
   secretos a comandos, archivos de pruebas, reportes ni al frontend.
2. Preparar PostgreSQL y migraciones según el procedimiento del proyecto.
3. Crear o verificar el fixture idempotente:

   ```bash
   cd backend
   ../.venv/bin/python -m scripts.seed_e2e
   cd ..
   ```

   El fixture usa Supabase Auth real y la organización dedicada
   `11000000-0000-0000-0000-000000000001`, con rol `owner` y suscripción `active`.
   La clave administrativa pertenece exclusivamente al seed/backend; Playwright
   solo utiliza email y contraseña del usuario E2E.
4. Iniciar el backend local en `http://localhost:8000` con la conexión runtime
   restringida `app_user`, nunca con el dueño de tablas. `/health` debe indicar
   `database: ok`. El seed y el backend deben apuntar a la misma base local.
5. Iniciar el frontend en `http://localhost:3000` con la configuración pública
   habitual de `frontend/.env.local` (mismo Supabase y API local). Ambos servicios
   deben estar iniciados antes de ejecutar Playwright; la suite no los detiene.

```bash
cd frontend
npm ci
npm run test:e2e:install
npm run dev
```

En otra terminal, desde `frontend`:

```bash
npm run test:e2e
# Comprobar repetibilidad: dos ejecuciones, dos actividades independientes.
npm run test:e2e -- --repeat-each=2
```

Si Chromium informa bibliotecas faltantes en Linux, instalarlas con
`npx playwright install --with-deps chromium` según los permisos del equipo.

## Cobertura y aislamiento

- Redirección del inventario a login sin sesión.
- Login mediante el formulario real; verificación del token contra la API y de
  membresía `owner` en el tenant E2E antes de crear datos.
- Listado → nueva actividad → detalle; bloqueo de activación incompleta tanto en
  UI como en backend (HTTP 400).
- Finalidad, categoría, titular, fuente y declaraciones negativas explícitas de
  sistemas, proveedores y transferencias: 10 de 10 requisitos persistidos.
- Activación, invalidación automática al dejar sistemas pendientes, resolución,
  retorno manual a preparación, archivo con confirmación y reactivación.
- Persistencia tras recarga y estado activo en el listado final.

Cada ejecución usa un nombre aleatorio y elimina únicamente el ID creado por esa
prueba, mediante la API autenticada y el tenant E2E, incluso si una aserción falla.
La limpieza comprueba HTTP 204 y posterior 404. No vacía tablas ni borra el usuario,
organización o datos anteriores. Si se mata el proceso o cae la API durante la
limpieza puede quedar una actividad `E2E RAT …`; revisarla manualmente en el tenant
de pruebas. Los escenarios afirmativos de sistemas, proveedores y transferencias,
y los roles distintos de owner, quedan fuera de esta suite mínima.

## Secretos y diagnóstico

La sesión vive solamente en memoria, sin `storageState` en disco. Trazas, vídeo y
capturas están desactivados; no habilitarlos con credenciales reales. Los directorios
de resultados y autenticación están ignorados por Git; `preserveOutput: "never"`
elimina los artefactos de cada prueba al terminar. El login devuelve un error
genérico para no propagar argumentos sensibles de las acciones del navegador.
La limpieza usa `fetch` sin registrar headers ni cuerpos de respuesta autenticados.

Credenciales ausentes, servicios inaccesibles, login fallido o fixture inconsistente
hacen fallar la prueba; no se omite silenciosamente. Para fallos de acceso verificar
la configuración local sin imprimir valores. CI puede validar tipos/lint, pero el
E2E requiere este entorno completo y no se agrega al CI genérico sin su fixture.

Referencias: [configuración de Playwright](https://playwright.dev/docs/test-configuration)
y [sesiones autenticadas](https://playwright.dev/docs/auth).
