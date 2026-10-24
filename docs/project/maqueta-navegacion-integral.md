# Maqueta integral de navegación de CumpleIA

## Objetivo y estado

NAV-UX-001 / LIC-UX-015. Usuario solicita incorporar el Panel principal al rediseño
para que la navegación sea homogénea y preparar la maqueta completa antes de sus
pruebas asistidas. Ruta local: `/dashboard/maqueta`, dentro del dashboard protegido.
Accesos visibles desde Panel principal y Bases de licitud; la maqueta V3 previa
conserva su ruta y ofrece enlace a la propuesta integral.

Estado: implementada como demostración aislada; validación dirigida y visual local
realizada. Prueba asistida y aceptación del diseño por el usuario pendientes.
No sustituye los recorridos conectados ni implementa sus cambios pendientes.

## Ajuste vigente: determinar antes de completar (24/10/2026)

Solicitud adicional del usuario: EIPD e infancia no deben aparecer como formularios
obligatorios en todos los casos. Se añade Determinar aplicabilidad, con dos
conclusiones fundamentadas e independientes por evaluación. Los accesos Completar
EIPD e Infancia aparecen únicamente tras guardar Corresponde. Los otros estados
no habilitan edición; los datos y versiones previas se conservan. Filtro común en
menús, navegación y enlaces. [Contrato, límites y prueba](maqueta-aplicabilidad.md).
29 Chromium, tipos/ESLint y capturas aprobados localmente; validación asistida y
adopción conectada pendientes. Esta sección prevalece sobre la presentación previa.

## Versión vigente: propuesta de Claude adaptada (24/10/2026)

El usuario aprobó el HTML de navegación y solicitó validar el informe de revisión.
Se implementa el patrón visual sobre los formularios funcionales de la maqueta:
menú oscuro Trabajo / Próximas funciones / Cuenta; contexto en diálogo Cambiar;
Bases de licitud agrupado en Alcance, Preparar, Revisar y decidir, Registro;
historial de sección/evaluación en fragmento, recuerdo por módulo/evaluación,
continuidad real desde Panel, migas y ubicación persistente móvil. Se conserva
la autenticación existente y los bloqueos. El marco antiguo descrito a continuación
es antecedente histórico; esta sección y el [análisis de la revisión](maqueta-revision-claude.md)
describen la implementación vigente. Autodiagnóstico completo de 50 preguntas y
adopción conectada siguen pendientes. No hay merge ni despliegue.

## Estructura común aprobada a partir del bosquejo del usuario

El usuario revisó la primera maqueta y señaló que aún costaba encontrar opciones.
Aportó un PowerPoint de cuatro pantallas con menú principal izquierdo y opciones
propias de cada módulo arriba. Aceptó las recomendaciones y pidió preparar esta
segunda versión para probarla. Aceptación de la propuesta no equivale a aceptación
de la implementación ni adopción en el producto conectado.

1. Menú principal fijo a la izquierda en escritorio: Inicio / Panel principal,
   Autodiagnóstico, Inventario de tratamientos, Bases de licitud, Documentos,
   Carpeta de evidencia y Mi organización. Iconos, nombres y selección naranja
   con borde e indicador accesible. En móvil usa un botón Abrir menú.
2. Barra superior específica de cada módulo. Se elimina la capa transversal de
   cuatro tareas y el segundo menú lateral de pasos. El estado interno de tarea
   se conserva únicamente para reutilizar formularios y consultas de la maqueta.
3. RAT: Catálogo con dos tratamientos ficticios, Actividad de tratamiento con cuatro
   secciones, Documentos y revisiones e Historial y descargas.
4. Bases de licitud: Alcance RAT, Base y fundamento, Infancia cuando corresponde,
   Documentar EIPD, Anexos, Resoluciones y revisiones cuando corresponde,
   Documentos guardados e Historial y descargas. EIPD abre cinco accesos:
   Tratamiento y alcance, Necesidad y proporcionalidad, Valorar riesgos,
   Valorar medidas y Fuentes y evidencias. Preparar resolución documental es
   el primer acceso de Resoluciones y revisiones, con referencia, notas y motivo.
5. Los submenús se abren por clic, no por pasar el puntero. Permanecen abiertos
   hasta elegir, pulsar Escape, clicar fuera o cambiar tamaño de pantalla.
   Teclado: Tab/Enter, flechas, Inicio/Fin y Escape con foco al control de apertura.
   Posición horizontal ajustada al espacio de pantalla. Móvil despliega opciones
   dentro de una lista con desplazamiento propio, sin tapar toda la pantalla.
6. Formularios largos en el área central. Cabecera con organización, escenario y
   evaluación, más tratamiento/finalidad y ruta de la sección. Menús y contexto
   compacto persistentes en escritorio; móvil evita una cabecera fija demasiado alta.
   Navegar lleva el foco al contenido y conserva los cambios de la visita.
7. Ventanas breves para detalles, copia, vista previa y confirmación. Se conserva
   la separación entre consultar, guardar, revisar y decidir por la organización.

## Qué se puede probar

- Panel con seis tarjetas de módulo y acceso a continuar la evaluación.
- Diagnóstico: menú de diez secciones ilustrativas, guardado y resultados de ejemplo.
  La primera contiene una pregunta; las otras nueve prueban ubicación y navegación,
  sin reproducir el cuestionario completo ni su puntuación.
- RAT: alcance, fuentes/sistemas, conservación/eliminación, terceros/transferencias.
- Licitud: alcance consultable, base/fundamento, infancia condicional, EIPD,
  riesgos, medidas, anexos y preparación de resolución de infancia.
- Consultas dentro de Bases de licitud: campos guardados, paneles de evidencia y vínculos de riesgos.
- Documentos y Carpeta de evidencias: accesos visibles con «Próximamente», deshabilitados
  en menú principal y tarjetas del Panel. No representan módulos disponibles.
- Mi organización: abre directamente nombre, RUT, rubro/industria y tamaño, con los
  valores de demostración de la captura aportada (CumpleIA Demo, 1111111-0, Consultoría,
  Pequeña empresa PYME). Guardado solo en memoria; los mismos datos se mantienen
  al alternar escenarios. Facultades siguen consultables dentro del recorrido de infancia.
- Historial y descargas: versiones de infancia, actividad de la visita y JSON de ejemplo.

### Estado y conservación

Dos tratamientos ficticios: Gestión de clientes y Programa con menores de 10 a 13 años.
La selección explícita usa tratamiento → finalidad → evaluación: dos finalidades de
clientes (citas y seguimiento comercial), una de infancia y cuatro evaluaciones
predefinidas, incluidas dos versiones de citas. No crea ni adopta evaluaciones reales.
Borradores y guardados se mantienen en memoria React mientras no se recargue;
cambiar módulo/finalidad/evaluación no borra los textos. Los valores guardados, estados,
anexos y actividad se separan por evaluación; los datos de organización se comparten
solo entre los ejemplos de esa misma organización. Los pasos con nuevas ediciones
muestran Cambios sin guardar aunque antes se hayan guardado. La consulta y el JSON
usan valores guardados; no incorporan los cambios pendientes.
No localStorage/sessionStorage, peticiones API, DB ni almacenamiento de archivos.
La ruta mantiene la autenticación existente del dashboard; el componente de maqueta
no obtiene ni utiliza tokens. Datos ficticios propios, no una copia de los expedientes
del usuario. Reiniciar solicita confirmación y recargar restaura todos los ejemplos.

### Revisiones y copias

Infancia permite consultar versiones 1/2, revisión documental separada de decisión
organizacional y facultad revocada. Copiar siempre pide confirmación, preserva el
original y abre preparación temporal con origen. Conservar no reemplaza el formulario.
Vista previa requiere referencia SIMULADA-, notas, motivo y declaración ficticia;
registro simulado exige otra confirmación. Una versión nueva no hereda revisiones
ni decisiones anteriores. No se concede facultad ni se habilita operación real.

### Límites de la simulación

- Campos de ejemplo representan las ubicaciones y jerarquía; no todos los contratos
  jurídicos completos. Consentimiento y LIA muestran el acceso previsto y explican
  que LIC-FORM-001 sigue pendiente; no se da por implementado.
- El resultado de diagnóstico es ilustrativo. La tarjeta conjunta R1/M1 es un ejemplo
  de lectura fijo, identificado como independiente de la edición de probabilidad/impacto;
  no recalcula ni acredita verificación real.
- Anexos validan extensión PDF/TXT, vacío y límite 2 MiB, preservan metadatos y
  bloquean Guardar si inválidos. Solo retienen el nombre del archivo, no sus bytes;
  no realizan análisis de contenido ni reproducen validaciones completas del servidor.
- Descarga `maqueta-cumpleia-*.json`, con marca propia y can_confirm=false,
  activation=deshabilitada. No es el contrato de expediente MVP ni contiene huellas
  auditables o aceptación jurídica. Consultas y simulación no alteran el producto.
- Documentos y Carpeta de evidencias están marcados Próximamente. Las consultas y
  los anexos dentro de Bases de licitud siguen disponibles en la maqueta.

## Validación técnica local

Archivos: frontend/components/navigation/{NavigationPrototype.tsx,prototype-data.ts},
PrototypeMenus.tsx y prototype-navigation.ts;
ruta frontend/app/dashboard/maqueta/page.tsx y accesos de dashboard/licitud.
Suite: frontend/e2e/navigation-prototype.spec.ts; comando npm run test:navigation-prototype.
Incluida también en test:eipd-client para CI. Se compila el componente real con
webpack/TypeScript y Tailwind existentes; navegador con red interceptada, sin servicios
ni credenciales. No nueva dependencia. No suite backend: no cambios backend.

Pruebas dirigidas: cobertura de todos los destinos de navegación, foco, borradores,
separación de escenarios, consulta guardada, cancelación/copia/registro conservando
originales, selección de archivo inválido y corrección, Escape/retorno de foco,
descarga solo guardada, reinicio, estados de guardado y móvil 390/320 sin desborde.
Capturas adicionales para escritorio 1440 y móvil 390. Ejecución local con
MAQUETA_SCREENSHOTS produce las imágenes; sin esa variable se omite solo la captura.
La segunda versión añade pruebas de desplegables por clic/teclado, acceso directo
a preparación y tamaños 1440/1024/768/640/390/320. Resultado previo: 13 pruebas
aprobadas (12 funcionales y una de capturas). Ajuste de organización y Próximamente
validado con la suite actualizada: 14 pruebas aprobadas en 14.6 s. Tras limitar
Mi organización a sus cuatro campos, caso específico y capturas repetidos: 2 aprobados.
Captura final de organización inspeccionada visualmente; tipos/lint/formato aprobados. Tipos, ESLint y formato
comprobados. Capturas revisadas de Panel, RAT, Infancia, menús EIPD y resoluciones,
escritorio y móvil. Ajuste final de reinicio de anexos validado con el caso dirigido.
Ruta local responde 307 hacia autenticación sin sesión; no se usaron credenciales
para estas pruebas ni se extrapola CI remota.
Tipos y ESLint de archivos afectados y formato comprobados; CI remota de este
candidato debe verificarse por HEAD, no se infiere de estos resultados.

## Guion para las pruebas asistidas del diseño

1. Abrir `/dashboard/maqueta` desde el Panel actual. Confirmar que aparece
   «Menú lateral y opciones por módulo» y seleccionar Inicio / Panel principal.
2. Encontrar Inventario de tratamientos en el menú izquierdo, abrir una actividad
   desde Catálogo y localizar sus secciones en Actividad de tratamiento.
3. Abrir Autodiagnóstico, desplegar Secciones y elegir la sección 7; volver a RAT.
4. Entrar a Bases de licitud y abrir Base y fundamento directamente. Editar un texto,
   cambiar de módulo y volver: debe conservarse sin que ello implique guardado.
5. Guardar el fundamento y localizarlo en Documentos guardados. Abrir un detalle,
   cerrar con botón o Escape y comprobar el retorno de foco.
6. Abrir Documentar EIPD, elegir Valorar riesgos y después Valorar medidas.
   Comprobar que las cinco opciones se encuentran sin buscar botones al pie.
7. Seleccionar el tratamiento Programa con menores. Abrir Infancia; después Resoluciones y revisiones
   y Preparar resolución documental. Comprobar ubicación, título y contenido central.
8. Consultar resolución 2, probar copiar/cancelar conservando el texto temporal;
   opcionalmente completar vista previa y registro exclusivamente simulado.
9. Localizar Revisiones, Decisiones y Facultades desde el mismo menú. Verificar
   que la facultad revocada mantiene bloqueada la decisión organizacional.
10. Probar anexo CSV rechazado y sustitución por TXT; encontrar Historial y descargas.
    Repetir navegación con teclado y en móvil; recargar solo si se desea reiniciar.

Registrar dificultad para encontrar opciones, número de clics, comprensión del
contexto y diferencia entre consulta/guardar/registrar. Ajustar la maqueta antes de
trasladar el patrón al producto conectado. NAV-UX-001 y LIC-UX-015 siguen abiertos
hasta la validación asistida y la adopción correspondiente.

## Ajuste observado durante la prueba asistida

Capturas 9c344647, 0d6da390 y a40ce6e1: el usuario confirma que Sistemas utilizados
conserva el texto ficticio tras cambiar de módulo; la primera captura posterior
muestra confirmación de guardado y la siguiente conserva el texto sin aviso de
cambios pendientes. El usuario observa que la confirmación estaba al inicio del
formulario, lejos de Guardar. Se reubica inmediatamente sobre los botones de guardado
en los formularios editables de la maqueta, una sola vez y con role=status. Los avisos
de consulta, copia y registro conservan su ubicación. No se modifica persistencia.
La confirmación temporal se limpia al navegar; ello no borra los valores guardados.

## Nombres diferenciados durante la revisión asistida

Usuario observa confusión entre Documentos del menú principal y Documentos guardados
como consulta de una evaluación (captura be1d7c1e). Se adopta «Políticas y referencias
normativas» en menú izquierdo y tarjeta del Panel, manteniendo Próximamente y el acceso
deshabilitado. Documentos guardados sigue siendo la consulta interna de cada evaluación.
El cambio es de nombre en la maqueta; no implementa políticas ni búsqueda normativa.

## Selección de contexto incorporada durante el recorrido

Usuario pregunta dónde se selecciona la finalidad y autoriza incorporarla ahora a
la maqueta, dejando la adopción conectada en backlog. En RAT y Bases de licitud se
muestran Organización (contexto único ficticio), Tratamiento del RAT, Finalidad de la
evaluación y Evaluación. Las opciones dependen de la selección anterior. Cambiar de
tratamiento/finalidad selecciona su primera evaluación válida sin copiar el borrador.
La selección se conserva al cambiar de módulo; al navegar dentro de la evaluación se
mantiene el paso si es aplicable. Infancia desaparece al seleccionar un tratamiento
adulto y el paso cambia si deja de corresponder. Cabecera persistente muestra finalidad
y versión correctas. Los nombres y finalidades del alcance se consultan desde este
contexto; su edición libre queda fuera del ejemplo para no contradecir la selección.

Fundamentos, guardados/pendientes, valoración ilustrativa editable, nombres de anexos,
selección de archivo de ejemplo y actividad pertenecen a cada evaluación. Cambiar el
contexto desmarca declaraciones ficticias y limpia los campos transitorios de revisión.
Los datos de Mi organización se reflejan en los cuatro ejemplos. Las dos resoluciones
predefinidas y sus revisiones pertenecen únicamente a la evaluación de infancia.
El JSON añade tratamiento, finalidad e identidad/versión de evaluación; sigue siendo
una descarga propia de maqueta, sin API, DB ni equivalencia con el expediente MVP.
Reiniciar restablece las cuatro evaluaciones; recargar continúa reiniciando la visita.

Prueba asistida nueva: seleccionar Gestión de clientes → Citas → versión 1, editar un
fundamento, cambiar a versión 2 y volver. Seleccionar Seguimiento comercial y comprobar
que no aparecen el fundamento, anexos ni actividad de Citas. Volver a Citas y confirmar
su conservación. Después seleccionar Programa con menores y continuar Infancia.

Validación de este bloque: 16 recorridos Chromium aprobados en 16.0 s, con tipos,
ESLint y formato de archivos afectados comprobados. Nuevos casos prueban filtrado de
opciones dependientes, retorno entre finalidades/versiones con borradores separados,
consulta exclusiva de guardados y aislamiento de anexos/actividad/JSON. Casos previos
de infancia, copia/cancelación/registro, facultad revocada, reinicio y móvil siguen
aprobados. Capturas de selección en escritorio y de infancia en móvil inspeccionadas.
Validación asistida de los nuevos selectores por el usuario pendiente; CI remota no
verificada para este candidato. No cambios de servidor, permisos o expedientes.

## Registro simulado y aviso de cambios pendientes

Prueba asistida: capturas a57a2854 y confirmación del usuario indican que ahora se
encuentra más fácilmente Preparar resolución documental. Cancelar copia conserva
la marca temporal y cerrar vista previa conserva referencia/notas/motivo (91eae0e2,
76ceb658). Capturas a87e45eb y 86a3eaa1 muestran resolución 3 registrada con sus notas
y resolución 2 con su contenido anterior, sin incorporar la marca de resolución 3.

Hallazgo: el aviso general de cambios pendientes seguía apareciendo tras registrar.
Causa comprobada: se vaciaba el formulario de preparación, pero su referencia de
comparación conservaba los valores iniciales. Se limpia también esa referencia
solo para los tres campos de preparación consumidos. No se marcan como guardados
los demás campos, ni se modifican resoluciones registradas. Validación dirigida
comprueba ausencia de aviso falso y conservación de avisos y textos realmente
pendientes en Infancia. No requiere reiniciar el recorrido actual del usuario.

## Descarga revisada al cerrar infancia

Archivo aportado por el usuario maqueta-cumpleia-infancia.json: 12 comprobaciones
aprobadas de identidad del ejemplo, contexto infancia/programa/evaluación v1, edades
sintéticas, referencias/resoluciones 1-3, marca temporal solo en resolución 3,
contenido de resolución 2 conservado, anexos vacíos y bloqueos de confirmación/activación.
No se infiere aceptación global del diseño ni persistencia en servidor.

Hallazgo adicional: el motivo obligatorio mostrado en la vista previa no se copiaba
al registro de resolución. Se incorpora reason en los nuevos registros de maqueta,
consulta y JSON. Es opcional en ejemplos anteriores: no se inventa ni completa un
motivo para los registros previos ni se modifica el archivo del usuario. Caso dirigido
verifica motivo de nueva resolución en pantalla y descarga, resolución 2 sin cambios
y bloqueos conservados. Para repetir manualmente se necesita un nuevo registro de
prueba; volver a descargar la resolución 3 anterior no recupera un motivo descartado.


## Ventana estrecha y recorrido asistido

Usuario confirma guardado/consulta del anexo TXT de infancia y ausencia en adultos;
se conserva al retornar a infancia. Autodiagnóstico sección 6 conserva borrador al
ir a sección 7 y volver, y guardado tras pasar por Panel principal. Resultados e
informe muestran sus títulos y contenido ilustrativo. El enlace al alcance RAT
conserva tratamiento, finalidad y evaluación de citas v1.

Requisito explícito del usuario para integración: reemplazar campos ilustrativos
del autodiagnóstico por las 50 preguntas del cuestionario del servidor, con sus
opciones, guardado y resultados. La validación actual es solo de navegación.

Hallazgo asistido en ventana estrecha: al bajar por un formulario, el acceso
Abrir menú quedaba fuera de vista. Se mantiene fija durante el desplazamiento la
cabecera del menú principal también bajo 768 px; la barra contextual se desplaza
con el contenido en ese tamaño para no superponer dos cabeceras. El menú expandido
permite desplazamiento dentro del alto disponible. Sin cambios de datos/servidor.

Validación local del ajuste: 17 pruebas de navegación aprobadas; una captura
opcional omitida. Caso nuevo comprueba acceso visible al final del formulario
y cambio de módulo en anchos 640/390/320 px. Tipos y ESLint aprobados.
CI remota no verificada para este ajuste; aceptación visual del usuario pendiente.


## Ajuste asistido: secciones en panel lateral móvil — 24/10/2026

El usuario solicita que Secciones funcione como Menú principal en ventana estrecha.
Secciones queda junto a Menú y abre un diálogo lateral con las opciones disponibles
agrupadas por intención. Seleccionar una opción cierra el panel y abre su área de
trabajo con el foco en el contenido, conservando los datos. Escape, Cerrar secciones
y pulsar fuera cierran el panel; el cierre explícito devuelve el foco al botón.
El panel permite desplazamiento propio y mantiene los filtros de aplicabilidad.
La presentación de escritorio se conserva. Sin cambios de servidor o persistencia.

Validación del ajuste: 29 pruebas Chromium (incluidas capturas), tipos y ESLint
aprobados localmente. Revisión visual del panel móvil realizada; aceptación
asistida y publicación pendientes.

Incidencia asistida posterior: usuario informa que Escape no cierra el panel.
Se refuerza el manejo de teclado directamente en ambos diálogos laterales, con
cierre inmediato, sincronización del estado al cerrar y retorno de foco al botón.
Prueba ampliada: Escape desde una opción enfocada, reapertura y cierre, además
del recorrido móvil. Tipos/ESLint y seis pruebas funcionales focalizadas aprobados;
una prueba opcional de capturas omitida. Revalidación en la ventana Edge del usuario pendiente.

Segunda incidencia asistida: Escape y clic exterior siguen sin funcionar en Edge
según usuario; no se pudo inspeccionar esa pestaña con el conector disponible.
Se incorpora cierre compartido de ambos paneles en captura de eventos de ventana,
antes de los manejadores interiores. Nueva prueba a 390 y 680 px: Escape desde la
última opción enfocada, clic real sobre el fondo, reapertura y borrador intacto;
aprobada junto a la prueba móvil previa, tipos y ESLint. La reproducción y aceptación
en la sesión Edge del usuario siguen pendientes; no se atribuye causa confirmada.

Tercera revisión tras confirmación de persistencia en ambos paneles: reemplazados
los diálogos nativos móviles por PrototypeDrawer, compartido, con portal fuera del
área de trabajo, fondo explícito, cierre por pointerdown exterior y Escape en captura.
Confinamiento de Tab/Shift+Tab, fondo inert y bloqueo/restauración de desplazamiento;
los menús cerrados mantienen su estructura oculta para preservar recorridos existentes.
La llamada pública de localhost desde Windows confirmó que el servidor entrega los
ajustes, sin inspeccionar la sesión privada de Edge. 30 pruebas Chromium aprobadas
incluidas capturas, tipos/ESLint correctos; validación visual local realizada.
Nueva señal visible en Secciones: «Escape o clic en el fondo para cerrar».
Pendiente aceptación del cierre en la ventana Edge del usuario; no se afirma haber
reproducido ni determinado la causa del fallo original en esa sesión.


## Aceptación asistida de navegación — 24/10/2026

El usuario confirma OK en el recorrido reiniciado: estado inicial pendiente,
habilitación de EIPD con fundamento, Atrás/Adelante con contexto y borrador,
guardado separado de riesgos y medidas, retirada/restauración de aplicabilidad
sin pérdida, infancia independiente, aislamiento de evaluaciones, coexistencia
de EIPD e infancia, cierre de ambos paneles móviles con Escape/clic exterior,
cambio de módulo conservando borrador, cancelar contexto/reinicio/salida y
Continuar en la sección recordada. Incidencia de cierre aclarada por el usuario:
Escape cierra el panel abierto y vuelve al formulario, no al menú principal;
clic exterior significa fondo sombreado, no espacio vacío dentro del panel.
Dos navegadores mantienen copias de prueba independientes; no hay sincronización.

Usuario acepta la navegación probada y autoriza commit/push de estos resultados.
Documentos guardados, anexos, resoluciones, historial y descargas se difieren
expresamente para la validación de la navegación conectada al servidor. Esta
aceptación de diseño no acredita persistencia, permisos o aceptación jurídica.
Solicita proceder con la integración de navegación al producto conectado.
