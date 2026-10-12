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

## 2026-10-10 — M3-T1 §164: etiquetas de campos en español

Ampliado el catalogo visual para campos de investigacion, documento EIPD, contexto,
base ordinaria y regimenes especiales. Uso exclusivo, controles, calidad, medidas,
publicacion, anonimizacion, conservacion y analisis documentales muestran etiquetas
en español. Identificadores originales conservados en detalle; campos desconocidos
mantienen fallback existente. No se declara localizacion completa de todo contrato.
Sin cambios de reglas, API, agrupacion, conteo, autoridad ni datos persistidos.
Tipos y lint frontend aprobados; no nuevas pruebas que reproduzcan traducciones.
Pruebas de interaccion §163 sin cambios y no repetidas. Inspeccion manual de nuevas
etiquetas pendiente. M3-T1 EN PROGRESO; fuentes/aceptacion, confirmacion/activacion
siguen pendientes/bloqueadas. Prueba directa de API EIPD entre cuentas pendiente.
Proximo: verificar etiquetas de investigacion en expediente ficticio local.

Inspeccion manual posterior mediante captura del usuario: Uso exclusivo para la
finalidad de investigacion y Controles de uso exclusivo visibles en español;
detalle conserva codigo, campo, categoria y etapa originales. Permanecen etiquetas
sin traducir en rutas de interes legitimo: conclusion, balancing_summary, decision.
Pendiente completar esas etiquetas y otras rutas; no se afirma localizacion total.

## 2026-10-10 — M3-T1 §165: etiquetas de interes legitimo

Catalogo visual ampliado para las secciones y campos de LIA v1: finalidad/interes,
necesidad, naturaleza/alcance, expectativas, impacto, salvaguardas, transparencia/
oposicion y conclusion. Rutas observadas conclusion/balancing_summary/decision
muestran Conclusion/Resumen de ponderacion/Decision en español. Respuestas y
comentarios tambien etiquetados. Detalle conserva identificadores originales.
Sin cambios de contratos, reglas, permisos, API ni datos. Campos desconocidos
mantienen fallback; no se declara localizacion completa de todos los regimenes.
Tipos y lint frontend aprobados. Sin pruebas nuevas que repliquen traducciones;
interacciones §163 sin cambios y no repetidas. Inspeccion visual pendiente.
M3-T1 EN PROGRESO; fuentes/aceptacion pendientes, confirmacion/activacion bloqueadas.
Proximo: revisar rutas LIA en expediente ficticio. Prueba directa API entre cuentas
permanece pendiente; rechazos de pagina/RAT no sustituyen ese control EIPD.

## 2026-10-10 — M3-T1 §166: diagnostico visible en español

Por solicitud explicita del usuario, el detalle presenta campo, categoria, etapa,
pregunta y motivo en español. Reemplaza identificadores crudos visibles por etiquetas;
Codigo pasa a Motivo. Datos originales del contrato y agrupacion siguen intactos
internamente; la pantalla ya no ofrece el detalle de identificadores tecnicos crudos.
Campos/preguntas desconocidos muestran etiquetas neutrales en español; no se infiere
traduccion ni requisitos legales. Indices numericos se muestran como elementos.
Se revisaron segmentos de los motivos del expediente ficticio mediante consulta
solo lectura y se agregaron etiquetas faltantes de fuentes, habilitacion, politicas,
condiciones y preguntas de deteccion. No se modifican datos ni contratos backend.

Tipos/lint frontend aprobados, 5 interacciones Chromium aprobadas en 2.3 s tras
actualizar expectativas de detalle; callbacks sinteticos. Inspeccion manual final
pendiente. La interfaz no habilita nuevas decisiones, confirmacion o activacion.
M3-T1 EN PROGRESO; fuentes/aceptacion y API entre cuentas siguen pendientes.
Proximo: comprobar detalle de diagnostico en español con expediente ficticio local.

## 2026-10-10 — M3-T1 §167: comprobacion visual del detalle en español

Captura del usuario con sesion autorizada y expediente ficticio confirma que el
motivo de justificacion muestra Motivo, Campo Justificacion, Categoria Incompleto
y Etapa Estado de la evaluacion en español. No aparecen identificadores ingleses
en ese detalle. Tarjetas negativas mantienen requisitos documentales cumplidos;
Continuar muestra pendientes y la confirmacion de investigacion permanece bloqueada.
La captura valida ese detalle y las etiquetas visibles, no todos los motivos de
otros expedientes ni una localizacion exhaustiva de todas las rutas.

Solo documentacion; sin codigo, migraciones ni datos nuevos. Tipos/lint y cinco
interacciones aprobados en §166 no repetidos. M3-T1 EN PROGRESO; fuentes/aceptacion
pendientes y confirmacion/activacion bloqueadas. Prueba directa API entre cuentas
permanece pendiente; pruebas de pagina y RAT no la sustituyen.
Proximo: revisar presentacion del volumen de motivos y pendientes funcionales del
expediente, manteniendo explicita la prueba de API entre cuentas aun no ejecutada.

## 2026-10-10 — M3-T1 §168: navegacion por temas de motivos

Etapas de motivos se muestran en desplegables nativos details/summary, cerrados
inicialmente, con cantidad de motivos distintos por tema. Total de ocurrencias
informadas permanece visible; deduplicacion exacta y cantidades no se modifican.
Textos e identificacion de campos/detalles en español conservados. Todos los motivos
siguen disponibles al abrir el tema, sin paginacion, truncamiento o nuevas consultas.

Seis interacciones Chromium aprobadas en 2.5 s, incluyendo abrir/cerrar/reabrir por
teclado sin otra peticion y grupos con duplicados/campos distintos. Tipos/lint
aprobados. Callbacks sinteticos; inspeccion manual de temas en expediente pendiente.
Sin reglas, contratos, permisos, escrituras, backend ni migraciones. M3-T1 EN PROGRESO;
confirmacion/activacion bloqueadas y fuentes/aceptacion pendientes. Prueba directa
API EIPD entre cuentas pendiente. Proximo: revisar desplegables en expediente ficticio.

## 2026-10-10 — M3-T1 §169: amplitud y jerarquia del detalle

A solicitud del usuario tras captura con columnas estrechas, decisiones se muestran
apiladas a ancho completo, eliminando el estiramiento de tarjetas sin motivos.
Temas con fondo diferenciado; motivos individuales en bloques con espacio y borde.
Detalle muestra etiquetas destacadas y valores en dos columnas desde sm; en ancho
pequeño se apilan. min-width y ruptura de palabras permiten rutas largas. Mantiene
desplegables por tema de §168, conteos, contenido, español y navegacion por teclado.

Validacion: tipos/lint aprobados y 6 interacciones Chromium aprobadas en 2.8 s.
Interacciones usan callbacks sinteticos, no validan pixeles ni CSS real de la pagina;
inspeccion visual final del nuevo diseño en sesion personal pendiente. Captura previa
confirma que los desplegables de §168 abren tema/detalle, pero motivo de esta mejora
fue el ancho insuficiente. Sin contratos, backend, reglas, autoridad ni escrituras.
M3-T1 EN PROGRESO; confirmacion/activacion bloqueadas y fuentes/aceptacion pendientes.
Prueba directa API EIPD entre cuentas pendiente. Proximo: inspeccionar ancho y detalle
del expediente ficticio en pantalla antes de cerrar validacion visual.

Inspeccion manual posterior: captura del usuario confirma ancho ampliado, bloques
separados y alineacion etiqueta/valor en detalles abiertos de justificacion e
investigacion; motivos, categoria y etapa visibles en español. Captura muestra
conteos por tema (Estado: 1, Investigacion: 65 motivos distintos) y total de 256
ocurrencias. Valida estos bloques en escritorio; vista movil y otros temas no
inspeccionados exhaustivamente. Confirmacion de investigacion sigue bloqueada.

## 2026-10-10 — M3-T1 §170: historia preservada tras cambio documental

Ensayo autorizado sobre datos ficticios locales: se cambio el analisis de conservacion
del material de investigacion mediante servicio de dominio/runtime restringido.
Comparacion de salida del evento antes/despues confirma igualdad completa, sin nuevas
revisiones. RAT vigente; readiness indica review_context_metadata_status obsoleta.
El usuario verifico por captura el mismo evento con decision, fundamento, referencia,
fecha y politica historicos. Consulta de requisitos muestra identidad auditable no
disponible para nueva revision: se conserva la vinculacion previa del documento EIPD,
no se repara silenciosamente al cambiar investigacion. Pantalla actual no expone
estado de vigencia del evento; ese estado se comprobo en servicio, no por captura.

Capturas adicionales confirman detalle amplio y ruta de Controles de uso exclusivo
en español. Se corrigio etiqueta faltante context_metadata por Identidad auditable
del material de revision; contrato y motivo sin cambios. Datos ficticios no se versionan.
M3-T1 EN PROGRESO; confirmacion/activacion bloqueadas, fuentes/aceptacion y prueba
API entre cuentas pendientes. Proximo: revincular explicitamente el documento ficticio
tras su revision, conservando el evento anterior, y verificar diagnostico actualizado.

## 2026-10-10 — M3-T1 §171: revinculacion documental explicita de prueba

Tras el cambio ficticio de conservacion de §170, se reviso/reaporto el documento EIPD
como PRUEBA-2 mediante servicio de dominio y rol runtime restringido. El servidor
vinculo el documento al contexto V2 actual; no se edito metadata manualmente.
Comparacion del evento historico antes/despues confirma igualdad completa. Su
asociacion al contexto anterior permanece obsoleta en readiness; no se transforma
una revision antigua en aprobacion del material nuevo. No se registro nuevo evento.

Servicio comprobo requisitos_met true y metadata disponible para ambas decisiones
negativas, y false para continuar. Captura del usuario confirma identidad del material
actual disponible, requisitos documentales cumplidos para requiere_cambios/no_continuar,
y continuar pendiente con 252 ocurrencias. No acredita expediente completo ni permiso.
Cambios ficticios solo en base local; sin codigo, migraciones ni nuevas pruebas
automatizadas. Validacion de servicio y pantalla; checks previos no repetidos.
M3-T1 EN PROGRESO; confirmacion/activacion bloqueadas y fuentes/aceptacion pendientes.
API EIPD entre cuentas sigue pendiente. Proximo: comprobar registro de otra revision
negativa sobre el material nuevo, conservando la anterior y su orden historico.

## 2026-10-10 — M3-T1 §172: segunda revision negativa independiente

Ensayo sobre expediente ficticio PRUEBA-2: servicio de dominio/runtime restringido
registro no_continuar con fundamento y referencia de prueba distintos. Comprobacion
transaccional: conteo aumento exactamente en uno; salida completa del evento anterior
permanece identica. Metadata de ultima revision vigente en readiness; representa
identidad documental, no aprobacion ni permiso. No confirmacion ni activacion.

Capturas del usuario: consulta del evento nuevo muestra No continuar, referencia
PRUEBA-REVISION-PRUEBA2-20261010 y fundamento sobre PRUEBA-2. Al consultar el evento
anterior reaparecen Requiere cambios, referencia original, fundamento y fecha intactos.
Ambos eventos se consultan por separado; no hay sobrescritura historica.
Datos ficticios solo en base local; sin codigo, migraciones o nuevos tests automatizados.
Validacion de servicio y sesion personal; checks previos no repetidos.
M3-T1 EN PROGRESO; fuentes/aceptacion pendientes; confirmacion/activacion bloqueadas.
API EIPD entre cuentas sigue pendiente. Proximo: hacer visible el estado de vigencia
documental de la ultima revision en consulta de requisitos, separado de historia y
preparacion para nuevas decisiones, sin inferir autoridad ni actualizar eventos.

## 2026-10-10 — M3-T1 §173: estado documental de ultima revision visible

Cliente de preparacion proyecta review_context_metadata_status existente del servidor
como latest_review_context_status: sin_revision/sin_metadatos/vigente/obsoleta, null
fuera de V3. Valida enum cerrado; no infiere estado ni calcula identidad en frontend.
Pantalla de requisitos muestra Vínculo de la última revisión con el material actual,
separado de requisitos por decision. Explica que identidad vigente no aprueba ni
autoriza continuar/confirmar/activar; estado siempre de ultima revision, no del evento
historico seleccionado. Consulta historica limpia este bloque y conserva su aviso.

Validacion: 12 pruebas cliente aprobadas (543 ms), 7 interacciones Chromium (3.2 s),
tipos/lint aprobados. Casos nuevos cubren cuatro estados, null fuera de V3, enum
invalido rechazado y alternancia requisitos/historia sin mezclar estado. Fetch/callbacks
sinteticos. Captura del usuario confirma vinculo vigente, aviso sin autoridad y Continuar
con requisitos pendientes (252 motivos); el campo de evento anterior permanece visible,
sin atribuirle el estado de ultima revision. Segunda captura confirma consulta del evento
anterior: Requiere cambios, referencia PRUEBA-REVISION-LECTURA-20261010, fundamento
y fecha originales; conserva aviso historico y no muestra bloque de vinculo actual.
Backend, contratos persistidos,
permisos y datos sin cambios. M3-T1 EN PROGRESO; fuentes/aceptacion y API entre cuentas
pendientes; confirmacion/activacion bloqueadas. Alternancia manual requisitos/historia comprobada en escritorio; otros estados solo
cubiertos por pruebas sinteticas. Prueba directa API entre cuentas sigue pendiente.

## 2026-10-12 — M3-T1 §174: comprobacion visual a ancho reducido

Dos capturas del usuario sobre el expediente ficticio: vista general y tema
Investigacion con primer detalle abierto. En el ancho mostrado, tarjetas y textos
visibles permanecen dentro del contenido; etiquetas y valores del detalle se apilan
en una columna. Motivo, Campo, Categoria y Etapa legibles; texto largo del campo de
uso exclusivo ajusta lineas. Sin recortes aparentes en el area capturada.

Evidencia visual parcial de escritorio a ancho reducido, no ensayo en dispositivo
movil ni medicion automatizada de overflow. Otros temas, anchuras y estados reales
siguen pendientes. Sin cambios de codigo, datos, permisos o decisiones; no se repiten
pruebas automatizadas porque solo se registra evidencia. M3-T1 EN PROGRESO;
fuentes/aceptacion y API entre cuentas pendientes; confirmacion/activacion bloqueadas.

## 2026-10-12 — M3-T1 §175: vista emulada de 390 pixeles

Captura del usuario en Edge DevTools, Responsive 390 x 749: Investigacion abierta
con detalle de confirmacion bloqueada. Motivo, Campo, Categoria y Etapa se apilan;
textos visibles ajustan lineas dentro de las tarjetas, sin recortes aparentes.
Tambien visible el motivo de evidencia ausente y su control de detalle cerrado.

Validacion visual del area capturada en emulacion, no dispositivo fisico ni medicion
de scrollWidth/clientWidth. No acredita ausencia de overflow en toda la pagina ni
cobertura de formularios, otros temas o anchuras. Contadores de DevTools visibles
sin mensajes de consola: no permiten determinar causa o impacto de errores.
Sin cambios de codigo, datos o permisos; no se repiten tests por registro documental.
M3-T1 EN PROGRESO; fuentes/aceptacion, API entre cuentas y cobertura restante
pendientes; confirmacion/activacion bloqueadas.

## 2026-10-12 — M3-T1 §176: medicion de desbordamiento a 390 pixeles

Captura del usuario en Edge Responsive 390 x 749, Investigacion y detalle abiertos:
expresion document.documentElement.scrollWidth > document.documentElement.clientWidth
retorna false. El elemento raiz no presenta ancho de contenido superior al visible
en ese estado. Complementa comprobacion visual de §175; no acredita otros estados,
anchuras, overflow interno de cada elemento o dispositivo fisico.

Sin cambios de codigo, datos ni permisos. Registro documental; tests no repetidos.
M3-T1 EN PROGRESO; fuentes/aceptacion y API entre cuentas pendientes;
confirmacion/activacion bloqueadas.

## 2026-10-12 — M3-T1 §177: cabecera administrativa adaptable

Capturas del formulario a 390 pixeles muestran campos y botones dentro del ancho;
no verifican accion de botones. Cabecera anterior comprime titulo en tres lineas.
Se apilan titulo, correo y cierre de sesion bajo breakpoint sm; a mayor ancho se
conserva fila. Correo largo puede partirse sin ensanchar contenido. Autorizacion,
sesion y componente de cierre sin cambios. Tipos y lint aprobados; ajuste de clases
visual sin nuevas pruebas automatizadas. Captura posterior Edge Responsive 390 x 749
confirma titulo en una linea, correo debajo y cierre separado, sin recortes visibles
en cabecera. Accion de cierre y otros anchos no comprobados por esta captura.
M3-T1 EN PROGRESO; confirmacion/activacion bloqueadas.
