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

### Cliente de revision EIPD (§159)

`npm run test:eipd-client` ejecuta `e2e/eipd-api-client.spec.ts` con Playwright
como runner, sin fixture page/browser ni red real. No requiere servicios locales,
sesion personal ni base de datos; fetch se simula/restaura en cada caso.
Once casos de contratos, headers, alcance, cache y errores. Estos checks no sustituyen
una futura prueba real de interfaz ni autorizacion del backend.

### Consulta interna EIPD (§160)

`npm run test:eipd-consultation` compila el componente React real en un directorio
temporal, eliminado al terminar, y ejecuta cuatro interacciones en Chromium.
No usa servicios, JWT personal ni base de datos; callbacks sinteticos prueban carga,
limpieza de contexto, errores y lectura historica. No sustituye prueba de layout
administrativo/autenticacion ni integracion de la sesion personal contra API real.
Pantalla: `/admin/licitud-validation`, solo lectura con UUID explicitos del expediente.

### Validacion manual local de consulta interna (§160)

Validacion manual posterior con sesion personal y datos ficticios locales: consulta
V3 muestra las tres decisiones; identificadores inexistentes de evaluacion, tratamiento,
revision y organizacion devuelven ausencia sin conservar resultados; restaurar alcance
recupera las tarjetas. Se comprobo la validacion de campo obligatorio en Revision.
Se preparo un borrador de investigacion estadistica para una finalidad de prueba en
el tratamiento existente mediante servicios de dominio y rol runtime restringido.
Se actualizo explicitamente su contexto RAT y se revinculo investigacion: aviso de
contexto desactualizado desaparecio en servicio y pantalla. Estas escrituras locales
no son parte del repositorio. No se registro revision ni se confirmo o activo EIPD.
Pendientes: lectura de un evento existente y aislamiento entre dos organizaciones
existentes de prueba; organizacion inexistente no acredita ese aislamiento completo.

## 2026-10-10 — M3-T1 §161: validacion manual de revision guardada

Con sesion personal en la pantalla interna y datos ficticios locales, se preparo
un documento EIPD incompleto vinculado al contexto V2 de investigacion y se registro
una decision sintetica requiere_cambios mediante servicios de dominio y rol runtime.
La consulta mostro decision, fundamento de prueba, referencia, fecha UTC, politica
deshabilitada registrada y metadata de contexto V2/cobertura de investigacion.
Un identificador de revision inexistente produjo ausencia; restaurar el correcto
recupero el mismo evento. Cambiar organizacion limpia Revision y resultados:
se reingreso expresamente el identificador antes de comprobar el rechazo.

Se verifico en la base que las dos organizaciones de prueba existen y pertenecen
a cuentas distintas. Con la sesion original, consultar el evento de la primera bajo
la segunda devolvio ausencia sin mostrarlo; restaurar la organizacion propietaria
recupero el evento y sus mismos datos historicos. Este resultado acredita ese caso
manual, no una prueba reciproca con la segunda cuenta ni cobertura exhaustiva de RLS.
No se otorgaron membresias ni permisos adicionales para la prueba.

Escrituras ficticias solo en base local; ningun registro, correo, UUID personal,
credencial o token se incorpora al repositorio. Sin cambio de codigo ni migracion.
Validacion: resultados de pantalla comunicados por el usuario; checks automatizados
§160 (4 interacciones, 11 cliente, tipos/lint) y §158 (621 backend) no repetidos.
M3-T1 EN PROGRESO; fuentes/aceptacion pendientes; continuar/confirmar/activar bloqueados.
Proximo: prueba reciproca con la segunda cuenta en su expediente autorizado, sin
ampliar permisos, y mejorar presentacion de motivos si corresponde.

## 2026-10-10 — M3-T1 §162: segunda sesion y acceso administrativo

Validacion manual con una segunda cuenta personal autenticada, propietaria de una
organizacion de prueba distinta y sin permiso global superadmin. Las membresias y
la separacion de organizaciones se comprobaron mediante consulta local solo lectura.
Abrir el tratamiento de la primera organizacion desde la segunda sesion mostro
Actividad de tratamiento no encontrada, sin cargar datos. Su inventario propio
mostro ausencia de actividades y no incluyo las de la primera organizacion.
La pagina /admin/licitud-validation redirigio a /dashboard por falta de superadmin.
No se ampliaron roles ni membresias para realizar la prueba.

Tras cerrar la segunda sesion y recuperar la cuenta original autorizada, se consulto
la revision ficticia existente: requiere_cambios, fundamento, referencia, fecha UTC,
politica deshabilitada y metadata de contexto V2 conservaron los valores registrados.
Resultados observados y comunicados por el usuario mediante capturas de pantalla.

Alcance: tratamiento RAT ajeno, listado propio, restriccion de pagina administrativa
y recuperacion de acceso autorizado. No constituye consulta reciproca de la API EIPD
con token de la segunda cuenta ni cobertura exhaustiva de aislamiento/RLS.
La cuenta automatizada de pruebas no se utilizo: no se verifico acceso utilizable.
Sin codigo ni migraciones; datos ficticios y organizacion nueva solo en base local.
Sin correos, identificadores personales, credenciales ni tokens en el repositorio.
Checks automatizados anteriores no repetidos por tratarse de documentacion.
M3-T1 EN PROGRESO; fuentes/aceptacion pendientes; confirmacion y activacion bloqueadas.
Proximo: mejorar presentacion de los motivos pendientes de la consulta V3 y mantener
como pendiente explicito la prueba directa de API EIPD entre cuentas/organizaciones.

## 2026-10-10 — M3-T1 §163: motivos documentales legibles

Consulta interna V3 agrupa motivos por etapa con titulos en español, explica codigos
frecuentes e identifica campo/pregunta. Deduplicacion solo visual por etapa, campo,
codigo, categoria y pregunta; conserva cantidad de ocurrencias y total informado.
Motivos con campos o preguntas distintos permanecen separados. Detalle desplegable
conserva codigo/campo/categoria/etapa/pregunta exactos para trazabilidad. Codigos
no reconocidos muestran aviso neutral y detalle, sin inventar requisitos legales.

Sin cambios de API, reglas, autoridad, metadata, permisos, escrituras ni migraciones.
Nuevas etiquetas no resuelven pendientes ni habilitan confirmacion/activacion.
Validacion: 5 interacciones Chromium aprobadas (2.6 s), tipos y lint frontend aprobados.
Caso agregado verifica campos distintos, duplicados con cantidad, preguntas y codigo
desconocido conservado. Callbacks sinteticos; presentacion en expediente local con
sesion personal pendiente de inspeccion manual. Backend y cliente sin cambios;
regresiones anteriores no repetidas. M3-T1 EN PROGRESO; fuentes/aceptacion pendientes.
Proximo: inspeccion visual de motivos en el expediente de prueba, manteniendo pendiente
la prueba directa de API EIPD entre cuentas/organizaciones.

Inspeccion manual posterior con sesion autorizada y expediente ficticio: usuario
confirmo mediante capturas las etapas, campos y tres tarjetas; el desplegable de
justificacion mostro codigo justificacion_ausente, campo justification, categoria
incompleto y etapa state. Continuar mantuvo pendientes; las decisiones negativas
mostraron requisitos documentales cumplidos sin conceder autoridad ni confirmar.
Pendiente ampliar traducciones de campos que conservan etiquetas inglesas como
exclusive_use; no se considera completada toda la localizacion.
