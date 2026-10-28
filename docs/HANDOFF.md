# Handoff vigente de CumpleIA

## Publicación autorizada de 9A — 28/10/2026

Usuario solicita commit y autoriza push de `feature/navegacion-9a-pendientes`, base
`a1c93c1`. Incluye unidades pendientes, estados UI, panel consultable, pruebas y
validación asistida acordada. 190 escenarios Chromium y checks estáticos previamente
aprobados; los últimos cambios solo registran los resultados asistidos y esta autorización.
No atribuir CI remota ni integración real a las pruebas con fixtures. Sin merge/despliegue,
9B no iniciado y lector manual de 7B pendiente. Excluir next-env.d.ts generado y outputs/.
Las entradas inferiores de autorización pendiente son antecedentes. Verificar identidad
remota después del push.

## 9A — recorridos asistidos acordados completados, 28/10/2026

Usuario confirma recuperación tras Offline con dos pendientes conservados y sin falso
guardado; capturas distinguen error de conexión de consulta completada. Se suma al
conteo/contexto, guardado parcial y panel estrecho ya confirmados.
[Resultado y límites](project/navegacion-servidor.md#9a--recuperación-confirmada-y-recorridos-acordados-completados-28102026).
190 escenarios automatizados aprobados en el alcance documentado. Listo para commit/push
cuando se autorice; sin publicación de 9A ni inicio de 9B. Lector manual de 7B pendiente.
Las entradas inferiores de aceptación pendiente son antecedentes.

## 9A — panel estrecho confirmado OK, 28/10/2026

Usuario confirma lectura completa, Escape y cierre exterior con retorno del foco a
Ver pendientes (1), sin guardar ni recargar.
[Registro y siguiente comprobación](project/navegacion-servidor.md#9a--panel-estrecho-y-cierre-confirmados-28102026).
Pendiente recuperación de consulta con ambos borradores conservados. Sin commit/push
de 9A ni inicio de 9B; lector manual de 7B pendiente.

## 9A — guardado parcial confirmado OK, 28/10/2026

Usuario confirma que guardar solo la determinación deja un pendiente EIPD y conserva
su nota, sin guardar ese borrador ni recargar.
[Registro y siguiente comprobación](project/navegacion-servidor.md#9a--guardado-parcial-y-nota-conservada-confirmados-28102026).
Pendientes cierre/foco en ventana estrecha y recuperación de consulta. Sin commit/push
de 9A ni inicio de 9B; lector manual de 7B pendiente.

## 9A — primer recorrido asistido OK, 28/10/2026

Usuario confirma conteo de dos unidades identificadas: determinación y un solo borrador
EIPD para sus siete pasos, con contexto correcto en la captura.
[Registro y siguiente comprobación](project/navegacion-servidor.md#9a--conteo-e-identificación-confirmados-28102026).
Pendiente guardar solo la determinación y comprobar conservación de EIPD; restantes
recorridos de 9A siguen abiertos. Sin publicación de 9A ni inicio de 9B.

## 9A implementado localmente — 28/10/2026

Rama `feature/navegacion-9a-pendientes`, base 8B `a1c93c1`. Ver pendientes (N)
identifica formularios y preparación temporal con contexto; siete pasos EIPD cuentan
una sola unidad. Estados UI distinguen lectura y escritura; guardado parcial y error
conservan los demás pendientes. Sin autosave/almacenamiento nuevo, navegación de 9B,
cambios API ni habilitación EIPD. 190 Chromium con fixtures y checks estáticos aprobados.
[Alcance, evidencia y checklist asistido](project/navegacion-servidor.md#bloque-9a--pendientes-identificables-28102026).
Pendiente aceptación asistida; sin commit/push autorizado de 9A, merge o despliegue.
Lector manual de 7B pendiente. Excluir next-env.d.ts generado y outputs/.
Las entradas inferiores describen antecedentes; lote 9 ahora sí está iniciado.

## Publicación autorizada de 8B — 27/10/2026

Usuario solicita commit y autoriza push de `feature/navegacion-8b-pasos`, base `e04d8d8`.
Incluye navegación principal EIPD, título/Paso N de 7, Anterior/Siguiente, foco al cambiar
ancho, pruebas y aceptación asistida. Evidencia: 111 escenarios de regresión más cinco de
repetición aprobados en ejecuciones separadas; tipos/lint/formato y capturas aprobados.
Lector manual de 7B pendiente. No atribuir CI remota nueva al push.
Las menciones inferiores de autorización pendiente son antecedentes. Excluir next-env.d.ts
generado y outputs/ locales. Lote 9 no iniciado; sin merge/despliegue. Verificar HEAD remoto.

## 8B — recorridos asistidos completados, 27/10/2026

Usuario confirma el último recorrido móvil, nota conservada y cierre exterior/foco.
8B aceptado en el alcance acordado, incluidos zoom 200 %, Escape repetido, ampliación y
Atrás/Adelante. [Evidencia y límites](project/navegacion-servidor.md#8b--recorridos-asistidos-completados-27102026).
111 escenarios de regresión + cinco nuevos de repetición aprobados en ejecuciones separadas.
Listo para commit/push cuando se autorice; lote 9 no iniciado. Lector manual de 7B pendiente.
Las entradas inferiores de validación pendiente son antecedentes del proceso.

## 8B — Atrás/Adelante y nota conservada OK, 27/10/2026

Usuario confirma regreso al Paso 4 con Atrás, retorno al Paso 5 con Adelante y nota
conservada en Describir riesgos, sin guardar ni recargar.
[Resultado y remanente asistido](project/navegacion-servidor.md#8b--atrásadelante-y-conservación-confirmados-27102026).
Pendiente secuencia móvil de tres destinos y cierre exterior; sin publicación de 8B.

## 8B — ampliación y foco confirmados OK, 27/10/2026

Usuario confirma cierre de Secciones al maximizar la pestaña actualizada y foco en la
barra visible. Zoom 200 % y Escape repetido previamente confirmados.
[Registro y siguiente prueba](project/navegacion-servidor.md#8b--ampliación-y-foco-en-barra-confirmados-27102026).
Pendiente Atrás/Adelante con conservación de nota; sin commit/push de 8B ni lote 9.

## 8B — zoom del navegador 200 % OK, 27/10/2026

Usuario confirma lectura/selección de pasos mediante Secciones con zoom real 200 %, sin
recortes ni desplazamiento horizontal de página, y retorno a 100 %.
[Registro y límites](project/navegacion-servidor.md#8b--zoom-real-200--confirmado-27102026).
Pendientes ampliación/foco y Atrás/Adelante; sin commit/push de 8B ni inicio de lote 9.

## 8B — Escape repetido confirmado OK, 27/10/2026

Usuario confirma apertura/cierre repetidos de Secciones sin elegir destino, con Escape
y foco de retorno. Caso anterior aclarado: el panel cerrado no consume Escape como
atajo global. [Registro y pendientes](project/navegacion-servidor.md#8b--cierre-repetido-de-secciones-confirmado-27102026).
Continúan pendientes zoom real 200 %, ampliación/foco y navegación histórica; sin publicación de 8B.

## 8B — Escape con panel cerrado aclarado, 27/10/2026

Captura muestra el formulario sin Secciones abierto: Escape no es un atajo global al
botón. No se reproduce fallo de cierre de un panel abierto. Pendiente repetir apertura
→ Escape sin elegir destino y confirmar; zoom real 200 % también pendiente.
[Detalle](project/navegacion-servidor.md#8b--aclaración-de-escape-mediante-captura-27102026).
Sin cambios adicionales de producto ni publicación de 8B.

## 8B — secuencia y conservación de nota OK, 27/10/2026

Usuario confirma Describir riesgos → Valorar riesgos → Medidas de mitigación,
Pasos 3/4/5 y nota conservada al volver sin guardar ni recargar.
[Registro y pendientes](project/navegacion-servidor.md#8b--secuencia-y-borrador-confirmados-27102026).
Continúan pendientes las comprobaciones de ventana estrecha, zoom y navegación histórica.
Sin commit/push de 8B ni inicio de lote 9.

## 8B — primer recorrido asistido OK, 27/10/2026

Usuario confirma Describir riesgos, Paso 3 de 7 y ausencia de lista central repetida
en ventana amplia. Continúan pendientes los siguientes recorridos del guion 8B;
[registro y límites](project/navegacion-servidor.md#8b--primera-comprobación-asistida-confirmada-27102026).
Sin commit/push de 8B ni inicio de lote 9.

## Bloque 8B implementado localmente — 27/10/2026

Rama `feature/navegacion-8b-pasos` sobre 8A publicado `e04d8d8`. Navegación EIPD conectada
sin lista central repetida; título/Paso N de 7 y Anterior/Siguiente después del formulario.
Barra desde 1200 px, panel Secciones por debajo; foco conservado al cambiar de ancho.
Editor independiente conserva su navegación. 111 Chromium (91 conectados + 20 independientes),
tipos/lint/formato y capturas aprobados. [Alcance y guion](project/navegacion-servidor.md#bloque-8b--navegación-principal-y-paso-actual-27102026).
Pendiente validación asistida, incluido zoom real 200 %. Lector manual de 7B pendiente.
Sin commit/push de 8B ni inicio de lote 9. Excluir next-env.d.ts generado y outputs/ locales.
Esta entrada actualiza las menciones anteriores de 8B no iniciado.

## Publicación autorizada de 8A — 27/10/2026

Usuario solicita commit y autoriza push en `feature/navegacion-8a-contexto`, base `15aa273`.
Se publica el contexto compacto y su detalle accesible, conservación de la cabecera
independiente, pruebas y resultados asistidos de 8A. 104 Chromium aprobados y checks
estáticos previos aprobados; no atribuir CI remota al push. Lector manual de 7B pendiente.
Las entradas inferiores de autorización pendiente describen estados anteriores.
Excluir `frontend/next-env.d.ts` generado y `outputs/` locales. 8B no iniciado;
sin merge ni despliegue. Verificar identidad del commit remoto tras publicar.

## 8A — recorridos asistidos completados, 27/10/2026

Usuario confirma ámbito organizacional en Mi organización/Autodiagnóstico y retorno a
Bases de licitud con su selección recuperada. Sumado a los recorridos anteriores y captura
histórica, 8A queda aceptado en ese alcance. Ganancia de espacio respaldada por mediciones
locales; 104 Chromium y comprobaciones estáticas previas aprobados.
[Resultado y límites](project/navegacion-servidor.md#8a--recorridos-asistidos-completados-27102026).
Listo para cierre Git cuando sea autorizado; sin commit/push de 8A ni inicio de 8B.
Lector manual de 7B pendiente. Las entradas inferiores describen estados anteriores.

## 8A — identidad histórica comprobada en captura, 27/10/2026

Cabecera de evaluación versión 1/borrador separada de resolución 1, referencia
SIMULADA-PILOTO-INFANCIA-RES-001 y edición PRUEBA-1 en Documentos guardados.
Evidencia visual añadida al [registro de 8A](project/navegacion-servidor.md#8a--evidencia-de-identidad-histórica-27102026).
No se registraron actuaciones. Conserva los límites de validación documentados;
sin nueva autorización de commit/push ni inicio de 8B.

## 8A — contexto por módulo confirmado, 27/10/2026

El usuario confirma «recorrido OK» al comprobar Ver contexto completo en Inventario
(organización/tratamiento), Panel principal (solo organización) y retorno a Bases de
licitud (finalidad/evaluación y texto pendiente conservados), sin recargar ni guardar.
Este resultado se suma a las comprobaciones asistidas previas del detalle y ventana estrecha.
Queda por comprobar la distinción entre evaluación activa y documento histórico consultado;
Mi organización/Autodiagnóstico conservan cobertura automatizada, sin atribuirles ahora una
prueba asistida adicional. Lector manual de 7B pendiente. Sin nueva autorización de
commit/push ni inicio de 8B.

## 8A — ventana estrecha confirmada, 27/10/2026

Usuario confirma «recorrido OK» tras reducir el ancho sin recargar, abrir Ver contexto
completo, leer sus datos con desplazamiento si es necesario y cerrar sobre el fondo gris
exterior al panel, con foco de retorno y texto del formulario conservado.
Se acepta este recorrido acotado; siguen pendientes ámbito por módulo e identidad histórica.
No atribuir prueba manual con lector de pantalla ni cierre completo de 8A.
Sin autorización nueva de commit/push; 8B no iniciado.

## 8A — primera comprobación asistida OK, 27/10/2026

El usuario confirma «prueba OK» tras el guion de abrir Ver contexto completo en Bases de
licitud, comprobar la selección y cerrar con Escape con retorno del foco y conservación del
formulario. Se registra aceptación de este recorrido, no del conjunto completo de 8A.
Pendientes: detalle en ventana estrecha/nombres largos y cierre exterior, ámbitos por módulo
y distinción frente al documento histórico. [Guion y evidencia](project/navegacion-servidor.md#bloque-8a--contexto-compacto-implementado-27102026).
Sin nueva autorización de commit/push; 8B no iniciado. Lector manual de 7B sigue pendiente.

## Bloque 8A implementado localmente — 27/10/2026

Rama `feature/navegacion-8a-contexto` sobre 7B publicado `15aa273`.
Cabecera compacta con detalle completo accesible; contexto por módulo; retirada del resumen
repetido solo en recorrido conectado. Formularios independientes y documento histórico conservados.
104 Chromium aprobados (84 conectados + 20 independientes), tipos/lint/formato y capturas
comparables; evidencia y [guion asistido 8A](project/navegacion-servidor.md#bloque-8a--contexto-compacto-implementado-27102026).
Pendiente validación del usuario; sin commit/push ni inicio de 8B. Lector de pantalla de 7B
sigue pendiente. Excluir `frontend/next-env.d.ts` generado y `outputs/` locales.
Las entradas inferiores de «sin inicio de 8A» describen estados anteriores.

## Publicación autorizada de 7B — 27/10/2026

Usuario solicita commit y autoriza push de 7B en feature/navegacion-7b-accesibilidad,
base 39bca0b. Publicar estructura/nombres/ayudas, pruebas y validación asistida acotada.
La prueba manual con lector de pantalla permanece pendiente por no disponibilidad del
usuario; publicar no cierra ese criterio ni acredita accesibilidad integral certificada.
168 escenarios aprobados y 1 captura opcional omitida según ejecución registrada;
no atribuir CI remota nueva al push. Los pendientes inferiores de autorización describen
estados anteriores. Excluir next-env.d.ts generado y outputs/ locales; verificar HEAD
remoto tras publicar. No iniciar 8A ni ejecutar merge/despliegue en este cierre.

## 7B — recorridos visuales y de teclado confirmados, 27/10/2026

Usuario aporta secuencia de Determinar aplicabilidad a Documentos guardados con título
de pestaña actualizado; confirma «recorrido OK» al abrir/cerrar Secciones y Contexto
con retorno del foco; confirma contorno de foco en Consultar última determinación guardada.
Capturas muestran ayuda de consulta y explicación de Nombre de la edición en preparación
de infancia. Confirma «recorrido OK» al abrir y cerrar Análisis, riesgos, medidas, fuentes
y evidencias con Enter, manteniendo foco. Es aceptación de esos recorridos, sin registrar
nuevos documentos ni actuaciones durante el guion.

Usuario informa que no dispone de Narrador/NVDA. La prueba manual con lector de pantalla
no se ejecutó y permanece pendiente, junto con cualquier comprobación asistida no cubierta.
La verificación estructural de main único, nombres, relaciones e IDs sigue respaldada por
fixtures automatizados; una captura visual no acredita su anuncio por lector. Tampoco se
atribuye al usuario prueba táctil real, comprobada solo mediante emulación.

168 pruebas aprobadas y 1 captura opcional omitida, según evidencia previa. 7B validado
parcialmente con este alcance; no dar por completado su criterio de lector ni declarar
accesibilidad certificada. Sin commit/push de 7B ni inicio de 8A. Rama
feature/navegacion-7b-accesibilidad sobre 39bca0b. Excluir generados y capturas locales.
Las menciones inferiores de aceptación asistida totalmente pendiente son antecedentes;
queda pendiente específicamente la parte no comprobada indicada aquí.

## Bloque 7B implementado localmente — 27/10/2026

Usuario solicita continuar 7B; rama feature/navegacion-7b-accesibilidad sobre 39bca0b.
Main conectado único/nominado, menú conectado con nombre correcto, título por destino,
relaciones de diálogos, regiones documentales sin pestañas ocultas e IDs por evaluación.
Ayudas asociadas y bloqueo EIPD por causa real, preservando usos independientes y 7A.
168 pruebas aprobadas (6 nuevas 7B); 1 captura opcional omitida, tipos/lint/formato correctos.
Capturas 1280/390 revisadas. Pruebas controladas; no certificación ni prueba con lector.
[Guion y límites](project/navegacion-servidor.md#bloque-7b--nombres-regiones-y-ayudas-accesibles).
Pendientes validación asistida y lector de pantalla; sin commit/push ni inicio de 8A.
Excluir next-env.d.ts generado y outputs/ locales. Entradas inferiores son antecedentes.

## Publicación autorizada de 7A — 27/10/2026

Usuario solicita commit y autoriza push de 7A aceptado, en feature/navegacion-7a-teclado
sobre 8fec3df. Se reúne navegación de teclado, manejo explícito de Espacio, regresiones
y aceptación asistida acotada. Los pendientes de publicación inferiores son antecedentes
anteriores a esta autorización. Mantener los límites de evidencia: pasada completa de 67
antes del último ajuste y siete escenarios dirigidos después, sin atribuir CI remota.
Excluir next-env.d.ts generado y outputs/ locales. Comprobar HEAD remoto tras el push.
No iniciar 7B ni ejecutar merge/despliegue en este cierre.

## Aceptación asistida acotada de 7A — 27/10/2026

Usuario confirma «Todo funciona OPK» tras comprender que el clic exterior se hace sobre
el fondo gris y no dentro del panel azul. Aceptados los recorridos informados: primera
secuencia Enter/Tab/Escape; apertura/cierre con Espacio en pestaña nueva con código
actualizado; avance al siguiente grupo y selección de destino («Todo el recorrido OK»);
y prueba estrecha de Menú/Secciones, Escape y clic interior/exterior tras aclaración.
El usuario también comprobó que la pestaña antigua conserva su preparación de infancia;
la nueva empieza vacía por ser temporal por pestaña, sin registro ni sincronización.
Esto no acredita copia de borradores entre ventanas ni guardado de una nueva versión.

7A aceptado con este alcance asistido. Retención completa de Tab/Shift+Tab, cambio de
tamaño con foco y ausencia de escrituras siguen respaldados por escenarios controlados,
sin atribuir pruebas manuales adicionales. No equivale a certificación de accesibilidad
ni cierra 7B o NAV-UX-006 globalmente. Evidencia automatizada: pasada completa inicial
de 67; tras ajuste explícito de Espacio pasaron 7 escenarios dirigidos, tipos y lint.
No se declara una pasada completa posterior de 68 escenarios.

Rama feature/navegacion-7a-teclado sobre 8fec3df. Sin commit/push de 7A; requiere
indicación del usuario para publicar. Próximo propuesto: 7B, estructura y ayudas
accesibles, sin iniciar. Excluir next-env.d.ts generado y outputs/ locales.
Esta aceptación sustituye los pendientes asistidos anteriores solo con el alcance indicado.

## 7A — observación asistida de Espacio y corrección explícita, 27/10/2026

Usuario confirma la primera secuencia Enter/Tab/Escape («toda la secuencia OK»),
pero informa que presionar y soltar Espacio no abre/cierra Preparar. La prueba
Chromium controlada anterior sí activaba el summary nativo; no se atribuye una
reproducción exacta del navegador del usuario. Se reemplaza solo para Espacio la
activación implícita por manejo explícito en el summary conectado: cancelar acción
nativa, alternar una vez por pulsación e ignorar repetición al mantener la tecla.
Enter mantiene su acción nativa; Tab, Escape y foco conservan sus comportamientos.

Siete escenarios dirigidos 7A aprobados tras el ajuste: los seis existentes y uno
nuevo que despacha eventos sin activación nativa y comprueba pulsación mantenida,
liberación, apertura/cierre real sin doble activación, mismo foco/URL y cero escrituras.
Tipos/lint/formato y diff --check correctos. La pasada completa de 67 escenarios
corresponde a antes de este ajuste; no se declara una nueva pasada completa de 68.
Pendiente repetir Espacio con el usuario y continuar aceptación de 7A. Sin commit/push.
No recargar su pestaña con borradores pendientes; para cargar código actualizado si
fuera necesario usar pestaña independiente con contexto propio.

## Bloque 7A implementado localmente — 27/10/2026

Usuario autoriza continuar 7A; rama feature/navegacion-7a-teclado sobre 8fec3df.
Corregidos dos problemas reproducidos de teclado en desplegables de escritorio:
coexistencia y permanencia al salir con Tab. Cierre sin robar foco, Escape localizado,
exclusión al abrir paneles y foco a Secciones al ocultarse navegación de escritorio.
Paneles compartidos, foco/scroll a trabajo y borradores conservados, sin cambios API/backend.
67 escenarios conectados (6 nuevos) aprobados; tipos/lint/formato y capturas revisados.
Pruebas controladas, no aceptación del usuario ni certificación de accesibilidad.
[Guion y evidencia](project/navegacion-servidor.md#bloque-7a--teclado-y-foco-en-navegación-conectada).
Pendiente validación asistida; sin commit/push ni inicio de 7B. Excluir generados/capturas.
Las entradas siguientes describen antecedentes anteriores.

## Cierre asistido y publicación autorizada de 6B — 27/10/2026

Usuario solicita commit y autoriza push al terminar las comprobaciones asistidas.
Rama `feature/navegacion-6b-operaciones`, base d9f859f. Se acepta con el alcance
observado y confirmado: nombres de edición y pasos EIPD, disponibilidad independiente
por tema, matriz alineada/coloreada, aviso ante reemplazo de preparación, cambio entre
revisión documental y decisión de organización («resultado OK»), conservación al volver
a preparación y regreso desde vista previa con referencia, PRUEBA-1 y notas intactas.
El usuario guardó expresamente una determinación ficticia de infancia Corresponde en
el programa con menores, manteniendo EIPD pendiente; capturas confirman su acceso.
Se encontraron dos versiones históricas; durante el guion no se solicitó registrar
otra ni emitir revisión/decisión. La vista previa mostró registro deshabilitado sin
revisión de contenido; volver mantuvo los campos. La preparación conservada no acredita
una copia nueva ni persistencia después de recargar. No atribuir esos ensayos al usuario.

171 escenarios automatizados distintos aprobados: 157 del bloque y 14 del formulario de
valoración (3 nuevos de matriz). Tipos/lint/formato correctos; capturas controladas de
1280/390/320 revisadas. Ausencia de registro, negativas, información insuficiente,
asociación por revisar y errores/carga conservan evidencia controlada, no nueva aceptación
manual. La prueba integrada API aislada no se ejecutó. Sin cambios backend ni reglas de
activación EIPD. NAV-UX-006 permanece abierto para los demás sublotes.

Este cierre sustituye los pendientes de aceptación asistida anteriores solo con ese
alcance. Commit/push autorizado para estos cambios y documentación; excluir next-env.d.ts
generado y outputs/ locales. No hacer merge/despliegue ni iniciar 7A en este cierre.
Siguiente bloque propuesto: 7A, teclado y foco, pendiente de indicación del usuario.

## Ajuste visual solicitado durante 6B — matriz Probabilidad / Impacto

26/10/2026. Usuario solicita alinear cabeceras y distinguir niveles por color.
Implementado en AssessmentSupportPanel: tabla de columnas fijas, títulos y valores
centrados, bordes visibles y cabeceras con scope de fila/columna. Bajo verde suave
(#dcfce7), Medio amarillo suave (#fef9c3), Alto naranja suave (#fed7aa), Muy alto rojo
suave (#fecaca), con texto oscuro (#0f172a), nombres explícitos y cabeceras neutras.
Contraste calculado texto/fondo: 16,26; 16,62; 13,19 y 12,34 a 1 respectivamente.
No se modifican valores de la matriz, metodología ni cálculo; el color es apoyo visual.
En ventana estrecha se conserva desplazamiento horizontal local con acceso por teclado.

14 escenarios del formulario aprobados, incluidos 3 de alineación/colores y dimensiones
1280/390/320; tipos y ESLint correctos. Capturas revisadas en outputs/matriz-6b (locales,
no publicar). Respuestas ficticias controladas; pendiente revisión visual por usuario en
Valorar riesgos → Metodología CUMPLEIA-CUALITATIVA-1 y criterios. Sin commit/push nuevo.

## Bloque 6B implementado localmente — 26/10/2026

Usuario solicita continuar 6B. Rama `feature/navegacion-6b-operaciones`, base publicada
`d9f859f9742cd013479e002536f366ad6573ca5a`. Operaciones documentales diferenciadas,
nombre libre de edición con ayuda, siete pasos EIPD alineados y razones de disponibilidad
por tema, sin acceso al editor bloqueado. Conservados contratos, históricos y borradores;
sin cambios backend ni activación EIPD. 157 escenarios distintos aprobados con fixtures,
tipos/lint/formato correctos y capturas escritorio/390/320 revisadas. No atribuir ensayo
integrado contra el servidor del usuario. Pendiente aceptación asistida según
[guion y evidencia](project/navegacion-servidor.md#bloque-6b--operaciones-documentales-y-disponibilidad).
Sin commit/push nuevo ni inicio de 7A. Excluir `frontend/next-env.d.ts` generado y `outputs/`.
Las entradas inferiores conservan antecedentes del cierre anterior.

## Publicación autorizada del bloque 6A — 26/10/2026

Usuario solicita commit y autoriza push del bloque 6A aceptado, en
feature/navegacion-6a-destinos sobre d42b2e9. Se reúnen implementación, regresiones,
legibilidad ajustada y aceptación asistida acotada. Las menciones inferiores de
publicación pendiente son antecedentes anteriores a esta autorización.
Excluir next-env.d.ts generado y outputs/ locales. Verificar HEAD remoto tras publicar;
no atribuir CI remota por el push. No iniciar 6B ni ejecutar merge/despliegue.

## Cierre asistido acotado 6A — 26/10/2026

Usuario confirma «esta OK la glosa» tras aumentar legibilidad de Revisar y decidir.
Aceptados los recorridos informados de acceso Documentos guardados/nombres, Historial con
Atrás/Adelante, conservación de nota EIPD y funcionamiento de Continuar, más este ajuste
visual. No atribuir a la captura estrecha antigua la comprobación de nombres nuevos;
320/390 conservan evidencia controlada, no nuevo ensayo asistido documentado.
6A aceptado con este alcance; no cierra NAV-UX-006 globalmente. [Detalle](project/navegacion-servidor.md#aceptación-asistida-del-rótulo-y-cierre-acotado-6a).
Cambios locales sobre d42b2e9, sin commit/push nuevo ni inicio de 6B. Próximo bloque
propuesto: 6B, pendiente de indicación. Los estados inferiores son antecedentes anteriores.

## Validación parcial 6A y legibilidad del grupo — 26/10/2026

Usuario confirma acceso/nombres Documentos guardados, Atrás/Adelante (3 OK), conservación
de nota EIPD y funcionamiento de Continuar. Observa que Revisar y decidir se lee demasiado
pequeño en escritorio. Ajuste acotado del rótulo: tamaño 1rem, negrita, color de texto
principal y espaciado; Documentos guardados conserva acceso directo y misma URL.
Captura estrecha aportada de Continuar aún muestra el nombre anterior Revisar documentos;
no acredita por sí sola nomenclatura nueva en móvil. Pendiente aceptación visual del
rótulo ajustado y comprobar móvil en la pestaña actualizada. Sin inicio de 6B ni commit/push.

## Bloque 6A implementado localmente — 26/10/2026

Usuario autoriza continuar exclusivamente 6A del plan. Rama feature/navegacion-6a-destinos,
base d42b2e9. Nombres de destino compartidos en navegación conectada; pantalla Documentos
guardados unificada en menú/miga/título/Continuar y enlaces de orientación. Grupos de un
solo destino son enlaces directos; grupos múltiples conservan desplegable. Activo señalado
por subrayado/borde/negrita y aria-current en el destino; no implica guardado o completitud.
Rutas, IDs, contexto, persistencia y reglas no cambian; componente documental independiente
conserva sus títulos anteriores. Sin cambios backend ni habilitación EIPD.

Validación: 51 escenarios conectados (5 nuevos), 20 del flujo documental independiente y
18 de maqueta de referencia aprobados; 89 distintos, sin sumar repeticiones. Tipos, ESLint,
formato y capturas escritorio/390/320 revisados. Pruebas con fixtures ficticios, no una
nueva prueba integrada contra el servidor del usuario. [Evidencia y guion](project/navegacion-servidor.md#bloque-6a--destinos-coherentes-y-accesos-directos).
Pendiente aceptación asistida del usuario. No iniciar 6B ni otros lotes. Sin commit/push
nuevo ni merge/despliegue; autorización previa cerró solamente la documentación del plan.
next-env.d.ts generado y outputs/ locales ajenos al bloque funcional.

## Plan integral de navegación y terminología — 26/10/2026

Usuario solicita analizar dos informes Word de Claude antes del siguiente lote y
replanificar incorporando los lotes pendientes 6, 7 y 8. Contraste de texto/tablas/diagramas,
código y contratos sobre `2e3f5460190185413f6e85243ad59958ba148463`.
La revisión de Claude es fuente externa, no instrucciones ni circuito de ejecución.
Se agregan [evaluación P1–P13 y glosario G01–G30](project/evaluacion-propuestas-claude.md)
y [plan por sublotes 6–13](project/plan-navegacion-formularios.md).
Decisiones de diseño propuestas para implementación, no cambios funcionales aceptados en uso.
Conservar lotes 1–5 y sus aceptaciones; Git acredita lote 5 publicado en 2e3f546.
Las notas históricas siguientes de publicación pendiente describen estados anteriores.

Rama documental: feature/plan-navegacion-terminologia. Sin cambios nuevos de código,
API, datos, permisos ni activación EIPD. No se inicia lote 6. Próximo propuesto: 6A,
nombres de destinos y accesos de un solo destino, con validación conjunta antes de avanzar.
NAV-UX-005, LIC-FORM-001 y demás trabajos funcionales conservan sus propios contratos.
El usuario solicita incorporar los Markdown al repositorio y autoriza commit/push el 26/10/2026.
Este cierre publica solo documentación; no inicia 6A ni acredita implementación o CI remota.
Sin merge/despliegue.
Excluir next-env.d.ts generado y outputs/ locales de cualquier publicación posterior.

## Cierre autorizado del lote 5 — 26/10/2026

Usuario solicita commit y autoriza push del lote 5 aceptado en fix/navegacion-estado-guardado.
Este cierre reúne implementación, pruebas y aceptación asistida C9, incluidos rótulos y
proximidad del resultado de guardado. Las menciones anteriores de publicación pendiente
son antecedentes previos a esta autorización. Excluir frontend/next-env.d.ts y outputs/.
No iniciar lote 6 ni ejecutar merge/despliegue. Comprobar HEAD remoto exacto tras publicar;
no inferir aprobación de CI remota del push. Otros pendientes del backlog conservan su alcance.

## Último resultado — lote 5 aceptado, 26/10/2026

Usuario confirma «OK las etiquetas». Lote 5 C9 aceptado con alcance de consulta que
conserva borrador, comparación rotulada, guardado/revisión coincidente y aviso próximo
a Guardar. Concurrencia, errores y móvil verificados con fixtures, no nuevos ensayos
manuales. Evidencia y límites en [continuidad](project/navegacion-servidor.md#aceptación-asistida-del-lote-5--etiquetas-confirmadas-26102026).
Cambios locales en fix/navegacion-estado-guardado sobre 84ad96a, sin commit/push nuevo.
Archivo generado frontend/next-env.d.ts y capturas de outputs/ ajenos al commit funcional.
Siguiente propuesto: lote 6, pendiente de indicación. No se inicia otro lote.

## Último resultado — lote 5, 26/10/2026

Usuario acepta proximidad del aviso de guardado (OK). Solicita conceptos en cada valor
comparado: etiquetas de decisión y fundamento agregadas en ambas columnas, para EIPD e
infancia. Once pruebas dirigidas, tipos/lint/formato y capturas correctos tras el ajuste;
46 pruebas completas anteriores no repetidas. Pendiente revisión asistida de etiquetas.
Conservar la pestaña original con sus cambios pendientes; no guardar ni recargar para
probar los rótulos. Sin commit/push nuevo. Lote 6 y demás pendientes no iniciados.

## Último resultado asistido — guardado del lote 5

Captura dfa6d431 confirma revisión de aplicabilidad 4 y formulario coincidente,
sin comparación pendiente en el panel. Falta comprobar visualmente el aviso de éxito
inmediatamente antes de Guardar: bajar en la misma pestaña, sin repetir guardado,
editar, consultar o recargar. Sin commit/push del lote 5; aceptación parcial.

## Último resultado asistido — lote 5, 25/10/2026

Capturas ead7a637/fad26d34 confirman consulta y comparación: revisión guardada 3,
línea de prueba conservada en borrador, resultado de consulta y cambios sin guardar.
Aceptación parcial de C9; pendiente guardar explícitamente y validar proximidad del
aviso de éxito/revisión incrementada. No recargar el borrador para esta prueba.
[Detalle y próximo paso](project/navegacion-servidor.md#validación-asistida-del-lote-5--consulta-y-comparación-correctas).
Sin commit/push nuevo ni inicio de otro lote.

## Bloque activo — lote 5 C9, 25/10/2026

Usuario autoriza continuar lote 5 tras documentación publicada en 84ad96a. Implementado
localmente en fix/navegacion-estado-guardado: última determinación consultada con revisión,
fecha/hora Chile y autoría por identificador del contrato; comparación con borrador pendiente;
consulta explícita sin escrituras; historial abierto tras rechazo 409; confirmación de guardado
inmediatamente antes de Guardar. No se inventan nombres de personas ni se modifican permisos,
API, DB o activación EIPD. 46 pruebas Chromium aprobadas (11 nuevas), tipos/lint/formato
correctos; capturas escritorio/390/320 revisadas. Validación asistida pendiente, sin commit/push
del lote 5. Archivo generado frontend/next-env.d.ts ajeno al bloque; capturas ficticias
en outputs/navegacion-lote5/ son evidencia local no destinada al commit. Próximo paso: seguir el
[guion de aceptación del lote 5](project/navegacion-servidor.md#lote-5-c9--estado-guardado-y-borrador).
Los lotes siguientes y demás pendientes del backlog no se inician ni se cierran por este cambio.

## Guía del ciclo documental — 25/10/2026

Se agrega la [guía de borradores, versiones, revisión y decisión EIPD](project/ciclo-documental-eipd.md), contrastada con e587da6, en la rama feature/documentacion-ciclo-documental. Incluye funcionamiento actual, límites de revisión del EIPD general, sucesores de infancia y circuito conceptual pendiente. Cambio exclusivamente documental; no modifica estados, permisos, datos ni la interfaz. El usuario autoriza commit y push de esta guía. Lote 5 y los demás pendientes del backlog conservan su estado.

## Cierre autorizado del lote 4 — 25/10/2026

Usuario autoriza commit y push del lote 4 validado en
fix/navegacion-orientacion-aplicabilidad. El presente bloque reúne implementación,
pruebas y aceptación asistida C3/C8. Lote 5 y mejora de ubicación del aviso de guardado
siguen pendientes, sin iniciar. Verificar HEAD/CI remoto exactos al retomar; no se
infiere CI funcional aprobada de una publicación. Sin merge ni despliegue.
El archivo frontend/next-env.d.ts regenerado por Next.js queda fuera de este commit.

## Último resultado — lote 4 validado, 25/10/2026

Captura 227db7c3 confirma retorno a EIPD tras restaurar Corresponde, con nota pendiente
conservada. Resumen/acceso directo, No corresponde y reubicación explicada ya comprobados
asistidamente. Lote 4 C3/C8 aceptado con ese alcance, local en
fix/navegacion-orientacion-aplicabilidad sobre 0340b0a, sin commit/push nuevo.
Siguiente propuesto: lote 5 C9, incluido acercar la confirmación de guardado al botón.
Pruebas de infancia y demás estados automatizadas; no atribuir ensayos manuales no realizados.

## Bloque activo — lote 4 C3/C8, 25/10/2026

Lote 3 publicado en 0340b0a (remoto verificado). Lote 4 implementado localmente en
fix/navegacion-orientacion-aplicabilidad: resultado de accesos según determinación
guardada, guía para estados no habilitados/consulta previa y aviso de reubicación
con conservación de borradores. Sin cambios de reglas/API/DB/permisos. 34 pruebas
conectadas y 10 dirigidas finales aprobadas (35 escenarios únicos), tipos/lint/formato
y capturas escritorio/390/320 correctos. Aceptación asistida y publicación lote 4
pendientes. [Guion vigente](project/navegacion-servidor.md). No iniciar otros lotes.

## Último resultado — lote 3 validado, 25/10/2026

Usuario confirma OK ayuda dinámica de Guardar y selector de contexto (motivo de
bloqueo, habilitación al seleccionar evaluación y Cancelar). Lote 3 C4 aceptado con
ese alcance; roles/solo consulta verificados automáticamente con fixtures, no otras
cuentas personales. Cambios locales en fix/navegacion-permisos-requisitos sobre
9c8632f; sin commit/push nuevo. Próximo propuesto: lote 4 C3/C8, aún no iniciado.

## Bloque activo — lote 3 C4, 25/10/2026

Lote 2 validado y publicado en 9c8632f, rama fix/navegacion-contexto-modulo.
Usuario autoriza continuar lote 3: implementado localmente en
fix/navegacion-permisos-requisitos, explicaciones de permisos/solo consulta y
requisitos para Guardar/Aplicar contexto, con descripciones accesibles. Veinticinco
Chromium, tipos/lint/formato y capturas aprobados; aceptación asistida pendiente.
Sin commit/push del lote 3 ni cambios de permisos/cuentas/datos/API/DB.
[Guion y límites](project/navegacion-servidor.md). Otros lotes permanecen pendientes.

## Último resultado — lote 2 aceptado, 25/10/2026

Usuario confirma Todo OK; capturas verifican Continuar contextual, cabecera RAT y
retorno a EIPD con notas sin guardar conservadas. Lote 2 C2/C14 validado, local en
fix/navegacion-contexto-modulo sobre lote 1 publicado 465a94c; sin commit/push nuevo.
Siguiente bloque propuesto: lote 3 C4 (permisos/requisitos), aún no iniciado.
No descartar notas pendientes ni cerrar otros criterios de backlog por esta aceptación.

## Bloque activo — lote 2 C2/C14, 25/10/2026

Lote 1 validado y publicado como 465a94c en fix/navegacion-carga-recuperacion,
confirmado contra remoto. Usuario autoriza continuar lote 2: implementación local
en fix/navegacion-contexto-modulo, cabecera por ámbito y Continuar con contexto del
destino; rutas/memoria/borradores intactos. Veinte Chromium, tipos/lint/formato y
capturas escritorio/390/320 aprobados. Aceptación asistida pendiente; sin publicación
nueva del lote 2. Ver [guion vigente](project/navegacion-servidor.md).

## Último resultado asistido — C1, 25/10/2026

Usuario confirma recuperación con Reintentar consulta y notas EIPD pendientes
conservadas en pestaña original tras reautenticar en otra. Lote 1 acotado completado
localmente; 16 Chromium/tipos/lint aprobados, sin commit/push nuevo. Seguimiento de
clasificación de error/sesión y mejoras de botón/duplicación registrados en backlog.
No iniciar lotes siguientes sin indicación; NAV-UX-003/004 no cerrados globalmente.
Los estados anteriores «recuperación pendiente» son antecedentes de este ensayo.

## Bloque activo — lote 1 C1, 25/10/2026

Retomado por usuario. Corrección local en fix/navegacion-carga-recuperacion sobre
db6f0d3: carga/error de aplicabilidad visibles en secciones condicionales, reintento
y retorno al formulario sin desmontar borradores; indicador/reintento de validación
de enlace fuera del selector. 15 Chromium, tipos/ESLint/formato y tres casos visuales
a 390/320/escritorio aprobados. Validación asistida pendiente, sin commit/push nuevo.
[Alcance y guion](project/navegacion-servidor.md#correcciones-de-revisión-externa--lote-1-c1-25102026).
Claude solo revisor externo; restantes lotes pendientes, EIPD bloqueada.

## Pausa solicitada y reanudación — 25/10/2026

Usuario solicita detener el trabajo por unas horas, registrar avance y próximos pasos,
y autoriza commit/push de la integración y este registro. Rama de continuidad:
`feature/navegacion-servidor`, base publicada de maqueta `6612076`.
Publicación del presente bloque autorizada; comprobar HEAD remoto y CI al retomar.
No confundir push con merge o despliegue: ninguno está autorizado en este cierre.

Leer primero [estado y guion conectado](project/navegacion-servidor.md), después
[checklist de maqueta](project/maqueta-navegacion-integral.md),
[checklist de licitud](project/m3-t1-checklist-recorrido-licitud.md) y
[backlog](backlog.md). Los bloques fechados anteriores conservan evidencia histórica;
este punto de continuidad prevalece sobre sus menciones de aceptación/publicación pendientes.

Retomar con sesión habitual en `/dashboard/trabajo`, comprobar servicios locales y
seleccionar organización/RAT/finalidad/evaluación existentes. No asumir el contexto
de otra ventana, no crear duplicados y no recargar ediciones pendientes para probar.
Seguir el checklist conectado: persistencia/aplicabilidad y luego documentos, anexos,
resoluciones, revisiones/decisiones/facultades, historial y descargas. Registrar cada
resultado asistido y hallazgo antes de cerrar NAV-UX-002/003/004. NAV-UX-005,
LIC-FORM-001 y demás pendientes no quedan resueltos por la integración.
Trabajo funcional detenido tras publicación; sin tareas programadas ni cambios adicionales.

## Entrada y limites

Participan usuario, ChatGPT/Codex y Deepseek. El usuario incorporó a Claude como
revisor puntual de navegación: aportó informe de solo lectura y propuesta HTML.
Codex valida e implementa; esto no delega operación, permisos ni publicación a Claude.
Leer AGENTS.md y docs/ai/handoff-contract.md. Para una tarea acotada, leer solo
su paquete y los ADR relevantes, no toda la historia de status.md.
EIPD bloqueada; datos ficticios; sin merge/despliegue. Credenciales nunca via chat.

## Estado operativo

Base verificada para preparar este contrato: 39dfad5, rama
feature/m3-t1-licitud-persistencia. CI 38819932076 success, comprobada por Codex
via GitHub Actions 2026-10-15: 4454 backend aprobadas, 1 omitida; frontend e
integrada aprobados. Esta observacion es un snapshot, no el HEAD perpetuo.
Antes de transferir, generar scripts/handoff.py state --remote: ese resultado
identifica el HEAD exacto de la tarea. Una CI anterior no prueba un commit nuevo.

## Bloque funcional vigente — producto

25/10, integración local de navegación en rama feature/navegacion-servidor, base
6612076 (ya publicado con aceptación de maqueta). /dashboard y /dashboard/trabajo
usan módulos/API reales y contexto autorizado por organización/RAT/serie/evaluación;
50 preguntas, borradores por contexto, paneles móviles, historial y salida protegida.
Aplicabilidad independiente persistida append-only; migración f6a24c8e9102 aplicada
primero aislada y después en desarrollo local, sin pérdida/inserción de expedientes.
1.145 runner EIPD + 194 API aprobadas; 55 UI con una captura opcional omitida,
batería conectada ampliada de 10, recorrido Chromium/API/PostgreSQL real y build
aprobados; tipos/ESLint correctos. [Contrato, límites y prueba](project/navegacion-servidor.md).
Aceptación asistida conectada y CI remota pendientes. Publicación de la integración
autorizada por el usuario en el cierre de pausa del 25/10. No hay sincronización automática entre ventanas ni cambio de snapshot
RAT implícito; NAV-UX-005 y LIC-FORM-001 siguen abiertos. EIPD/datos reales bloqueados.

24/10, aceptación asistida: usuario confirma OK navegación de la maqueta y cierres
móviles; aclara que Escape vuelve al formulario y clic exterior es fondo sombreado.
Aprueba commit/push de resultados y solicita integrar navegación al servidor.
Documentos/anexos/resoluciones/historial/descargas se probarán tras conexión.
Las menciones siguientes a aceptación pendiente son antecedentes superados por
este recorrido; no se declara aceptado el producto conectado ni habilitada EIPD.

Incidencia móvil de cierre persistente comunicada por usuario en ambos paneles:
solución local actual reemplaza diálogos nativos por PrototypeDrawer con portal,
fondo explícito, Escape/clic exterior, foco confinado y fondo inert. 30 Chromium
incluidas capturas y tipos/ESLint aprobados. Falta validar en Edge del usuario;
los ajustes previos de eventos no resolvieron su reporte. Sin commit/push nuevo.

24/10, prueba asistida: usuario confirma borradores/guardados de riesgos y medidas,
retirada/restauración EIPD sin pérdida, independencia infancia/EIPD y separación
entre evaluaciones. Solicita Secciones junto a Menú con panel lateral móvil:
implementado localmente, selección abre formulario y cierra panel, Escape/Cerrar
restauran foco; 29 Chromium incluidas capturas, tipos/ESLint aprobados. Validación
asistida del panel y publicación pendientes. NAV-UX-005 registra alcance mixto
adultos/hijos para desarrollo posterior, sin modificar la restricción del ejemplo.

24/10, ajuste posterior: aplicabilidad independiente de EIPD e infancia. Bases de
licitud abre Determinar aplicabilidad; estado Corresponde guardado con fundamento
habilita su menú de completar. Pendiente/No corresponde/Información insuficiente
no habilitan edición. Datos previos conservados, filtros también en historial,
Continuar y enlaces. No clasificador jurídico ni cambios de servidor. 29 Chromium,
tipos/ESLint aprobados; [contrato y prueba](project/maqueta-aplicabilidad.md).
Validación asistida y publicación de este ajuste pendientes.

24/10: usuario aprueba propuesta de Claude; rediseño de maqueta sobre base a9d3ab4,
rama feature/maqueta-navegacion-review. Menú oscuro, contexto Cambiar con confirmación,
agrupación por intención, historial Atrás/Adelante, recuerdo por módulo/evaluación,
Continuar real, salida protegida y cajón/ubicación móvil. Formularios y bloqueos
conservados. [Respuesta hallazgo por hallazgo y oportunidades](project/maqueta-revision-claude.md).
25 Chromium (incluidas capturas), tipos/ESLint aprobados localmente; revisión
asistida y CI remota pendientes. Lo siguiente describe el antecedente de la maqueta.

Maqueta integral NAV-UX-001 en `/dashboard/maqueta`: Panel principal y seis módulos,
menú principal izquierdo y opciones superiores por módulo según bosquejo del usuario,
submenús por clic/teclado y formularios centrales. Selección explícita de tratamiento,
finalidad y evaluación: dos tratamientos, tres finalidades y cuatro evaluaciones
ficticias con borradores/guardados/anexos separados; adopción conectada NAV-UX-002 pendiente,
Mi organización con nombre/RUT/rubro/tamaño, Documentos y Carpeta de evidencias
marcados Próximamente. Guardado en memoria y consultas/ventanas de detalle. Accesos desde dashboard y
licitud. [Contrato y guion de prueba](project/maqueta-navegacion-integral.md).
Ajuste asistido: menú principal persistente también en ventana estrecha al bajar
por formularios; 17 pruebas locales aprobadas, captura opcional omitida, tipos/lint
aprobados. Cuestionario completo de 50 preguntas requerido para integración;
campos actuales del diagnóstico son ilustrativos. CI del ajuste no verificada.
No sustituye producto ni implementa consentimientos/LIA completos; validación
asistida del diseño y adopción pendientes. Recargar reinicia la demostración.

Pendiente LIC-UX-013: consulta del residual por riesgo junto con medidas, dimensión,
eficacia, verificación y respaldos. Alcance y criterios detallados en [backlog](backlog.md);
registrado para desarrollo posterior, sin cambios de producto. Preservar procedencia
y revisión histórica; no atribuir reducciones individuales no evaluadas.

Pendiente LIC-FORM-001: formularios completos de consentimiento/LIA. Originales Excel
aportados y 50 preguntas cotejadas; servidor existente no equivale a UI completa.
Para retomar leer [contrato de implementación](project/m3-t1-consentimiento-lia-implementacion.md)
y [auditoría de cobertura](project/m3-t1-consentimiento-lia-cobertura.md). Desarrollo
no iniciado en este bloque documental; preservación/versionado/evidencias requieren
las decisiones indicadas. Usuario pidió registro detallado para implementación posterior.

Bloque de riesgos/anexos implementado: metodología interna de cuatro niveles,
inherente/residual previsto/actual, controles fundamentados y respaldo PDF/TXT
versionado. Revisar documentos reúne RAT, licitud/LIA y EIPD. Preparación infancia
oculta en adultos; consulta de autoridad condicional y filas vacías corregidas.
Migración e67a4b829c10 en pruebas y desarrollo local; 38 tablas previas intactas.
Pruebas dirigidas, tipos/lint/formato y recorrido real aislado aprobados; detalle en
[contrato vigente](project/m3-t1-riesgos-anexos.md). Pendiente validación asistida
ampliada y revisión/adopción formal EIPD general/RAT-LIA; EIPD/datos reales bloqueados.
CI base 6bf7870 aprobada: 4518 backend (2 omitidas), 211 frontend y 2 integradas.
Bloque UX del 22/10 implementado: LIC-UX-005 a 012, siete pasos EIPD con valoración
como paso 4, tablas completas por riesgo, tipografía y avisos cercanos al guardado.
34 Chromium y 4 aisladas de recorrido/listado aprobadas; tipos/lint/formato y
capturas escritorio/móvil revisados. Checklist consolida el recorrido asistido:
[estado vigente](project/m3-t1-checklist-recorrido-licitud.md).
Pendiente revisión visual del usuario y CI del nuevo bloque; metodología configurable
y auditoría completa requieren diseño separado. EIPD bloqueada; sin merge/despliegue.

19/10: recorrido Bases de Licitud integrado al servidor: cuatro pestanas,
secciones cortas, borradores conservados al navegar y diagnosticos/descargas
invalidados tras guardar. Preparacion de resolucion infancia con vista previa,
lectura ficticia y proteccion de reemplazo; revision/decision/facultades separadas.
EIPD general: borrador con seis secciones, riesgos/medidas/evidencias/seguimiento,
guardado y reapertura; copia guardada consultable sin confundirla con resolucion.
71 Chromium afectados, 4 API/integracion con PostgreSQL aislado, tipos/lint/formato;
SQL confirma EIPD/LIA persistidos y confirmed_at=null; vista movil/escritorio revisada.
No nuevos endpoints, migraciones, permisos ni opt-in local. EIPD/datos reales
bloqueados, sin merge/despliegue. CI exacta del nuevo commit por consultar.
Pendientes: validacion asistida conectada; revision EIPD general/adopcion RAT-LIA
y trazabilidad estructurada requieren sus contratos; cierre juridico/operativo
no declarado. LIC-UX-004 abierto. Contrato: project/m3-t1-licitud-experiencia.md.

18/10: recorrido manual ficticio de Bases de licitud cerrado: clientes,
trabajadores e infancia; guardado/reapertura, dos resoluciones, revisiones negativas,
decision documental y grant/revocacion. Decision conservada, nuevas decisiones
bloqueadas en UI tras recarga; JSON con faculty_current=false y EIPD/datos reales
bloqueados. Escritura temporal local restituida a false y override retirado.
CI funcional de 33039d3 success (39040075836), Handoff tambien success.
No hay pruebas pendientes del recorrido acotado; pendientes de producto/operacion
no equivalen a aprobacion para datos reales. Evidencia y limites en
project/m3-t1-recorrido-frontend.md; hallazgos en backlog.md. Sin merge/despliegue.

16/10: piloto sigue ficticio. Usuario define escenario [FICTICIA] Comercial Piloto
Andes SpA / [FICTICIA] Persona Facultada Piloto, contactos example.invalid y RUT
simulados. V2 genera actas descargables HTML/JSON con marca ACTA DE PRUEBA,
DATOS FICTICIOS, SIN VALOR JURIDICO; referencias SIMULADA- exigidas en servidor.
Revision pendiente/no realizada por defecto; cualquier otra decision es simulada.
Escenario no sustituye identidad tecnica de sesion, no registra aceptacion real
ni cierra gates. V1 e historiales conservados, datos reales y EIPD bloqueados.
20 backend/guardas, 13 UI/cliente y una integrada real aprobadas; tipos/lint/formato.
Docker/WSL restablecido; CI previa b229fb3 aprobada. Verificar nuevo HEAD/CI.
[Contrato y evidencia](project/m3-t1-piloto-preparacion.md).
Pendientes reales: empresa/actas/facultades, revision humana y controles de piloto.
Piloto poblado local validado: clientes/trabajadores con LIA borrador e infancia
con dos resoluciones, dos revisiones negativas, dos eventos documentales y
otorgamiento/revocacion de facultades (ocho registros historicos). Restauracion
de 39 tablas conserva conteos/checksums/politicas y lecturas API como app_user;
aislamiento, facultad revocada y EIPD bloqueada comprobados en la copia.
Ejecutor fijo: backend `python -m scripts.run_populated_pilot`; limpia solo fixtures
y copia propias. Evidencia: project/pilot-evidence/populated-history-restore-20261016.json.
41 pruebas dirigidas y recorrido local poblado aprobados; CI del previo 8a8903f
aprobada. Comprobar candidato por HEAD. No certifica produccion ni backup externo.
Sin migraciones, provision de identidades, merge o despliegue.

## Proxima transferencia

Estado: DS-001 a DS-005 terminados. DS-005 agrega reordenacion de evidencia;
25 UI aprobadas (7 independientes), tipos/lint/formato aprobados tras Prettier
final de Codex. El bucle Deepseek se detuvo tras tres fallos de formato;
no acredita autonomia completa. Ver docs/ai/pilot-results.md y results/DS-005.json.
Permisos acotados, no agente general; no reenviar pilotos terminados.
BENCH-001: tres pares pequenos, 5 puntos cuota local vs 22 delegados; no ahorro
observado, cuota compartida y par 2 contaminado. No extrapolar. Informe:
docs/ai/benchmarks/BENCH-001.md. 18 regresiones nuevas, comando CI 91 aprobadas.

Desde raiz y checkout limpio:

    python3 scripts/handoff.py state --remote
    python3 scripts/handoff.py packet --task docs/ai/tasks/DS-001.json --remote > /tmp/CumpleIA-DS-001.json

No hay bloque Deepseek activo. Decision: seleccionar bloques coherentes caso a
caso; microtareas directas en Codex. Ejecutor consolidado y validado localmente
sin API: 36 unitarias + 25 Chromium. Guia: docs/ai/deepseek-automation.md.

Modalidad recomendada por preferencia del usuario: lanzador local + API,
`python3 scripts/deepseek_run.py ID`. Por defecto prepara sin gasto. Clave dedicada
y servicio verificados; trece generaciones pagadas entre pilotos y BENCH-001. Nuevas tareas requieren
contrato y autorizacion de gasto; no hay lote mensual autorizado. Ver
docs/ai/deepseek-automation.md.

Fallback manual: copiar el JSON completo a Deepseek y pedir diff unificado + reporte, sin aplicar.
Al volver, guardar el diff fuera del checkout y comprobarlo usando el HEAD del
paquete (nunca sustituirlo por el HEAD actual para eludir una base obsoleta):

    python3 scripts/handoff.py check --task docs/ai/tasks/DS-001.json --base HEAD_DEL_PAQUETE --patch /tmp/DS-001.patch

El check no aplica el parche ni aprueba pruebas. Codex revisa, aplica y ejecuta
los checks del contrato. Solo tras aceptar el bloque se hace commit/push bajo
la autorizacion del usuario. Mantener un unico responsable por tarea.

## Evidencia y continuidad

Tabla de verificacion, resultados del ensayo local y criterios del piloto:
docs/ai/pilot-results.md. Accesos: docs/ai/access-matrix.md.
Los handoffs fechados previos permanecen como antecedentes para preservar enlaces.
Nuevos cierres historicos, solo cuando aporten una decision o evidencia necesaria,
van a docs/archive/. No duplicar el historial en este archivo.
