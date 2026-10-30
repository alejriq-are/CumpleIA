# Guía del espacio de trabajo conectado

Referencia: 29/10/2026, código publicado `41c561b78e7b4d96994d927b86422d7d9efed5d1`.
Documentación del bloque 13; aceptación integral pendiente en el [checklist de cierre](cierre-navegacion-checklist.md).

## Dónde trabajar

Abre `/dashboard/trabajo`. La franja indica «Espacio conectado al servidor».
`/dashboard/maqueta` es la maqueta de referencia: sus ejemplos y guardados temporales no son los registros del servidor.

El **Menú** cambia de módulo. **Secciones** muestra los destinos del módulo cuando el ancho requiere un panel lateral. En una ventana amplia esos destinos aparecen en la barra superior. El área central contiene el formulario o la consulta del destino seleccionado.

| Necesito | Dónde está | Qué hace | Qué conserva |
| --- | --- | --- | --- |
| Retomar trabajo | Panel principal → Continuar en… | Abre el destino recordado y su contexto de esta visita; no determina el próximo paso jurídico. | Los formularios pendientes de la pestaña. |
| Elegir trabajo existente | Cambiar contexto | Selecciona organización, tratamiento, finalidad y evaluación existentes según el módulo. Aplicar cambia el contexto; Cancelar mantiene el actual. | Los pendientes quedan en sus formularios originales, sin copiarse a la nueva evaluación. |
| Leer la selección completa | Ver contexto completo | Muestra nombres y evaluación sin aplicar cambios. | La selección y los formularios. |
| Encontrar cambios sin guardar | Ver pendientes (N) | Lista unidades de trabajo y permite volver a su destino/contexto. Los siete pasos EIPD cuentan como una unidad. | Abrir el listado o un pendiente no guarda. |
| Responder el cuestionario | Autodiagnóstico → Cuestionario | Presenta las 50 preguntas reales distribuidas por secciones. N/A es una respuesta válida. | Las respuestas pendientes al navegar dentro de esta visita; usar su guardado para persistirlas. |
| Mantener una actividad RAT | Inventario de tratamientos → actividad → Información general y demás secciones | Edita el registro del inventario. | Guardar persiste el registro; no sustituye automáticamente el alcance ya asociado a una evaluación. |
| Abrir o crear una evaluación | Bases de licitud → Preparar → Evaluaciones y creación de borrador | Abrir una guardada cambia el trabajo seleccionado. Crear borrador registra una evaluación nueva. | Cancelar creación conserva los campos de preparación durante la visita; no crea la evaluación. |
| Determinar EIPD e infancia | Bases de licitud → Preparar → Determinar aplicabilidad | Guarda las dos determinaciones y sus fundamentos en una revisión de aplicabilidad. | Antecedentes anteriores y borradores; cada tema se determina por separado aunque el guardado sea conjunto. |
| Consultar aplicabilidad reciente | Consultar última determinación guardada | Lee el servidor, actualiza accesos y compara con las ediciones pendientes. No guarda, no recarga el RAT ni sincroniza ventanas. | El borrador pendiente; con formulario limpio puede cargar lo consultado. |
| Completar la EIPD general | Bases de licitud → Completar EIPD | Abre el editor cuando corresponde según la determinación guardada asociada y los controles del servidor. | Un solo documento compartido entre sus siete pasos. |
| Completar infancia | Bases de licitud → Infancia y adolescencia → Completar infancia y adolescencia | Edita los antecedentes de infancia cuando la determinación guardada lo permite. | Su contenido guardado es distinto de una versión documental histórica registrada. |
| Crear una versión de infancia | Infancia y adolescencia → Preparar nueva versión documental de infancia | Prepara, previsualiza y permite registrar explícitamente una versión nueva. | Las anteriores son inmutables; copiar o previsualizar no crea un registro. |
| Leer, revisar o decidir | Bases de licitud → Documentos guardados, grupo Revisar y decidir | Consulta el documento exacto; en infancia permite elegir revisión o decisión cuando sus requisitos lo permiten. | El original y los eventos asociados a cada versión. |
| Consultar o descargar antecedentes | Bases de licitud → Historial y descargas | Consulta antecedentes disponibles y descarga el formato ofrecido. | El JSON no contiene los archivos anexos: estos se descargan por separado. |
| Mantener datos de la organización | Mi organización | Trabaja sobre la organización, no sobre una evaluación EIPD. | Los registros guardados de esa organización. |

## Leer el contexto antes de editar

La organización identifica a quién pertenece el trabajo. El tratamiento es la actividad del RAT. La finalidad indica para qué se usan los datos dentro de esa actividad. La evaluación tiene su propio número y estado.

Panel principal y Mi organización trabajan a nivel de organización; Inventario añade el tratamiento; Bases de licitud añade finalidad y evaluación. El autodiagnóstico corresponde a la organización: no se convierte en una evaluación EIPD por tener otra selección abierta.

Cada pestaña mantiene su selección y sus borradores de la visita. Copiar una URL permite seleccionar los registros identificados en ella, sujeto a permisos; no transfiere campos sin guardar. Guarda antes de recargar. Una pestaña nueva consulta registros persistidos, no recupera la preparación temporal de otra.

## Completar y guardar la EIPD

| Paso | Destino |
| --- | --- |
| 1 | Tratamiento y alcance de la EIPD |
| 2 | Necesidad y proporcionalidad |
| 3 | Describir riesgos |
| 4 | Valorar riesgos |
| 5 | Medidas de mitigación |
| 6 | Fuentes y evidencias |
| 7 | Riesgo residual y seguimiento |

El número del paso indica ubicación, no porcentaje de cumplimiento ni aprobación.
**Guardar borrador EIPD** actualiza el documento de la evaluación seleccionada. **Ver vista previa EIPD** no guarda. **Documentos guardados** lee únicamente lo persistido.
La vista previa presenta los campos documentales; las Notas del borrador EIPD del editor no se muestran en ese contenido preparado. Para comprobar una edición pendiente en la vista previa, usa un campo documental como Finalidad del tratamiento.

La valoración estructurada tiene su propia acción de guardado: antes hay que guardar los cambios del documento que utiliza como base.

Si aparece **EIPD: disponibilidad** o **Infancia y adolescencia: disponibilidad**, abre su explicación. Un resultado pendiente, información insuficiente, «No corresponde», falta de asociación actual o error de consulta no equivale a un editor habilitado. El mensaje y el servidor determinan la condición; escribir «Corresponde» sin guardar no habilita el acceso.

## Dónde subir y consultar anexos

Para subir archivos usa **Preparar → Anexos de respaldo**. **Valorar riesgos** muestra la valoración y **Documentos guardados → Consultar valoración y anexos** permite consultar lo guardado; esas consultas no sustituyen el formulario de carga.

Si el formulario está bloqueado, guarda primero los cambios del documento asociado y comprueba que la evaluación esté cargada, editable y admitida por el servidor. Completa referencia, descripción, sección relacionada, archivo válido y declaración ficticia; los códigos de riesgos y medidas se usan cuando corresponda.

En el espacio conectado se admiten PDF o TXT UTF-8, hasta 2 MiB por archivo y 20 MiB/50 anexos por evaluación. El servidor conserva los archivos y sus versiones. En la maqueta de referencia se conservaba solo el nombre: son comportamientos distintos. Un archivo adjunto no acredita por sí mismo evidencia suficiente ni verificación de una medida.

Sigue pendiente mejorar la presentación de ciertos errores y la disponibilidad del botón ante archivos inválidos (LIC-UX-014); la validación no debe darse por superada por el aspecto del botón.

## Qué persiste cada acción

| Acción | Objeto y efecto | No implica |
| --- | --- | --- |
| Crear borrador | Nueva evaluación de una finalidad, con número asignado por servidor. | Nueva versión histórica del documento de infancia. |
| Guardar determinación | Nueva revisión de aplicabilidad para la evaluación y alcance asociados. | Nueva evaluación, aprobación o guardado de las notas EIPD. |
| Guardar borrador EIPD | Actualización del documento editable de la evaluación. | Registro de una versión documental inmutable o revisión formal. |
| Guardar antecedentes de infancia | Actualización de los antecedentes editables. | Registro de otra versión documental de infancia. |
| Preparar nueva versión a partir de esta | Copia a una preparación temporal; pide elegir si ya hay preparación que reemplazar. | Modificar el original o guardar en servidor. |
| Registrar nueva versión documental ficticia | Nuevo registro histórico de infancia con identidad propia. | Heredar revisión o decisión del original. |
| Registrar revisión documental | Resultado y fundamento sobre una versión exacta de infancia. | Modificar su contenido o decidir por la organización. |
| Registrar decisión de la organización | Decisión sobre una versión exacta, con facultad y material admitidos. | Confirmar o activar EIPD. Ser administrador no concede esa facultad. |

El **Nombre de la edición (texto libre)** es una ayuda para reconocerla, no un número de versión ni un identificador del servidor. La referencia del documento también es distinta del identificador interno. Consulta el [ciclo documental](ciclo-documental-eipd.md) y el [glosario](glosario-funcional.md).

El circuito formal de versiones, revisión y decisión de infancia está integrado con sus límites. El circuito formal completo del borrador EIPD general todavía no lo está. Confirmación y activación EIPD permanecen bloqueadas en el piloto.

## Teclado, paneles y recuperación

- Tab y Mayús+Tab recorren controles; el contorno visible indica el foco. Enter o Espacio activan el control enfocado.
- Escape cierra un panel o desplegable abierto y devuelve el foco a su control de apertura. Con el formulario abierto y sin panel, Escape no es una orden para volver a Secciones ni al menú principal.
- Hacer clic fuera significa pulsar el fondo atenuado fuera del panel. Un espacio vacío dentro del panel no lo cierra. También están disponibles Cerrar menú, Cerrar secciones o el cierre del detalle correspondiente.
- En ventana estrecha usa Menú para módulos y Secciones para destinos del módulo. Al ampliar la ventana los destinos pueden pasar a la barra; comprueba que el foco siga visible.
- Ante error de conexión, restablece la red y reintenta la consulta en la misma pestaña. El reintento no guarda ni descarta cambios. No interpretes una consulta fallida como ausencia de registros.
- Ante sesión ausente o expirada, usa Iniciar sesión en otra pestaña con la misma cuenta. Conserva la original abierta y después reintenta allí. La pestaña de autenticación no recupera los borradores de la original.
- En el cuestionario, Siguiente requiere responder la sección completa; una sola respuesta N/A no completa las demás preguntas. Cuestionario permite ir a otra sección conservando lo escrito durante la visita.

La prueba manual con lector de pantalla sigue pendiente; estos recorridos no constituyen certificación de accesibilidad.

## Referencias de implementación

Los nombres, rutas y condiciones se contrastan con [destinos](../../frontend/components/navigation/connected-destinations.ts), [navegación](../../frontend/components/navigation/connected-navigation.ts), [disponibilidad](../../frontend/components/navigation/connected-availability.ts), [pasos EIPD](../../frontend/lib/licitud/eipd-steps.ts) y [flujo documental](../../frontend/components/licitud/AssessmentFlow.tsx). Ante una discrepancia, verificar código y contrato del servidor antes de modificar la guía o el producto.

## Rutas para soporte y comprobación

Los siguientes fragmentos van después de `/dashboard/trabajo`; conservan los parámetros de contexto que la aplicación haya añadido. No escribir identificadores inventados ni usar nombres como identificadores.

| Destino | Fragmento |
| --- | --- |
| Panel principal | `#/panel/resumen` |
| Cuestionario / resultado | `#/diagnostico/cuestionario` / `#/diagnostico/resultados` |
| Inventario | `#/rat/catalogo` |
| Evaluaciones y creación de borrador | `#/licitud/catalogo` |
| Determinar aplicabilidad | `#/licitud/aplicabilidad` |
| Alcance / base y fundamento | `#/licitud/alcance` / `#/licitud/base` |
| Editor EIPD | `#/licitud/eipd` con `step=0` a `step=6` en sus parámetros |
| Anexos de respaldo | `#/licitud/anexos` |
| Infancia / preparación de versión | `#/licitud/infancia` / `#/licitud/preparar` |
| Documentos guardados / historial | `#/licitud/revisar` / `#/licitud/historial` |

Abrir una ruta no elude los controles de permiso, estado, aplicabilidad o material del servidor.
