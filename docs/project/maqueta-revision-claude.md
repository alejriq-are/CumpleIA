# Revisión de Claude: validación, implementación y oportunidades para CumpleIA

Fecha: 24 de octubre de 2026. Base revisada: a9d3ab4.
Rama de implementación: feature/maqueta-navegacion-review.
Ruta de revisión: /dashboard/maqueta.

## Conclusión

La revisión de Claude es útil y sus hallazgos principales se confirman en el código
base. Su informe declara correctamente que no ejecutó la maqueta: las alturas,
la facilidad de uso y ciertos comportamientos móviles eran hipótesis, no fallos
observados. Se conserva esa distinción. El usuario aprobó la propuesta visual;
la nueva implementación requiere todavía su recorrido de aceptación.

Se implementó el patrón aprobado sobre los componentes reales de la maqueta:
menú oscuro agrupado, contexto compacto con diálogo Cambiar, opciones por intención,
migas navegables y ubicación móvil persistente. Se mantuvieron todos los formularios,
consultas, anexos, resoluciones, descarga y bloqueos existentes.

El HTML recibido no es una implementación integral: deja Autodiagnóstico,
Inventario y Mi organización como pantallas de ubicación; su formulario genérico
ofrece guardar una preparación, y su reinicio no conserva la confirmación original.
Se adoptó su diseño, pero no se sustituyó con ese código el flujo ya probado.
En infancia, Preparar resolución documental queda primero dentro de Preparar,
para conservar la facilidad de encontrar esa acción validada en el recorrido anterior.

## Resolución de los hallazgos altos

| ID | Validación del hallazgo | Resolución aplicada y evidencia |
|---|---|---|
| A1 | Confirmado: ubicación solo en estado y enlace de salida sin confirmación. | Fragmento validado con módulo/tarea/sección y evaluación ficticia; Atrás/Adelante restauran ubicación y contexto sin borrar datos. El enlace Salir confirma pérdida de la visita; beforeunload cubre recarga/cierre según el navegador. Se protege también lo guardado, porque sigue siendo memoria temporal. Casos automatizados de historial, enlaces y cancelación de salida. |
| A2 | Confirmado: se conservaba el texto, pero se abría el primer paso. | Se recuerda la ubicación por módulo y por evaluación. Regresar a Bases de licitud desde otro módulo devuelve a la última sección válida. Caso dirigido aprobado. |
| A3 | Confirmado: Continuar siempre iba a Base. | El botón nombra y abre el último destino real de la evaluación. Sin historial, se presenta como tarea sugerida. Caso Medidas → Autodiagnóstico → Bases → Panel → Continuar aprobado. |
| A4 | Confirmada la repetición; la altura original citada por Claude era estimada. | Se elimina la acumulación de cabeceras, tarjeta repetida, selector desplegado y pies repetidos. Contexto en una línea y diálogo; un título de pantalla. En la nueva maqueta, cabecera ~95 px a 1024×768 y selector visible (Y ~321 px en la medición). También se verificó visibilidad del primer campo a 1366×768. No se atribuye una reducción porcentual sin medición equivalente del antes. |

## Resolución de los hallazgos medios

| ID | Validación | Resolución |
|---|---|---|
| M1 | Confirmado que el acceso móvil no mostraba ubicación y las secciones quedaban arriba. | Barra fija móvil con Menú, módulo/sección y Secciones. Desde el final del formulario se puede abrir la navegación; prueba a 390 px. |
| M2 | Riesgo confirmado por flex-wrap; el tamaño original era una hipótesis. | Bases de licitud utiliza Alcance, Preparar, Revisar y decidir, Historial y descargas. Menú lateral compacto con iconos, nombres accesibles y títulos entre 768 y 1100 px. Prueba de cabecera ≤120 px a 1024. |
| M3 | Confirmado: la frase genérica no describía algunas acciones. | Etiquetas Editar, Consulta, Preparación, Revisión y Decisión en destinos; descripción por capacidad de la sección. La revisión de adultos se anuncia como acceso previsto sin registro; la de infancia conserva el registro simulado. Bloqueo por facultad revocada intacto. |
| M4 | Confirmado: se ofrecía guardar donde solo se podía abrir vista previa. | Preparación se describe como borrador temporal, sin promesa de guardado; conserva vista previa y segundo diálogo de registro. El menú usa Borrador temporal. |
| M5 | Confirmado: estado visible solo al abrir algunos grupos. | Indicador agregado en cada disparador con texto accesible y número de secciones pendientes. El detalle conserva el estado por destino. |
| M6 | Confirmado: migas decorativas. | Inicio lleva al Panel y el módulo a su primera sección explícita. La sección actual permanece como texto. Prueba de Inicio aprobada. |
| M7 | Confirmadas diferencias de nombres y duplicación de resultados/informe. | Destinos comparten nombres con el título; se conserva el vocabulario completo de CumpleIA. Informe muestra ahora una estructura ilustrativa distinta de Resultados. No se inventa un informe calculado. RAT se explica en el selector. |
| M8 | Confirmados los puntos de código; no se había observado un teléfono real. | Cajón principal móvil con diálogo nativo y gestión de foco; panel Secciones y desplegables con Escape/clic exterior; resize cierra solo al cambiar el ancho; relleno de foco; funciones futuras con aria-disabled, foco y mensaje; aria-current=page. Pruebas de teclado, alto móvil y foco. La comprobación en un teléfono real y lector de pantalla sigue pendiente. |

## Resolución de los hallazgos bajos

| ID | Resolución y límites |
|---|---|
| B1 | Dos accesos de salto al inicio de la maqueta: contenido y secciones. Se reduce el número de controles anteriores al formulario ocultando los selectores en Cambiar contexto. No se afirma un conteo de tabulaciones universal. |
| B2 | En la maqueta se oculta visualmente la cabecera real duplicada mediante estilo acotado y se ofrece Salir con confirmación. La autenticación del dashboard se mantiene en el servidor. El resto del dashboard conserva su cabecera. |
| B3 | Reinicio indica las cuatro evaluaciones y mantiene confirmación. |
| B4 | Cancelar y conservar mi borrador sustituye la etiqueta ambigua. |
| B5 | Se retira la flecha de enlace externo en accesos a detalles de la maqueta; siguen siendo botones con diálogo. Preferencia visual pendiente de aceptación del usuario. |
| B6 | Etiquetas cortas de finalidad y versión; frase completa y nombre de evaluación en el diálogo. Versión siempre visible en la barra de contexto. |
| B7 | Cambiar contexto muestra pendientes de la evaluación actual; las opciones de evaluación indican pendientes. Cancelar no cambia el contexto. Los datos de las otras evaluaciones se conservan. |
| B8 | Se mantiene explícitamente que el Autodiagnóstico es ilustrativo. Las 50 preguntas, los nombres de sus secciones y avance respondidas/total deben provenir del catálogo real al integrar. No se inventan preguntas ni se calcula avance real con campos ilustrativos. Pendiente de integración, no defecto resuelto mediante contenido ficticio. |
| B9 | Avance documental expresa secciones guardadas / secciones del módulo; excluye la preparación que no usa Guardar. No equivale a cumplimiento ni aprobación. |

## Condiciones del proyecto preservadas

- Demostración sin acceso desde sus componentes a las APIs o expedientes reales.
- Borradores y guardados separados por evaluación; datos de organización comunes
  únicamente dentro de la organización ficticia. El selector no crea evaluaciones.
- Confirmaciones de copia, vista previa, registro y reinicio conservadas.
- Versiones previas, motivo del nuevo registro y contenido histórico intactos.
- Anexos PDF/TXT validados; la maqueta conserva el nombre, no carga el archivo.
- Revisión documental y decisión organizacional separadas. Facultad revocada bloquea
  nuevas decisiones. Confirmación y activación EIPD siguen deshabilitadas.
- Sin nuevas dependencias, migraciones, permisos, credenciales o almacenamiento local.
- Las direcciones solo incluyen identificadores de fixtures, nunca el contenido escrito.

## Verificación y límites de evidencia

Se ejecutó la suite de 25 pruebas Chromium de la maqueta, incluida generación de
capturas de escritorio y móvil. Se aprobaron tipos y ESLint. Se inspeccionaron
capturas de Infancia, cajón móvil y contexto. La suite aborta peticiones externas
a los componentes; no utiliza cuentas ni expedientes reales.

La medición de altura corresponde a esta maqueta y esos tamaños de ventana.
No es una medición de tiempos de tarea ni una prueba de usabilidad con usuarios.
La revisión del usuario y la CI remota del candidato siguen pendientes.

El historial interno funciona entre secciones y evaluaciones. Al abandonar el
historial propio, cerrar o recargar, la protección nativa depende del navegador;
no reemplaza persistencia del servidor ni garantiza recuperación después de cierre.
La maqueta sigue reiniciándose al recargar. No se ha validado en un teléfono físico.

## Oportunidades de mejora del proyecto

1. **Adoptar un marco de navegación común en el producto conectado.** Reutilizar menú,
   migas, contexto y metadatos de destinos en Panel, Autodiagnóstico, RAT y Licitud.
   Evitar mantener dos cabeceras con comportamientos distintos. Hacerlo después de
   aceptar la maqueta y con comprobaciones de autorización en servidor.
2. **Tratar el contexto como una identidad de trabajo.** Usar organización → tratamiento
   → finalidad → evaluación con relaciones autorizadas. Recordar la ubicación por
   evaluación y separar caché/borradores/guardados/anexos/descargas. Una URL no concede
   permisos ni justifica copiar datos entre versiones.
3. **Distinguir estado de edición, estado documental y estado jurídico.** Pendiente,
   guardado, registrado, revisado y decisión son conceptos diferentes. Centralizar
   etiquetas y acciones disponibles; evitar que un indicador de avance se interprete
   como aprobación o habilitación EIPD.
4. **Integrar los formularios reales con contratos verificables.** Para Autodiagnóstico,
   reutilizar las 50 preguntas y secciones del catálogo del servidor, opciones y cálculo
   determinista existente. Incorporar progreso real y acceso a pendientes. Para
   consentimiento/LIA y riesgos, resolver sus contratos y backlog por separado, sin
   atribuir a la maqueta el desarrollo ya terminado.
5. **Persistencia y recuperación antes de ampliar funcionalidad.** En la versión conectada,
   comprobar guardado/reapertura/recarga, concurrencia y versiones. La protección de
   salida es un complemento, no un mecanismo de conservación. Mantener historia
   inmutable y procedencia de los respaldos.
6. **Definir un sistema pequeño de diseño y pruebas de navegación.** Nombres únicos,
   variantes de botones/avisos/menús, foco y teclas comunes. Mantener pruebas de rutas,
   aislamiento y permisos junto con capturas a tamaños representativos; no depender
   solo de capturas ni duplicar pruebas puramente cosméticas.
7. **Medir la facilidad de uso antes de adoptar.** Recorrido breve con tareas concretas:
   encontrar resolución, volver a Medidas, cambiar evaluación sin mezclar datos y abrir
   Secciones desde el final en móvil. Registrar éxito, clics, retrocesos y dudas; no
   presentar la opinión de un revisor como una mejora cuantificada.

Prioridad propuesta: aceptar navegación → integrar contexto y cuestionario real →
validar conservación/aislamiento del servidor → completar formularios pendientes.
No se autoriza por este informe un merge, despliegue o activación EIPD.

## Recorrido de aceptación sugerido

1. Bases de licitud → Preparar → Base y fundamento; escribe un ejemplo.
2. Preparar → Medidas de mitigación; pulsa Atrás y Adelante del navegador.
3. Abre Autodiagnóstico y vuelve a Bases: debe regresar a Medidas.
4. Panel → Continuar: debe nombrar y abrir Medidas.
5. Cambiar contexto → otra finalidad: confirma; vuelve y comprueba el borrador.
6. Programa con menores → Preparar resolución documental: vista previa y cancelación.
7. En ventana estrecha, baja al final y abre Secciones y Menú, cerrando con Escape.
8. Prueba Salir y elige Seguir en la maqueta.

Fuente aportada: informe-revision-navegacion-a9d3ab4.md. SHA-256: fa39dac28168f57a240c2517be584a85ec4a7c38b3c1a20d847d08f45418219d.

Fuente aportada: propuesta-navegacion-cumpleia.html. SHA-256: b2cd65a802b951a2a8333272105710ddb0c3504d98a0809c3511232fb2dc7255.

