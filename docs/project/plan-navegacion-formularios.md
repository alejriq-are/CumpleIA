# Plan de navegación y formularios: lotes 6–13

Fecha: 26 de octubre de 2026. Base funcional: `2e3f5460190185413f6e85243ad59958ba148463`.

Estado al 26/10/2026: **6A aceptado con el alcance asistido documentado; commit/push autorizado el 26/10/2026**. Los demás sublotes no se han iniciado. La autorización del usuario para continuar 6A sucede a la publicación documental del plan en d42b2e9. [Análisis, decisiones P1–P13 y glosario G01–G30](evaluacion-propuestas-claude.md).

## 1. Alcance y secuencia

Se conservan los lotes pendientes **6: menús y nombres; 7: accesibilidad; 8: simplificación visual**. Se amplían sus criterios con las propuestas aceptadas de Claude, sin volver a abrir las correcciones ya aceptadas de los lotes 1–5. Los trabajos nuevos se separan a partir del lote 9.

Cada sublote tiene implementación, comprobaciones dirigidas, recorrido asistido y cierre propios. No se ejecutan dos sublotes juntos por comodidad si eso dificulta reconocer el origen de una regresión. Una propuesta aceptada en el análisis todavía no es una mejora validada en uso.

| Orden | Sublote                              | Resultado que verá el usuario                                                                         | Prioridad        | Dependencia                                             |
| ----- | ------------------------------------ | ----------------------------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------- |
| 1     | 6A. Destinos y nombres               | Un mismo destino conserva su nombre; los accesos con un destino no obligan a desplegar.               | Alta             | Base actual y matriz de nombres.                        |
| 2     | 6B. Orientación documental           | Se distingue preparar, guardar, registrar y consultar; los accesos no disponibles explican su razón.  | Alta             | 6A; verificar contrato por objeto.                      |
| 3     | 7A. Teclado en navegación            | Apertura, selección, cierre y retorno del foco previsibles.                                           | Alta             | 6A–6B.                                                  |
| 4     | 7B. Estructura y ayudas accesibles   | Pantalla y controles con nombres correctos; ayuda disponible con teclado y táctil.                    | Alta             | 7A.                                                     |
| 5     | 8A. Cabecera y contexto              | Más área útil; contexto legible sin duplicar el mismo resumen.                                        | Alta             | 7B para no ocultar información inaccesible.             |
| 6     | 8B. Pasos y ventanas estrechas       | Una navegación principal por tamaño; sin segunda lista de los siete pasos en el formulario conectado. | Alta             | 7A–7B y 8A.                                             |
| 7     | 9A. Inventario de cambios            | Se identifican unidades reales con cambios y su contexto.                                             | Alta             | Contrato explícito de unidades; no deducir de pasos.    |
| 8     | 9B. Volver al trabajo pendiente      | Se encuentra el formulario pendiente y se entiende qué ocurrirá al cambiar contexto.                  | Alta             | 9A y guardas de aplicabilidad.                          |
| 9     | 10A. Capacidades por documento       | Se entiende qué admite cada documento y por qué una acción está bloqueada.                            | Alta             | Nombres 6B, roles y contratos actuales.                 |
| 10    | 10B. Historial y revisión orientados | Documento, versión, revisión y decisión permanecen vinculados y localizables.                         | Media            | 10A.                                                    |
| 11    | 11A. Ayudas para completar           | Campos y acciones críticas explican formato, propósito y requisitos sin avisos repetidos.             | Alta             | Glosario y acciones 6B.                                 |
| 12    | 11B. Crear frente a seleccionar      | Crear evaluación no se confunde con cambiar la evaluación en que se está trabajando.                  | Media            | 9B; contrato de creación existente.                     |
| 13    | 12A. Diagnóstico y retorno           | Progreso real, retorno y salidas aún ambiguas comprobados por tarea.                                  | Media            | Navegación estabilizada.                                |
| 14    | 12B. Recuperación y sesión           | Fallo temporal y sesión ausente tienen orientación coherente conservando borradores.                  | Alta             | Seguimiento del lote 1, aislado de cambios visuales.    |
| 15    | 13. Guía y aceptación integral       | Guía y glosario corresponden a lo implementado; evidencias y pendientes quedan claros.                | Alta para cierre | Sublotes aceptados; documentación incremental en todos. |

La prioridad no obliga a iniciar simultáneamente. Si un fallo de recuperación impide validar los primeros sublotes, adelantar únicamente 12B como corrección aislada y documentar la razón. Si no hay fricción comprobada en una hipótesis, se conserva el comportamiento y se registra el resultado; no se reorganiza por cumplir la lista.

## 2. Condiciones comunes

- Trabajar sobre el espacio conectado `/dashboard/trabajo`. La maqueta `/dashboard/maqueta` sigue siendo referencia y conserva los comportamientos independientes que usen componentes compartidos.
- Mantener rutas, identificadores y enlaces anteriores. Cambiar rótulos no traduce claves de API, enums ni nombres de tablas. Probar enlaces directos y Atrás/Adelante por secciones.
- Mantener contexto por módulo, organización y aislamiento. Una ventana puede tener otra selección; este plan no introduce sincronización ni guardado automático entre ventanas.
- No recargar una pestaña con borradores pendientes para validar cambios visuales. Usar sesión de prueba independiente o guardar explícitamente cuando la tarea lo indique. No asumir que lo no guardado reaparece en otra ventana.
- No desmontar editores con cambios por ocultar un panel o retirar navegación duplicada. No copiar contenido entre evaluaciones o documentos.
- Conservar diferencia entre limpio, sin guardar, guardado, completo, revisado, aceptado y autorizado. Un punto verde, un número de paso o una consulta exitosa no prueba los otros estados.
- Mantener las guardas del servidor: rol, estado, organización, contexto, facultad y concurrencia. Conservar piloto ficticio y confirmación/activación EIPD bloqueadas.
- Cambios de datos de prueba solo en recorridos identificados. Consultar/abrir/cerrar no debe enviar escrituras de dominio. Guardar determinación y registrar versiones pueden generar registros; no repetirlos para comprobar un aviso.
- Cada cambio lleva pruebas adecuadas al comportamiento afectado; no una nueva batería completa por una edición documental o una cadena aislada. Tipos, formato y lint para código afectado; ampliar regresión ante nuevos cambios o fallos. No atribuir pruebas manuales al usuario que no haya ejecutado.
- Codex mantiene el trabajo de implementación y validación. Claude es una fuente de revisión externa; no participa en ejecución ni recibe acceso a datos por este plan. Commit/push de esta documentación o de nuevos sublotes se realizará con autorización aplicable; no hay merge ni despliegue incluidos.

## 3. Lote 6 — Menús, nombres y orientación

### 6A. Un destino, un nombre

**Resuelve:** P7, parte de P2/P12; G15/G17/G28/G30; pendientes previos de coherencia de menús.

**Cambios acotados:**

1. Inventariar destinos reales de los módulos conectados y definir una configuración común de rótulo por destino. Incluir título, miga y texto del enlace; conservar nombre de grupo cuando agrupa operaciones diferentes.
2. Para `revisar`, usar pantalla «Documentos guardados» dentro del grupo «Revisar y decidir». No cambiar la clave `revisar` ni perder destinos internos.
3. Presentar enlace directo cuando el grupo tenga un solo destino accionable y no requiera elegir entre alternativas. Mantener desplegable para varios destinos. La misma ruta no puede exigir un clic adicional solo por estar en otro módulo.
4. Señalar destino actual de forma visual y accesible. Resolver el caso grupo activo/paso activo sin confundirlo con cambios sin guardar.
5. Iniciar diccionario acotado de textos de navegación por significado. No centralizar todos los textos del producto en esta entrega.

**Archivos orientativos:** ConnectedWorkspace, connected-navigation, Secciones y pruebas conectadas. Antes de tocar un componente compartido, identificar sus usos en la maqueta.

**Aceptación:**

- [ ] Mismo nombre para la pantalla en menú, miga y título.
- [ ] Acceso de un destino abre con una activación y conserva URL/contexto.
- [ ] Grupos múltiples siguen mostrando todos sus destinos.
- [ ] Activo reconocible sin depender solo del color.
- [ ] Volver a EIPD conserva la nota pendiente en la misma evaluación.
- [ ] Enlaces previos y Atrás/Adelante llegan al mismo destino lógico.

**Guion con usuario:** desde Panel → Inventario → ficha seleccionada; abrir Documentos guardados desde Bases de licitud y regresar. Comparar nombres y cantidad de pasos; no guardar datos.

**Ejecución 26/10/2026:** implementación local en feature/navegacion-6a-destinos sobre d42b2e9.
51 escenarios conectados (5 nuevos), 20 del flujo independiente y 18 de maqueta de referencia
aprobados; tipos/lint/formato y revisión visual correctos. Aceptación asistida acotada registrada el 26/10/2026, incluida la glosa ajustada.
La captura estrecha antigua no prueba nombres nuevos; las pruebas controladas no se atribuyen al usuario.
[Evidencia y recorrido](navegacion-servidor.md#bloque-6a--destinos-coherentes-y-accesos-directos).
Sin commit/push nuevo; no se inicia 6B.

### 6B. Operaciones documentales y disponibilidad

**Resuelve:** P10/P11 y parte de P2; G04–G08, G10/G16/G18/G20/G24. Conserva mejoras de lotes 3–5.

**Cambios acotados:**

1. Usar «Resultado de la revisión documental» y «Decisión de la organización» acompañados de su objeto cuando sea necesario.
2. En el circuito de infancia, aclarar «Versión registrada del documento de infancia» y «Preparar nueva versión a partir de esta». La acción final de registro se distingue de la preparación temporal. Conservar referencias/documentos históricos y correspondencia con «resolución».
3. Validar «Nombre de la edición (texto libre)» en los pocos campos actualmente llamados etiqueta; ayuda: no asigna el número de versión ni crea otra evaluación. Mantener campo Referencia separado.
4. Alinear nombres de los siete destinos EIPD. Comprobar que «Describir riesgos» representa el contenido del paso 3 antes de adoptarlo frente a «Valorar riesgos» del paso 4. No fusionar pasos ni añadir otro menú.
5. Donde una opción condicionada no esté disponible, ofrecer una fila informativa con razón y orientación a Determinar aplicabilidad, sin enlace habilitado al editor bloqueado. Preservar la diferencia entre falta de determinación, No corresponde, información insuficiente, asociación por revisar y error de lectura.
6. Mantener nombres recientes aceptados: consulta de determinación, revisión de aplicabilidad, fundamentos y conceptos comparativos.

**Aceptación:**

- [ ] El usuario explica que preparar no registra, guardar EIPD no crea versión y aceptar no activa.
- [ ] Una EIPD Corresponde guardada/asociada permite abrir el editor; una edición no guardada no cambia ese permiso.
- [ ] Infancia depende de su propia decisión guardada, independientemente de EIPD.
- [ ] No corresponde y asociación por revisar muestran razón; carga/error no aparecen como una negativa de negocio.
- [ ] Nombre manual de edición no se presenta como ID ni secuencia asignada.
- [ ] No se modifican documentos históricos, valores API ni reglas de habilitación.

**Guion con usuario:** leer las acciones sobre una versión existente sin registrar otra; explicar qué ocurriría al prepararla. Comprobar disponibilidad con fixtures independientes y guardar solo cuando el guion identifique expresamente una escritura ficticia.

## 4. Lote 7 — Teclado, foco y estructura accesible

### 7A. Navegación con apertura y cierre previsibles

**Resuelve:** P7/P12, parte de P13 y accesibilidad pendiente del lote 7.

**Cambios:** asegurar un solo desplegable abierto; Tab/Shift+Tab y Enter/Espacio según elemento nativo; Escape cierra y devuelve foco al control pertinente; salir de la región de navegación no deja un desplegable abierto sobre otro formulario; cierre por fondo exterior en paneles, no por clic dentro de su superficie. Conservar el comportamiento ya comprendido por el usuario: Escape cierra panel, no cambia al menú principal ni navega atrás.

No imponer `role=menu` a enlaces desplegables si el patrón es disclosure. Flechas/Inicio/Fin solo se incorporan si se define y prueba su patrón; no interceptar teclas dentro de campos.

**Aceptación:**

- [ ] Recorrido completo sin ratón, con foco visible y orden lógico.
- [ ] Escape y clic sobre fondo exterior cierran ambos paneles; clic interior conserva panel salvo selección/cierre explícito.
- [ ] Al abrir otro grupo se cierra el anterior, también con teclado.
- [ ] Tras seleccionar destino, foco y desplazamiento sitúan el área de trabajo sin ocultarla bajo cabecera.
- [ ] No aparece escritura de dominio por abrir/cerrar menús; nota pendiente permanece.

**Guion:** abrir Menú, cerrar con Escape; abrir Secciones, elegir un paso EIPD; volver a abrir y cerrar por fondo exterior. Repetir con Tab y sin tocar el contenido del formulario.

### 7B. Nombres, regiones y ayuda

**Resuelve:** E12, G22/G28 y reglas de ayuda accesible.

**Cambios:** corregir nombre accesible «Módulos de la maqueta» en uso conectado sin alterar el de referencia; resolver main anidados y etiquetar la región de trabajo; revisar título de documento, encabezados y relación de paneles con sus pestañas cuando hay navegación externa; comprobar descripciones de requisitos y ayudas con teclado/táctil/lector. No anunciar «rol de solo lectura» si la causa es otro bloqueo.

**Aceptación:**

- [ ] Un único contenido principal semántico por vista conectada, con nombre/encabezado reconocible.
- [ ] Controles y grupos tienen nombre correcto; no apuntan a encabezados ocultos o inexistentes.
- [ ] Foco no se pierde al cerrar panel o cambiar sección.
- [ ] Ayuda se abre, lee y cierra con teclado y táctil; requisito asociado al control.
- [ ] Revisión manual con lector de pantalla en los recorridos afectados, además de comprobaciones automáticas apropiadas. Si no se ejecuta, registrar pendiente; no declarar accesibilidad integral certificada.

## 5. Lote 8 — Simplificación visual

### 8A. Contexto compacto, completo cuando se necesita

**Resuelve:** P8; G16/G19; repetición y altura de cabeceras. Conserva alcance por módulo del lote 2.

**Cambios:** una cabecera principal de organización/tratamiento/finalidad/evaluación según módulo; quitar resumen duplicado de AssessmentFlow solo si recibe navegación/contexto externo equivalente; conservar su cabecera en uso independiente. Hacer accesible el texto completo de nombres largos mediante expansión o panel, no hover exclusivamente. Diferenciar contexto de trabajo y material histórico seleccionado antes de eliminar un resumen local.

Conservar una advertencia de piloto/bloqueo visible y las restricciones relevantes junto a acciones; retirar solo reiteraciones equivalentes. Separar finalidad de identificación de evaluación cuando los datos permitan hacerlo, sin inventar nombres o contenidos.

**Aceptación:**

- [ ] Panel/Organización/Autodiagnóstico muestran ámbito organizacional; RAT tratamiento; licitud su evaluación.
- [ ] Se identifica la evaluación elegida y el documento histórico, si difiere, sin mezclarlos.
- [ ] Más área útil medida contra captura previa equivalente; ningún campo o requisito desaparece.
- [ ] Nombres largos legibles completos con teclado/táctil y sin desbordamiento.
- [ ] Sin regresión de cabecera independiente o mensajes de error/permiso.

**Guion:** usuario identifica contexto, abre su detalle y vuelve al mismo campo. Comparar capturas a igual tamaño, zoom, posición y datos; no exigir que todo primer campo siempre quepa sin desplazarse.

### 8B. Una navegación principal y ubicación del paso

**Resuelve:** P11/P12; duplicación EIPD observada y registrada en backlog.

**Cambios:** retirar la segunda lista central EipdSteps únicamente en modo conectado con navegación externa; mantenerla en editor independiente. Mostrar título y «Paso N de 7» sin marcar completitud. Mantener acciones propias del formulario. En ventanas estrechas usar panel Secciones como vía principal; en ancho suficiente usar la barra. Mantener equivalencia antes de ocultar el acceso redundante de escritorio. Determinar ajuste por espacio disponible, nombres largos y zoom, no por una captura aislada.

**Aceptación:**

- [ ] Siete destinos accesibles sin segunda lista central en conectado; independiente conserva navegación.
- [ ] Paso actual y siguiente acción se entienden sin confundir paso visitado con completado.
- [ ] Menú/Secciones accesibles al desplazarse y en 320/390 px, ancho intermedio y escritorio.
- [ ] Sin desplazamiento horizontal de página ni opciones cortadas; comprobar zoom 200 % y reflujo.
- [ ] Mismos destinos condicionados, orden y cierres del lote 7; borradores y Atrás/Adelante conservados.

**Guion:** describir riesgo → valorar riesgo → medidas; volver al primero; reducir ventana, abrir Secciones y repetir. No recargar ni volver a registrar datos para esta prueba.

## 6. Lote 9 — Cambios pendientes y cambio de contexto

### 9A. Unidades de trabajo identificables

**Resuelve:** P9, G03 y alcance previo C6. Es cambio de estado de UI, no solo un aviso.

**Antes de implementar:** definir qué constituye una unidad guardable: determinación conjunta, borrador EIPD, antecedentes de infancia, preparación temporal y otros formularios reales. Siete pasos EIPD no son siete documentos. El booleano por evaluación existente no permite contar formularios exactos; ampliar el contrato de callbacks con descriptor, contexto, destino y origen real.

**Cambios:** lista de unidades con cambios sin guardar y nombre/contexto comprensibles; resumen global breve. Mantener aviso local cerca de Guardar. No identificar «guardado» por `dirty=false`: distinguir al menos sin consulta, consultando, consultado sin cambios, editado, guardando, guardado y error donde corresponda. No implementar una máquina universal que cambie los estados de dominio.

**Aceptación:**

- [ ] Dos unidades editadas muestran dos unidades reales, con identificación correcta; dos pasos del mismo borrador no duplican conteo.
- [ ] Un formulario nunca cargado no muestra ✓ guardado.
- [ ] Guardar una unidad retira solo su pendiente; las otras permanecen.
- [ ] Error, reintento o consulta no eliminan pendientes ni simulan escritura exitosa.
- [ ] Datos sensibles no se añaden a almacenamiento de navegador; la lista no persiste borradores automáticamente.

### 9B. Encontrar el pendiente y anticipar el destino

**Resuelve:** P9, G19 y C10. No cambia selección global de otras ventanas.

**Cambios:** abrir la unidad pendiente con su contexto y destino validados; si su editor está condicionado/no disponible, explicar la reubicación conservando contenido. Mostrar qué cambiará antes de Aplicar contexto cuando haya trabajo pendiente y cuál será la pantalla de destino. Permitir cancelar sin cambiar datos. Evitar cabeceras que salten de altura al alternar el aviso, sin fijar una altura que recorte texto largo.

**Aceptación:**

- [ ] Ir a un pendiente devuelve al formulario correcto, no al de otra evaluación.
- [ ] Cancelar cambio deja selección, ubicación y texto intactos.
- [ ] Aplicar informa el nuevo destino y conserva las unidades anteriores de la visita.
- [ ] Acceso bloqueado no fuerza edición ni borra la preparación temporal.
- [ ] Aviso al salir/recargar sigue funcionando; no se interpreta conservar en memoria como guardar en servidor.

**Guion conjunto del lote 9:** editar notas EIPD y determinación sin guardar, navegar a Panel, localizar cada pendiente y volver; cancelar cambio de contexto y después aplicarlo. Leer explicación antes de confirmar. Usar datos ficticios distintos por evaluación.

## 7. Lote 10 — Documentos, revisiones y decisión

### 10A. Capacidades por objeto seleccionado

**Resuelve:** P6 y G04/G05/G10–G12/G22/G23.

**Cambios:** panel breve de acciones y razones para el documento seleccionado, tomando restricciones efectivas del contrato. Diferenciar EIPD general editable, versión de infancia conservada, preparación temporal, revisión y decisión. Para cada acción visible mostrar disponibilidad por tipo, estado, material, rol y facultad cuando sean aplicables. La facultad no se infiere del rol de administrador. No incorporar revisión favorable o aceptación general inexistentes.

**Aceptación:**

- [ ] EIPD general no ofrece circuito formal de infancia por analogía.
- [ ] Versión anterior se consulta con su identidad; no se presenta como documento editable actual.
- [ ] Facultad revocada/ausente bloquea nueva decisión y conserva consulta histórica.
- [ ] Material no asociado se explica sin inventar invalidez jurídica de todo documento anterior.
- [ ] Datos aún no consultados/error no producen acciones habilitadas o falsos estados definitivos.
- [ ] Confirmación/activación permanecen bloqueadas incluso ante Acepta documental.

### 10B. Localizar revisión e historial sin perder el documento

**Resuelve:** P6, parte de P2/P5; C13; G13/G14.

**Cambios:** enlaces o anclas claras a revisión, decisión e historial del documento seleccionado; identidad/número/fecha y resultado con concepto. Mantener referencia al objeto histórico y sus asociaciones al volver. Antes de separar pantallas, validar si anclas y encabezados resuelven la tarea; no reorganizar todas las rutas sin evidencia. Los eventos disponibles no se presentan como auditoría completa.

**Aceptación:**

- [ ] El usuario encuentra la revisión de una versión concreta y la distingue de la decisión organizacional.
- [ ] Requiere cambios lleva su concepto, autoría disponible y versión; no se mezcla con otro documento.
- [ ] Cambiar versión cambia sus antecedentes de forma coherente, sin reutilizar un resultado ajeno.
- [ ] Preparar desde una anterior deja claro origen, temporalidad y nueva confirmación necesaria.
- [ ] Lectura y desplazamiento no registran revisión ni decisión.

## 8. Lote 11 — Completar formularios con menos fricción

### 11A. Ayuda localizada y verbos que explican el efecto

**Resuelve:** P1/P5, G01/G03/G06/G08/G18/G20/G23–G26 y LIC-UX-015 en alcance de comprensión.

**Cambios:** piloto en campos de tratamiento/alcance EIPD y descripción/valoración de riesgos. Indicar propósito, formato, obligatoriedad real, ejemplo ficticio y requisitos faltantes solo donde ayude. Diferenciar referencia, nombre manual de edición, secuencia del servidor y códigos solicitados. Explicar términos legales junto al campo, sin sustituirlos ni generar conclusiones legales. Conservar borrador y validación del servidor. Definir una ayuda corta reutilizable por concepto; no un gran glosario obligatorio antes de rellenar.

**Aceptación:**

- [ ] Usuario distingue qué describir y qué valorar; comprende referencia y nombre de edición.
- [ ] Ayudas accesibles y relacionadas con el campo; errores conservan valores y señalan acción correctora.
- [ ] Lo opcional no se vuelve obligatorio por el texto; los requisitos del servidor no desaparecen.
- [ ] Vista previa identifica si incluye ediciones pendientes; consultar guardado no promete incluirlas.
- [ ] Guardar indica objeto y efecto; aviso de éxito aparece junto a su acción y se retira cuando ya no corresponde.

No resolver aquí formularios completos de consentimiento/LIA, metodología de riesgo, extracción automática ni cambios de criterios jurídicos.

### 11B. Selección de trabajo frente a creación

**Resuelve:** parte de P8 y G19. Hipótesis de fricción en selector repetido.

**Cambios:** diferenciar «Trabajando en…» de «Crear evaluación para…». Comprobar si es seguro precargar una selección disponible/autorizada en el formulario de creación; si no, explicar por qué debe elegirse. No crear evaluación automáticamente ni copiar alcance de otra por coincidencia de nombre. Guardar/cancelar creación conserva pendientes independientes.

**Aceptación:**

- [ ] El usuario anticipa si cambiará una selección o creará un registro nuevo.
- [ ] Cancelar creación no altera el contexto ni crea evaluación.
- [ ] Prefill, si se implementa, usa IDs y dependencias válidas; no oculta una elección requerida.
- [ ] Crear tiene resultado y destino explícitos; conflicto/permiso/error no deja contexto falso.

## 9. Lote 12 — Pendientes previos que requieren verificación específica

### 12A. Diagnóstico, salidas y navegación histórica

**Cubre:** C15/C16/C18 y remanentes de C17 cuando afecten orientación. No supone que todos sean defectos confirmados.

1. Comprobar progreso del autodiagnóstico usando sus 50 preguntas y secciones reales. Mostrar progreso derivado de respuestas válidas, no de visitas ni formularios ilustrativos. Si el contrato no lo permite, explicitar la falta y separar ampliación de API.
2. Verificar salida de Próximamente cerca del control activado, sin avisos remotos que parezcan de otro formulario.
3. Comprobar Atrás/Adelante y solicitudes al cambiar pasos. No sustituir todos los pasos por `replaceState`: destruiría recorridos útiles ya aceptados. Ajustar listeners/validaciones duplicadas solo si se reproducen.
4. Verificar que los rótulos de describir/valorar riesgos representan tareas distintas; conservar ambos si así son sus campos.

**Aceptación:** tareas con resultado esperado, captura/log acotado de solicitudes cuando corresponda, sin escrituras por navegar; conservación de borradores; ningún progreso o descarga inexistente inventados. Una hipótesis no reproducida se registra como tal, sin refactor preventivo.

### 12B. Error temporal frente a sesión ausente

**Cubre:** seguimiento abierto del lote 1, no un rediseño de autenticación.

**Cambios:** clasificar errores de consulta/autenticación usando el resultado real del proveedor; evitar «Tu sesión expiró» por cualquier fallo. Ofrecer reintento o indicación de iniciar sesión según corresponda, conservando memoria de la pestaña original. No almacenar ni imprimir credenciales, renovar permisos por UI o reutilizar sesión inválida.

**Aceptación:** desconexión temporal, sesión realmente ausente y recuperación tras autenticación separados; borrador conservado al reintentar; error no habilita editor ni emite éxito de guardado; la nueva ventana no promete recuperar notas no guardadas de la anterior.

## 10. Lote 13 — Guía, glosario y cierre comprobable

**Resuelve:** P1–P6 y P13 en documentación final, trazabilidad de G01–G30 y C19 como criterio transversal.

La documentación de cada sublote se actualiza al cerrarlo; este lote consolida, no posterga toda explicación hasta el final.

**Entregables:**

- Guía «Dónde está / qué hace / qué conserva» con rutas y efectos efectivamente implementados.
- Mapa de identidades, guardado y registro, basado en los diagramas corregidos del análisis.
- Glosario funcional breve con nombres aceptados, equivalencias históricas y verbos por operación.
- Guía del ciclo documental actualizada separando capacidades actuales y circuito general futuro. Si se produce Word/PDF, ambas versiones deben coincidir con el repositorio y revisarse visualmente.
- Checklist único de aceptación y remanentes con versión Git, rol/contexto, evidencia, resultado y límite de prueba.

**Recorridos integrales de cierre:**

1. Elegir contexto, determinar aplicabilidad, localizar editor EIPD o su razón de bloqueo.
2. Editar EIPD, cambiar de paso/módulo, localizar pendiente y volver sin pérdida.
3. Guardar explícitamente en escenario ficticio, reconocer confirmación y distinguir última lectura del borrador.
4. Consultar documento/versiones; encontrar revisión y decisión correspondientes; explicar por qué no equivalen a activación.
5. Preparar copia de una versión sin registrarla; cancelar/volver y explicar dónde está el contenido.
6. Repetir navegación esencial en ventana estrecha, con teclado y zoom; cerrar paneles y volver al formulario.
7. Provocar error de lectura y recuperar en la misma pestaña; comprobar rol/estado/material bloqueados con fixtures controlados.
8. Autodiagnóstico real, Inventario y Mi organización mantienen su ámbito y no heredan una evaluación como propia.

**Criterio de cierre:** cada recorrido aplicable se registra como OK/Fallo/No probado con evidencia. No se declara aprobación jurídica, producción, auditoría total ni accesibilidad certificada. No se suman ejecuciones repetidas como escenarios diferentes. La publicación de una rama no prueba una CI ni constituye despliegue.

## 11. Trazabilidad y pendientes preservados

| Origen                                                             | Cobertura en el nuevo plan                            | Estado al redactar                                                         |
| ------------------------------------------------------------------ | ----------------------------------------------------- | -------------------------------------------------------------------------- |
| Lotes 1–5 aceptados                                                | Regresión focalizada en todos los cambios adyacentes. | Conservar aceptación; no declararlos pendientes por los informes antiguos. |
| Lote 6 anterior                                                    | 6A–6B.                                                | Pendiente implementación y validación.                                     |
| Lote 7 anterior                                                    | 7A–7B.                                                | Pendiente implementación y validación.                                     |
| Lote 8 anterior                                                    | 8A–8B.                                                | Pendiente implementación y validación.                                     |
| C5/C7: menús y teclado; P7/P11/P12                                 | 6A, 7A y 8B.                                          | No se presume que toda carencia de flechas sea defecto.                    |
| C6: pendientes globales / P9                                       | 9A–9B.                                                | Requiere unidades identificadas, no contar booleanos como formularios.     |
| C10: cambio de contexto                                            | 9B/11B.                                               | Conservar alcance por módulo y destino explícito.                          |
| C13: revisión/decisión localizables                                | 10A–10B.                                              | Validar anclas/ayudas antes de dividir pantallas.                          |
| C15/C16/C17/C18                                                    | 12A y rótulos de 6B/11A.                              | Verificar cada hipótesis; no desaparecen del plan.                         |
| C19: pruebas                                                       | En cada sublote y consolidación 13.                   | No aplazar comprobaciones al final.                                        |
| NAV-UX-005 / LIC-FORM-001                                          | Trabajo funcional separado.                           | No se cierra por navegar mejor o añadir un glosario.                       |
| Evidencias/anexos, rectificación histórica, auditoría, metodología | Mantienen backlog y contratos específicos.            | Fuera de cambios de presentación; no cierre implícito.                     |

Los códigos C se conservan como referencias históricas del checklist de revisión: la descripción concreta y el repositorio prevalecen sobre una asociación numérica ambigua en los informes. Los identificadores P y G permiten seguir cada decisión aceptada sin renumerar los lotes 6–8.

## 12. Primer bloque para ejecutar

**Estado: 6A aceptado con alcance asistido acotado; publicación autorizada el 26/10/2026.** Próximo bloque propuesto: 6B, pendiente de indicación; no se inicia en este cierre. No implementar aún la lista de pendientes, nuevos estados documentales, cambios de servidor o rediseño de todos los formularios.

Este plan se puede ajustar tras la aceptación del usuario. La estimación depende de la evidencia que surja en cada componente; no se prometen plazos ni mejoras porcentuales sin medición.
