# Backlog — CumpleIA

## Visibilidad de accesos que abren formularios o información

- [ ] **NAV-UX-002 — Adoptar selección explícita de contexto en la navegación conectada.** Usuario solicita durante la prueba seleccionar organización → tratamiento del RAT → finalidad → evaluación. Incorporado ahora únicamente a la maqueta integral con ejemplos separados; pendiente prueba asistida y posterior adopción en el producto. Usar identidades y opciones autorizadas del servidor, filtrar finalidades por tratamiento y evaluaciones por finalidad, mostrar el contexto elegido durante todo el recorrido y no conservar una combinación inválida al cambiar la selección anterior. Separar borradores, guardados, valoraciones, anexos, revisiones y descargas por evaluación; mantener su asociación histórica y no copiar ni heredar decisiones por cambiar de finalidad o versión. Navegar debe conservar los borradores sin presentar cambios pendientes como guardados. La selección de infancia depende del alcance de la evaluación elegida. Validar múltiples finalidades y versiones, cambios con ediciones pendientes, retorno entre módulos, recarga desde servidor, consultas y descarga de la evaluación exacta, permisos/aislamiento por organización y uso en móvil/teclado. No implica crear evaluaciones automáticamente, ampliar permisos ni habilitar EIPD. [Contrato y prueba de maqueta](project/maqueta-navegacion-integral.md).


- [ ] **NAV-UX-001 — Maqueta integral con Panel principal y navegación homogénea.** Usuario solicita segunda versión basada en su bosquejo PowerPoint y acepta menú principal fijo a la izquierda, opciones superiores específicas por módulo, submenús por clic y formularios centrales. Se elimina la capa genérica Completar datos. Preparar resolución documental queda en Resoluciones y revisiones. Demostración implementada en `/dashboard/maqueta`, con módulos, escenarios adultos/infancia, borradores en memoria y pruebas dirigidas. Pendientes prueba asistida, ajustes y aceptación antes de adopción en producto conectado. [Alcance, límites y guion](project/maqueta-navegacion-integral.md). LIC-UX-015 sigue abierto: maqueta no equivale a implementación transversal del producto.

- [ ] **LIC-UX-015 — Destacar de forma transversal las acciones de apertura y mostrar claramente su destino.** El usuario informa durante el recorrido de infancia del 23/10/2026 que le costó encontrar «Preparar documento para revisión» y solicita destacar estas opciones para todos los casos. Aplicar un patrón consistente a botones, enlaces y desplegables que abren formularios, nuevas etapas o información adicional del recorrido de licitud; no limitar el ajuste a infancia ni a un único botón. Revisar también su coherencia con el RAT y los componentes compartidos, delimitando cualquier ampliación antes de implementarla.

  **Alcance de diseño:** inventariar accesos en Resumen, Completar datos, Revisar documentos e Historial/descargas, incluidos preparar resolución, preparar sucesor, vista previa/preparar para revisión, consultar resoluciones, añadir anexos/evidencias, contenido guardado, fundamentos y detalles/historial de facultades. Distinguir acciones principales, secundarias y desplegables con borde/fondo, peso, espaciado y texto explícito; incorporar indicador de apertura o expansión cuando ayude. No depender solo del color ni convertir todas las acciones en botones primarios. Separar navegación/consulta de guardar, registrar, retirar o reemplazar contenido.

  **Destino y estados:** al abrir otro paso, mostrar título y ubicación claros, desplazar/focalizar el inicio del nuevo contenido cuando queda fuera de la vista y mantener foco de teclado accesible; al expandir detalles locales, conservar relación con su control y estado abierto/cerrado. Si un botón está deshabilitado, mantenerlo reconocible y explicar cerca qué requisito falta. Las confirmaciones de reemplazo deben conservar sus dos opciones claramente diferenciadas; no saltarlas ni copiar/guardar automáticamente. Mantener borradores y advertencias de cambios pendientes al navegar. Considerar enlace de retorno y acceso al siguiente paso en formularios largos, evitando acciones duplicadas ambiguas.

  **Criterios de aceptación:** (1) recorrido visual y por teclado en adultos e infancia permite localizar las aperturas sin indicaciones externas sobre su posición; (2) escritorio, zoom y móvil conservan jerarquía, foco visible, contraste y áreas de interacción adecuadas; (3) cada acción indica qué abre y el contenido nuevo resulta perceptible; (4) desplegables accesibles con nombre/estado correctos; (5) botones deshabilitados explican el motivo y se actualizan al completar requisitos; (6) no se modifica persistencia, permisos, bloqueos o registro histórico; (7) al preparar sucesor, se distingue copiar a un formulario temporal de crear una resolución, y la confirmación de reemplazo sigue funcionando. Validar con casos dirigidos de interacción y recorrido asistido, no solo cambios de color. Relacionado con LIC-UX-004/006 y LIC-UX-014; pendiente diseño e implementación. Evidencia: captura 14b2c648 y observación explícita del usuario.

## Errata en referencia de revisión histórica de infancia

- [ ] **LIC-DATA-001 — Tratar de forma trazable la referencia histórica IMULADA-PILOTO-INFANCIA-REV-002.** Usuario detecta S inicial ausente en la revisión documental No continuar de resolución 2. Referencia esperada SIMULADA-PILOTO-INFANCIA-REV-002.; captura c5bbcc4b y antecedentes 9674aab9/ad339ee2. ChildEipdHistory muestra directamente event.review_reference, sin recortar; pendiente cotejo de la respuesta específica de revisiones para confirmar el origen almacenado, ya que el expediente JSON exporta eventos de organización y no esta revisión. Antes de corregir, identificar registro exacto y verificar referencia de origen. Conservar registros inmutables: definir fe de erratas o anotación correctiva vinculada con original, motivo, actor y fecha, o usar mecanismo existente si está disponible; no ejecutar UPDATE histórico ni corregir solo en pantalla como si siempre hubiera estado bien. Validar que consulta y exportación de ese canal distingan referencia original/corrección, no cambien hashes de resolución ni reinterpreten una decisión, y mantengan permisos/aislamiento. Si no existe mecanismo correctivo, delimitar contrato antes de implementación. Registro documental pendiente, sin cambios de producto ni de datos históricos.

## Estado de guardado ante archivos rechazados

- [ ] **LIC-UX-014 — Aclarar el estado de Guardar y evitar errores duplicados en anexos.** Ensayo manual del 23/10/2026: con referencia/descripcion/seccion completas, CSV rechazado y confirmacion ficticia marcada, el boton Guardar anexo ficticio permanece habilitado. Al pulsarlo se rechaza el intento y se conservan los campos, pero el mismo mensaje de formato aparece junto al selector y junto al guardado. No se observa un guardado exitoso; el hallazgo es de presentacion, no evidencia de que se admitan CSV. Ajuste posterior: deshabilitar Guardar mientras exista un error conocido del archivo (formato, vacio o tamano), con motivo visible y asociado de forma accesible; mantener la validacion al enviar y la del servidor como defensas independientes. Evitar repetir el mismo error global y local; mantener accesible el aviso junto al campo y un foco/resumen coherente si el rechazo proviene del envio. Conservar referencia, descripcion, seccion, vinculos y confirmacion al corregir el archivo; actualizar el estado tras seleccionar un PDF/TXT valido, sujeto a los demas requisitos. Criterios: CSV, archivo vacio y sobredimensionado no habilitan Guardar; sustitucion por valido retira el error anterior; no hay falsos mensajes de exito ni solicitudes duplicadas; navegacion por teclado y lector de pantalla comprensible; pruebas dirigidas de estado y correccion sin alterar persistencia ni limites. Evidencia: [checklist del recorrido](project/m3-t1-checklist-recorrido-licitud.md), capturas ee6c75a3 y da53ff0a. Pendiente implementacion; mantener datos ficticios y EIPD bloqueada.

## Consulta conjunta del riesgo residual y sus medidas de mitigación

- [ ] **LIC-UX-013 — Mostrar las medidas que sustentan el riesgo residual en Consultar valoración y anexos.** Solicitud del usuario durante el recorrido asistido del 23/10/2026. Estado: registrado para desarrollo posterior; no implementado por este registro. Objetivo: comprender el resultado por riesgo junto con sus medidas y respaldos, sin tener que reconstruir las relaciones entre formularios y anexos. Complementa la consulta existente; no cambia el cálculo ni las condiciones de guardado.

  **Presentación requerida:** mantener el resumen general y añadir un detalle por riesgo con código y descripción, residual previsto y residual actual claramente separados, probabilidad, impacto y nivel de cada uno; mostrar «Sin evaluar» cuando corresponda. Junto al resultado, listar todas las medidas vinculadas con código, descripción, dimensión de mitigación (probabilidad, impacto o ambas), eficacia cualitativa, implementación declarada, estado de verificación y fundamento consultable. Mostrar referencias de evidencia y anexos relacionados con referencia, versión y acceso a la descarga autorizada cuando exista un archivo. Distinguir una referencia documental de un archivo adjunto; no ofrecer descargas inexistentes ni presentar una referencia como evidencia verificada por sí sola.

  **Origen y vigencia:** leer el resultado y los atributos del control desde la revisión de valoración consultada. Para descripciones, implementación y respaldos obtenidos del documento o del índice de anexos, identificar su procedencia y comprobar su asociación con esa revisión. No combinar silenciosamente una valoración histórica con descripciones, estados o versiones actuales. Si el contrato disponible no permite recuperar una descripción o respaldo histórico exacto, informar esa limitación y mantener los códigos de la revisión; definir cualquier ampliación del contrato antes de implementarla. No escoger automáticamente la versión más reciente de un anexo para justificar una valoración previa. Los cambios pendientes del formulario no deben aparecer como guardados.

  **Reglas de interpretación:** las medidas se vinculan a riesgos, no directamente a un nivel global agregado. Una medida que actúa sobre probabilidad no debe presentarse como reducción del impacto. Mostrar todas las medidas de un riesgo sin repartir porcentajes ni atribuir una reducción individual no evaluada. Conservar la distinción entre medida propuesta, implementación declarada y verificación registrada; los casos ficticios deben mantener su identificación. Si no hay medidas, referencias o archivos relacionados, indicarlo expresamente. Las referencias no resolubles deben conservarse visibles con su estado, sin inventar respaldos. Mostrar la condición histórica o pendiente del resultado antes del detalle.

  **Ejemplo de aceptación del ensayo:** R1 con residual actual Medio (probabilidad Baja e impacto Grave); M1, restricción de acceso según funciones autorizadas, dimensión Probabilidad, eficacia Parcial y estado Verificada en el escenario ficticio. Referencia SIMULADA-VERIFICACION-M1-001, con la versión de anexo que pueda asociarse de forma comprobable. El ejemplo no acredita implementación o pruebas reales.

  **Criterios de aceptación y validación:** (1) un riesgo con una medida y varios riesgos con varias medidas, incluida una medida compartida; (2) residual previsto frente a actual sin evaluar, medidas propuestas o pendientes y ausencia de vínculos; (3) referencias documentales sin archivo, anexos con varias versiones y referencias no resolubles; (4) consulta vigente frente a histórica sin mezclar revisiones; (5) guardar, recargar y reabrir conserva las relaciones y resultados del servidor; (6) lectura accesible en escritorio y móvil, con etiquetas claras y fundamentos extensos desplegables; (7) permisos y aislamiento por organización conservados en lectura y descarga; (8) comprobaciones dirigidas de presentación y, solo si se amplía el contrato, pruebas de compatibilidad e historial. No mutar revisiones, anexos, cálculos ni campos manuales al consultar.

  **Puntos de entrada para desarrollo:** frontend/components/licitud/AssessmentSupportPanel.tsx, tipos y cliente de soporte, vista de consulta de riesgos y backend/app/services/assessment_support.py si resulta necesaria una ampliación de lectura. Revisar primero el [contrato de riesgos y anexos](project/m3-t1-riesgos-anexos.md). Coordinar con LIC-COH-001 para diferenciar el resumen manual de sección 7 del resultado estructurado, sin sobrescribirlo. Mantener el mensaje de revisión por una persona responsable y los bloqueos vigentes de EIPD/datos reales.

## Coherencia del resumen manual y la valoración de riesgos

- [ ] **LIC-COH-001 — Revisar coherencia entre sección 7 y valoración estructurada.** Hallazgo del ensayo positivo ficticio del 23/10/2026: JSON (5) conserva resumen/fundamento manual pendientes, residual_risk_level sin_resolver, plan de verificar M1 y limitaciones sin anexos; la valoración estructurada revisión 6 actual registra residual Medio, M1 implementada/verificada en escenario sintético y cuatro anexos. Son campos independientes, no pérdida de persistencia. Alcance: revisar explícitamente los textos del ensayo y diseñar ayuda/aviso que identifique fuente, revisión y necesidad de actualizar el resumen documental al cambiar riesgos/controles/anexos. No sobrescribir narrativas ni equiparar automáticamente las escalas (nivel documental no_alto/alto/sin_resolver y matriz de cuatro niveles). La verificación sintética no acredita controles reales. Criterios de aceptación: (1) diferenciar resumen manual de resultado estructurado y señalar su procedencia; (2) mostrar aviso de coherencia por revisar cuando corresponda, sin declarar una contradicción jurídica por comparación de códigos de escalas distintas; (3) conservar texto e historial hasta edición explícita; (4) guardar la edición invalida la asociación anterior y exige nueva valoración conforme al mecanismo existente; (5) reapertura/exportación conserva correcciones y versiones; (6) datos incompletos, valoraciones históricas y anexos nuevos no producen falsos positivos; (7) EIPD/datos reales permanecen bloqueados. Evidencia: [checklist del recorrido](project/m3-t1-checklist-recorrido-licitud.md), ensayo revisión 6 y JSON (5). Pendiente diseño e implementación del aviso y actualización explícita del contenido del ensayo; no modificar automáticamente el expediente del usuario.


## Brecha de formularios de consentimiento y LIA

- [ ] **LIC-FORM-001 — Completar los formularios de consentimiento y LIA del recorrido.** Auditoría solicitada por el usuario el 23/10/2026: el servidor ya tiene contratos/evaluadores, pero consentimiento no tiene editor y LIA solo expone nueve textos. Conectar checklist de consentimiento (14 preguntas generales y 2 condicionales), ocho grupos completos de LIA, evidencia/anexos por control, diagnóstico por campo y consulta legible; conservar datos al cambiar de base y en guardado/reapertura/exportación. Reutilizar controles existentes, separar completitud documental de validación jurídica y distinguir normativa vigente/reforma. Originales Excel aportados y cotejados: 19 preguntas de consentimiento y 31 de LIA, más estados/conclusiones. El informe mapea cada celda al contrato y la adaptación requerida; desglose de consentimiento requiere decisión/versionado de conservación, sin copiar borrado universal ni recomendaciones como mandatos. 190 pruebas de servicios/esquemas existentes aprobadas; implementación de la brecha pendiente. Alcance y aceptación: [auditoría de cobertura](project/m3-t1-consentimiento-lia-cobertura.md). Desarrollo posterior detallado en [contrato LIC-FORM-001](project/m3-t1-consentimiento-lia-implementacion.md): campos, condicionales, compatibilidad/versionado, evidencias, paquetes FORM-01 a 05, decisiones pendientes y matriz de aceptación. Solo datos ficticios, EIPD bloqueada; sin merge/despliegue.


> Primer archivo de backlog trackeado en git. Hasta ahora el seguimiento de tareas vivía en archivos `Claude_*`/`Fase 1`/`Modulo 1` sin trackear (`git status` los marca `??`); este archivo empieza a fijar en el repo los ítems con criterios de aceptación explícitos, empezando por el de este trabajo.

## Experiencia de licitud — propuesta aceptada 18/10/2026

- [ ] **LIC-UX-004 — Flujo guiado y separacion por tareas.** Propuesta aceptada: cuatro pestanas (Resumen y siguientes pasos, Completar datos, Revisar documentos, Historial y descargas), esquema visible, facultades en acceso separado, contexto de version junto a decisiones, controles reconocibles y causas de bloqueo. Primero maqueta navegable con adultos, infancia y facultad revocada; luego implementacion y validacion asistida. Conservar borradores al navegar y refrescar dependencias tras guardar. Documento y criterios: [Experiencia de licitud](project/m3-t1-licitud-experiencia.md). Incluye hallazgos LIC-UX-002/003 y patron RAT-UX-001 segun alcance; RAT-VAL-001 sigue separado. Aceptada no equivale a implementada. Sin ampliacion de permisos, activacion EIPD ni datos reales.
  - Maqueta V3: `/dashboard/licitud/maqueta`, seleccion RAT/finalidad y cuatro pestanas. Editor simplificado; preparar muestra contenido, pendientes y version con notas opcionales; lectura preparatoria ficticia y registro completo en memoria. Crear desde version seleccionada copia su contenido con origen/motivo obligatorio; confirma reemplazo de cambios pendientes. Emitir revision es independiente. Editar genera otra version sin mutar anteriores. Bloque de maqueta consolidado: usuario confirma copia DEMO-1 a DEMO-3, original intacto, descarga y observaciones separadas por version. Resaltado de descarga coherente y ayudas en los siete desplegables; 18 Chromium del bloque aprobadas. Recorrido integrado al servidor con secciones, guardados coordinados y borrador EIPD guiado; 71 Chromium y 4 API/integracion aislada aprobadas. Pendiente validacion asistida de esta interfaz conectada y contratos de adopcion RAT/LIA, origen/motivo estructurados y revision EIPD general; LIC-UX-004 abierto.

  - Bloque de riesgos/anexos completado: valoración estructurada interna, controles y residual,
    anexos ficticios versionados, revisión conjunta RAT/licitud-LIA/EIPD y preparación
    infancia según alcance; autoridad condicional y guardado sin filas totalmente vacías.
    [Contrato/evidencia](project/m3-t1-riesgos-anexos.md). Resta validación asistida ampliada
    y contratos de adopción/revisión formal; no se marca LIC-UX-004 integralmente cerrado.

- [x] **LIC-UX-005 — Acercar y destacar el aviso de cambios sin guardar.** Visita guiada V2, 19/10/2026: el usuario confirma que el fundamento se conserva al cambiar de pestana, pero no identifica el aviso situado debajo de las pestanas. Moverlo al formulario activo, cerca de los campos editados y de la accion de guardar, con presentacion visible y accesible. Mantener el significado: cambios pendientes conservados entre pestanas durante la visita; recargar reinicia el ensayo. Criterios: el estado se identifica mientras se edita y antes de guardar, sin buscarlo arriba; no confundir guardado simulado con persistencia en servidor. Aplicado en maqueta V3 y formularios conectados: aviso destacado dentro del formulario activo; pendiente validar ubicacion del recorrido conectado con usuario. Sin cambios en permisos ni activacion EIPD. Aclaración del recorrido asistido del 21/10/2026: en Base y fundamento, ubicar el aviso «Cambios sin guardar» inmediatamente después del campo Fundamento y encima del botón Guardar borrador, no solo al inicio del formulario. Mantener su estilo destacado y retirar el aviso tras guardado confirmado; conservarlo ante rechazo. Posición observada en la captura: encima de las instrucciones y campos, demasiado alejada del botón. Ajuste implementado en el bloque del 22/10; aviso inmediatamente antes de Guardar y conservado ante rechazo.

- [x] **LIC-UX-006 — Jerarquía de títulos y separación de casillas en formularios de licitud.** Recorrido asistido, 21/10/2026: revisión transversal de Crear evaluación, Alcance del RAT, Base y fundamento, Documentar EIPD, Valorar riesgos y Anexos de respaldo. Destacar visualmente títulos de secciones, leyendas y etiquetas de campos con negrita/color o fondo coherente, diferenciándolos de los datos ingresados. Incluye Finalidad, Categorías de datos incluidas, Titulares incluidos, Base de licitud propuesta, Fundamento y los campos de EIPD/riesgos/anexos mostrados en las capturas. Agregar separación visible entre cada casilla y su texto, incluidas declaraciones de datos ficticios. Conservar etiquetas accesibles, selección al pulsar el texto y jerarquía semántica. Implementado y validado en el bloque de presentación del 22/10.

- [x] **LIC-UX-007 — Resultado de creación visible y conflicto de borrador claro.** Recorrido asistido, 21/10/2026: colocar junto a Crear borrador una confirmación destacada y accesible de borrador creado/guardado únicamente tras éxito confirmado del servidor. Si ya existe un borrador para la finalidad, explicar que no se creó otro y ofrecer Abrir borrador existente; no concatenar el consejo de respuesta incierta a un rechazo conocido. Conservar el formulario ante rechazo y no dar por guardados los cambios de ese intento. La captura muestra el rechazo «Ya existe un borrador para esta finalidad», con una sola evaluación versión 1 en el historial; no acredita una creación nueva. Implementado y validado localmente en el bloque del 22/10; revisión asistida posterior pendiente.

- [x] **LIC-UX-008 — Mensaje del resumen comprensible y acorde al alcance.** Recorrido asistido, 21/10/2026: sustituir la frase «La preparación disponible corresponde al contrato documental EIPD de infancia. No crea una versión autónoma de RAT o LIA ni determina que una EIPD sea obligatoria.». El usuario señala que no corresponde al mensaje de esta pantalla. Explicar las acciones disponibles con lenguaje de usuario, sin términos internos como «contrato documental» ni referencias de infancia en el tratamiento de adultos. Ajustar cualquier explicación específica de infancia al alcance aplicable. Propuesta para adultos: «Completa y guarda los datos de esta evaluación. Luego podrás consultar el alcance del RAT, la base de licitud y el documento EIPD guardado, si existe. Guardar no equivale a aprobar la evaluación.». Implementado y validado localmente en el bloque del 22/10; revisión asistida posterior pendiente.

- [x] **LIC-UX-009 — Tamaños de lectura consistentes en todo el flujo de licitud.** Recorrido asistido, 21/10/2026: revisar en conjunto cabecera, Resumen, Alcance del RAT, Base y fundamento, Documentar EIPD, Valorar riesgos y Anexos de respaldo. El texto sobre versiones y otras ayudas se perciben demasiado pequeños respecto del resto. Aplicar una escala coherente de títulos, etiquetas, respuestas y textos explicativos; evitar diferencias arbitrarias o aclaraciones esenciales en letra diminuta. Mantener legibilidad en escritorio/móvil y zoom normal, con el criterio de títulos destacados de LIC-UX-006. La solicitud se amplía con las cinco capturas del usuario. Implementado y validado localmente en el bloque del 22/10; revisión asistida posterior pendiente.

- [x] **LIC-UX-010 — Integrar Valorar riesgos en la navegación interna de EIPD.** Observación expresa del usuario en el recorrido asistido del 21/10/2026: Valorar riesgos debe ser la sección 4 dentro de Documentar EIPD, en lugar de una opción separada al mismo nivel del documento. Orden solicitado: 1. Tratamiento y alcance; 2. Necesidad y proporcionalidad; 3. Riesgos; 4. Valorar riesgos; 5. Medidas; 6. Fuentes y evidencias; conservar Riesgo residual y seguimiento como sección 7. Evitar el acceso duplicado exterior una vez integrado. Conservar los datos al navegar, los guardados y su asociación con el documento guardado, las revisiones/hashes existentes y el bloqueo de activación. Implementado y validado en el bloque del 22/10, conservando los borradores al navegar.

- [x] **LIC-UX-011 — Tabla de riesgos completa y legible.** Hallazgo del recorrido asistido del 22/10/2026: mezcla descripciones largas y resultados cualitativos, dificultando comparar R1/M1. Inspección de EipdRiskTable confirma que no presenta los fundamentos estructurados inherente/previsto/actual, contexto de frecuencia/exposición, horizonte, acción/responsable/fecha ni referencias de evidencia del control en esa tabla; esto no prueba pérdida en persistencia. Propuesta pendiente: por riesgo, descripción y daño en bloque propio; tabla de valoración con filas Inherente, Residual previsto y Residual actual y columnas Probabilidad, Impacto, Nivel y estado de evaluación; tabla de controles con identificador, descripción breve, dimensión de mitigación, eficacia, implementación y verificación claramente diferenciadas. Mostrar fundamentos completos, frecuencia/horizonte, seguimiento y evidencias/anexos vinculados en detalle identificado, sin mezclar análisis narrativos anteriores con fundamentos vigentes ni ocultar que un campo está pendiente. Diferenciar visualmente texto descriptivo de niveles mediante tipografía, fondos y etiquetas además del color; versión y vigencia visibles, adaptable a móvil. Mantener controles múltiples, asociaciones y guardas de actualidad; sin recalcular ni aprobar riesgos. Presentación aprobada e implementada en el bloque del 22/10; pruebas de detalle, asociaciones y vigencia aprobadas.

- [x] **LIC-UX-012 — Validación de anexos visible junto al archivo y al guardado.** Recorrido del 22/10/2026: usuario reporta rechazo de CSV sin explicación visible junto a Guardar; captura conserva referencia, descripción, R1/M1, archivo CSV y declaración ficticia. El cliente tiene validación PDF/TXT de hasta 2 MiB, pero el error del panel se renderiza arriba. Mensaje superior confirmado por captura posterior: «Selecciona un PDF o TXT de hasta 2 MiB»; rechazo de formato en cliente comprobado. Prueba posterior con SIMULADA-ANEXO-EXCEDE-2MiB.txt (2 MiB + 1 byte): usuario reporta rechazo y captura conserva formulario; no muestra aviso junto al botón. Referencia/descripción continuaron con texto de CSV, lo que no cambia la prueba de tamaño del archivo seleccionado. Mostrar motivos diferenciados («Formato no admitido» / «El archivo supera 2 MiB») junto al selector y acción de guardado, con foco/aviso accesible; explicar PDF o TXT UTF-8 hasta 2 MiB por archivo y conservar campos para corregir. Distinguir rechazo de resultado incierto y éxito; no declarar defensa de servidor probada solo por rechazo del cliente. Implementado y validado en bloque UX del 22/10; revisión asistida posterior pendiente.

- [ ] **LIC-AUD-001 — Bitácora de auditoría de acciones de Bases de Licitud.** Observación acordada con el usuario el 22/10/2026. Distinguir el historial append-only de valoraciones/anexos ya existente (actor, fecha del servidor, organización, evaluación, revisión, solicitud y huella del documento) de una bitácora completa de acciones. Revisar cobertura de guardados de licitud/LIA/EIPD, valoraciones y anexos, consultas/descargas y rechazos de validación o autorización; no asumir que cada acción ya genera un evento auditable. Definir eventos, actor servidor, contexto, fecha/hora, resultado y motivo/código, correlación de solicitud y referencias de versión; evitar secretos y contenido personal innecesario en logs. Definir permisos de consulta/exportación, aislamiento por organización, integridad y retención. Coordinar la presentación con Carpeta de Evidencia/Módulo 5 y la política existente, sin ampliar por defecto la exposición al usuario. Validar éxitos y rechazos con datos ficticios, incluyendo rechazo de residual actual sin controles verificados. Pendiente diseño de alcance e implementación; no equivale a certificación de auditoría ni modifica el bloqueo EIPD.

- [ ] **LIC-RISK-001 — Propuesta de criterios configurables y versionados de valoración.** Consulta del usuario durante el recorrido asistido del 21/10/2026: permitir definir el significado de los niveles de probabilidad e impacto. Propuesta funcional pendiente de definir/confirmar, no acordada como implementación automática: configuración de metodología por organización y personas autorizadas, con horizonte, definiciones/criterios observables, ejemplos y fundamentos; impacto centrado en daño a titulares. Mantener una plantilla inicial y mostrar en EIPD la metodología/versión aplicada. Definir expresamente si solo se parametrizan descripciones/umbrales o también matriz, escalas y reglas; estos últimos requieren contrato y validación específicos. Cada valoración debe conservar la versión/copia exacta del método; cambiar criterios no debe recalificar silenciosamente registros previos. Exigir una nueva revisión explícita para reevaluar. Los criterios actuales de CUMPLEIA-CUALITATIVA-1 son fijos. Separar esta propuesta de los ajustes de presentación y mantener activación bloqueada.

### Estado del bloque de ajustes del 22/10/2026

LIC-UX-005 a LIC-UX-012 implementados y validados localmente: tipografía/etiquetas/casillas,
avisos junto a Guardar con foco de error, conflicto de creación conocido con acceso a borradores,
mensajes de alcance comprensibles, valoración dentro de EIPD como paso 4 y navegación 1–7,
tablas por riesgo/etapa y controles con fundamentos, seguimiento y anexos vinculados.
CSV, archivo vacío y exceso de 2 MiB muestran motivos distintos junto al selector y guardado.
La confirmación de guardado se conserva si falla únicamente el diagnóstico posterior.
34 pruebas Chromium y 4 aisladas del recorrido/listado aprobadas; tipos/lint/formato revisados.
Pendiente revisión visual asistida del bloque actualizado. LIC-UX-004 no se cierra integralmente;
LIC-RISK-001 y LIC-AUD-001 continúan pendientes de diseño, sin cambios en metodología/API/RLS.
EIPD bloqueada; solo datos ficticios; sin merge/despliegue.

## Hallazgos de prueba manual RAT — 17/10/2026

- [ ] **RAT-UX-001 — Estado de guardado visible al reabrir secciones.** Prioridad baja; no bloquea el piloto ficticio. En Fuentes de los datos, la confirmacion temporal desaparece al recargar aunque el contenido persiste, lo que genera dudas sobre el guardado. Mostrar estado derivado de datos cargados del servidor (datos guardados/sin registros), cambios sin guardar al editar y confirmacion tras respuesta exitosa. No declarar guardado ante error o respuesta incierta. Criterios: recargar o volver desde otra pagina conserva estado y contenido; editar/agregar/eliminar distingue cambios pendientes; fallo conserva el formulario sin indicar exito. Evaluar el mismo patron en las demas secciones RAT. Sin cambiar completitud documental, permisos ni bloqueo EIPD. Detectado por el usuario en el piloto de infancia.

- [ ] **LIC-UX-002 — Acciones y version consultada identificables.** Hallazgo manual 18/10: registrar resolucion/decision/consulta parece texto corriente; fue dificil localizar el control y se completo un fundamento para resolucion 2 mientras estaba consultada la 1. Mostrar botones reconocibles y referencia/version junto a la decision; conservar foco/contexto al consultar. Criterio: identificar accion y version sin busqueda del navegador; no cambiar permisos ni historiales.
- [ ] **RAT-VAL-001 — Revisar completitud de fuentes.** Una fila con tipo de fuente y descripcion vacia satisface el requisito actual de fuente registrada; distinguir existencia de fila y descripcion suficiente. Definir contrato de borrador/completitud y alinear servidor, diagnostico y UI, con pruebas de vacio/espacios y persistencia. No asumir completitud juridica ni cambiar activacion EIPD. Hallazgo del piloto, pendiente de implementacion.
- [ ] **LIC-UX-003 — Explicar coherencia entre RAT e infancia.** Grupos del documento se declaran por separado de las marcas del RAT; no se sincronizan automaticamente. Mostrar origen, diferencias y necesidad de revisar/guardar contexto al cambiar RAT, preservando versiones historicas. Validar escenario sintetico de cambio de titulares sin afirmar actualizacion automatica ni sobrescribir decisiones.

## Modelo de organizaciones, roles y suscripción

Ver `docs/adr/0001-modelo-organizaciones-roles-suscripcion.md`.

- [x] Existen las entidades `Organization`, `Profile` (usuario), rol de organización (`Membership.role`), admin de plataforma (`profiles.is_superadmin`) y `Subscription`, migradas y documentadas.
- [x] Toda tabla nueva de este trabajo (`subscriptions`) incluye `organization_id` con RLS.
- [x] Existe una función de autorización (`has_permission`/`role_has_permission`, `app/services/authorization.py`) y una de estado de suscripción (`get_subscription_status`/`is_subscription_active`, `app/services/subscriptions.py`), ambas con tests unitarios.
- [x] Existe una organización semilla con un admin para desarrollo (`scripts/seed_dev.py`), ahora también con su `Subscription`.
- [x] El ADR está commiteado y referenciado desde este backlog.
- [x] No se tocó ninguna pantalla de administración de organizaciones ni integración de pagos (fuera de alcance).

### Backlog derivado — fase de Monetización (no construir todavía)

- [ ] Integración con pasarela de pago real (Stripe/Mercado Pago) que actualice `subscriptions.status` según el resultado de cobro.
- [ ] Job/flujo de dunning: mover `active` → `grace` (con `grace_until`) en compromisos anuales ante un fallo de cobro mensual aislado, y `active` → `suspended` directo en planes mensuales puros.
- [ ] UI de administración de organizaciones y de suscripción.
- [ ] Flujo de invitación de un segundo usuario a una organización existente, con asignación de rol por el admin de organización (`Permission.manage_members`, ya modelado en `app/services/authorization.py`, sin endpoint todavía).

## Autodiagnóstico (Fase 1, Módulo 1)

Ver `Fase 1/plan-fase1-modulo1-autodiagnostico.md` y `docs/adr/0002-logica-adaptativa-riesgo-remediacion.md`. Tareas 0-6 completadas para el MVP del Módulo 1:

- Tarea 0: catálogo CCS versionado (50 preguntas / 10 secciones / 8 obligaciones).
- Tarea 1: modelo `Diagnostic`/`DiagnosticAnswer`/`Finding` con RLS real.
- Tarea 2: motor de puntaje determinista, sin LLM (`app/services/diagnostico_puntaje.py`).
- Tarea 3: API (`GET /diagnostico/cuestionario`, `POST /diagnostico/respuestas`, `GET /diagnostico/actual`, `app/api/diagnostico.py` + `app/services/diagnostico.py`), primer uso real de `require_permission`. "Diagnóstico vigente" es get-or-create (a lo sumo uno por organización, `diagnostics.organization_id` UNIQUE); las brechas resueltas se cierran (`status='cerrado'`), no se borran.

### Backlog derivado — Autodiagnóstico

- [ ] **Capa 1 del ADR 0002 (aplicabilidad de preguntas por rubro/tamaño):** el catálogo no tiene ese dato todavía; `GET /diagnostico/cuestionario` devuelve las 50 preguntas a toda organización por igual.
- [ ] **Catálogo `instructivo_agencia` (ADR 0002, capa 3):** catálogo global (sin `organization_id`, análogo a `Obligacion`/`Seccion`/`Pregunta`) para los instructivos que emita el Consejo Directivo de la Agencia de Protección de Datos — no antes de oct-dic 2026 (Consejo Directivo en proceso de ratificación a la fecha del ADR).
- [ ] **Endpoint de carga/vinculación de `reference_documents`:** la tabla y el modelo ya existen (migración 0005) con `tipo='politica_interna_gobernanza'`, y `GET /diagnostico/actual` ya devuelve `hallazgos[].documentos_referencia` (vacío hoy) — falta el endpoint para que una organización cree/vincule sus propios documentos.
- [ ] **Re-evaluaciones (historial de diagnósticos):** hoy una organización tiene a lo sumo un `Diagnostic` para siempre (get-or-create). Iniciar un nuevo ciclo de evaluación tras completar uno queda fuera de alcance de la Tarea 3.
- [x] Tarea 4 (capa de IA con guardarraíles) y Tarea 5 (exportación HTML del informe) completadas. Ver las secciones específicas más abajo.
- [x] Tarea 6 completada: frontend con wizard, dashboard y descarga del informe. Ver la sección específica más abajo.


### Deuda técnica menor detectada en la revisión de PR #11 (no bloqueante)

- [ ] `recalcular_diagnostico` indexa `hallazgos_existentes` por `pregunta_id`: si algún módulo futuro (RAT, etc.) llegara a crear un `Finding` con `diagnostic_id` seteado pero `pregunta_id=None`, dos de esas filas colisionarían en el dict y la de cierre automático podría marcar como `cerrado` un hallazgo que no le corresponde. Hoy no hay ningún escritor de `Finding` en esa combinación — revisar si Tarea 4/RAT llega a crearla.
- [ ] `_construir_actual_out` (app/api/diagnostico.py) reutiliza `obtener_config_por_id`, que trae `peso_por_seccion`/`riesgo_por_pregunta`/el `Profile` de `creado_por` sin necesitarlos (solo usa `secciones`/`preguntas`). Irrelevante en latencia a esta escala; una función de solo-lectura más liviana sería más prolija si el catálogo crece.
- [ ] `_limpiar_diagnostico*_org_a` está duplicada entre `tests/test_api_diagnostico.py` y `tests/test_diagnostico_service.py` (ambas necesarias por el `UNIQUE` nuevo en `diagnostics.organization_id`). Candidata a moverse a `conftest.py` como fixture compartida.
- [ ] El umbral de "diagnóstico completado" (`len(respuestas_input) >= len(config.preguntas)`) depende del tamaño *actual* del catálogo global (`Pregunta`), no de uno fijado al crear el diagnóstico — hoy es inofensivo porque el catálogo se trata como contenido fijo (Tarea 0), pero si alguna vez se vuelve editable habría que pinnear también el conteo de preguntas, no solo pesos/riesgo.

## Capa de IA del Autodiagnóstico (Fase 1, Módulo 1, Tarea 4)

Tarea 4 completa: `POST /diagnostico/informe` (solo con el diagnóstico `completado`, 409 si no) genera la narrativa vía `app/services/diagnostico_ia.py`, anclada por RAG a `ley_21719`/`guia_ccs` (`app/services/rag.py::search_chunks(sources=...)`, `ley_19628` excluida a pedido explícito) con tool-calling forzado (`LLMClient.generate_structured`, `app/services/providers/llm.py`). El riesgo y el mapeo a las 8 obligaciones **no los decide el LLM**: siguen siendo 100% deterministas (motor de puntaje de la Tarea 2 + cadena `Pregunta→Seccion→Obligacion` del catálogo de la Tarea 0) — el LLM solo redacta sobre datos ya resueltos.

Guardarraíl verificado con una llamada real (no solo mockeada): cualquier cita que no corresponda a un fragmento efectivamente recuperado por RAG, o un `finding_id` que no pertenezca al diagnóstico, se descarta en silencio (log) antes de persistir `Diagnostic.informe_ia`. En la corrida de verificación real, el modelo devolvió 4 citas y el guardarraíl descartó 3 por no calzar con los fragmentos recuperados — comportamiento esperado, no un bug.

### Backlog derivado — Capa de IA

- [ ] **Aprobación/revisión humana formal del informe:** hoy el informe se muestra como salida de un diagnóstico ya completado (borrador implícito), pero no hay un flujo explícito de "revisar y aprobar" como el que tendrán los documentos generados del Módulo 4 (`Document.status`: borrador/aprobado/archivado). Evaluar si el informe del Autodiagnóstico necesita ese mismo flujo o si basta con la revisión editorial que ya permite regenerar (`POST /informe` sobrescribe).
- [ ] **Regeneración sin versionado:** cada `POST /diagnostico/informe` sobrescribe `informe_ia` — no hay historial de versiones del informe. Aceptable para el MVP ("simple, económico"); revisar si se necesita conservar informes anteriores cuando exista carpeta de evidencia (Módulo 5).
- [ ] **Costo/latencia de RAG por informe:** hoy se hace una sola consulta de retrieval agregada (no una por hallazgo) — correcto para costo, pero no se ha medido con diagnósticos de muchas brechas simultáneas (hasta 50). Revisar si `top_k=12` sigue siendo suficiente/necesario a esa escala.
- [ ] **Capa 3 del ADR 0002 (`reference_documents`)** sigue sin endpoint de carga (ver sección de Tarea 3 arriba) — el informe de la Tarea 4 no los referencia todavía porque no hay ninguno cargado.

### Deuda técnica menor detectada en la revisión del PR #13 (no bloqueante)

Los hallazgos #1 (RLS de `org_visibility` bloqueaba a un superadmin sin membresía) y #2 (informe obsoleto en silencio tras reabrir respuestas) de esa revisión se trataron como fix prioritario, no como backlog — ver migración `0007_org_visibility_superadmin.py` y la invalidación en `app/services/diagnostico.py::recalcular_diagnostico`. Quedan como backlog legítimo (bajo esfuerzo, bajo riesgo):

- [ ] **Narrativas duplicadas por `finding_id` no se deduplican:** el schema de `generate_structured` no impone unicidad de `finding_id` dentro de `narrativas[]`; si el LLM devolviera dos entradas para el mismo hallazgo, el guardarraíl actual (que solo valida pertenencia, no unicidad) dejaría pasar ambas.
- [ ] **Falta test del filtro `Finding.status != FindingStatus.cerrado`** en `generar_informe`: ningún test de `test_diagnostico_ia.py` cubre un hallazgo ya cerrado — si ese filtro se rompiera en un refactor futuro (narrando también brechas resueltas), ningún test lo detectaría hoy.

## Exportación del informe (Fase 1, Módulo 1, Tarea 5)

`GET /diagnostico/informe/exportar` (`app/services/diagnostico_exportacion.py`) sirve el informe ya generado (Tarea 4) como HTML autocontenido y descargable — resumen ejecutivo, puntaje global y por sección, y el detalle de cada hallazgo (riesgo, sección, narrativa con sus citas, acción correctiva, responsable). 404 sin diagnóstico vigente, 409 si el informe todavía no fue generado (mismo contrato que `POST /informe`), solo requiere `view_content`. Empieza simple a propósito (HTML imprimible a PDF desde el navegador, sin agregar WeasyPrint u otro motor de PDF todavía) — ver la Tarea 5 del plan. Todo texto que no viene del catálogo fijo (nombre de organización, resumen/narrativas del LLM, descripción/acción/responsable de un hallazgo) se escapa con `html.escape`, verificado con un intento de `<script>` real en la verificación en vivo.

### Backlog derivado — Exportación

- [ ] **PDF real:** sigue pendiente para cuando el Módulo 4 (generador de documentos) exista o si una PYME lo pide antes — hoy el usuario debe usar "Imprimir → Guardar como PDF" del navegador sobre el HTML exportado.
- [x] **Descarga desde el frontend:** resuelto en la Tarea 6 (`ResultadosDashboard.tsx::handleDescargar`, fetch con Bearer token + Blob URL, ya que el navegador no puede mandar el header `Authorization` desde un `<a href>` plano).
- [ ] **Respuestas crudas no incluidas:** decisión explícita (no diferida por falta de tiempo): el anexo con el detalle de las 50 respuestas se reserva para la Carpeta de Evidencia (Módulo 5, de pago) en vez de regalarse en el informe gratuito del Módulo 1 (freemium) — ver nota de estrategia más abajo. El dashboard en pantalla (`ResultadosDashboard.tsx`) ya muestra un aviso "Anexo de respuestas — disponible en la Carpeta de Evidencia" a modo de preview del upsell.

## Frontend del Autodiagnóstico (Fase 1, Módulo 1, Tarea 6)

Wizard del cuestionario por sección + dashboard de resultados + descarga del informe, bajo `/dashboard/autodiagnostico` (`frontend/components/autodiagnostico/`: `AutodiagnosticoWorkspace`, `Cuestionario`, `ResultadosDashboard`). Decisiones tomadas antes de construir (sin selector de organización ni tests de frontend preexistentes en el repo):

- **Organización activa:** se asume una sola organización por usuario (`GET /me/organizations`); si hay más de una se muestra un `<select>` local sin contexto global — no hay onboarding ni selector persistente todavía, y no era el alcance de esta tarea construirlo.
- **Navegación del wizard:** una sola ruta con estado interno en React (tabs/paso actual), sin URL por sección — el catálogo es chico (50 preguntas) y no había precedente de rutas dinámicas en el repo.
- **Sin tests automatizados de frontend:** consistente con que todo el proyecto no tenía ningún framework de testing de frontend configurado antes de esta tarea (ni Jest, ni Vitest, ni Playwright) — verificación manual en navegador real.

### Backlog derivado — Frontend

- [ ] **Selector/contexto global de organización:** si alguna vez un usuario pertenece a más de una organización de verdad, el `<select>` local de `AutodiagnosticoWorkspace` no escala a otras pantallas futuras — evaluar un contexto de React reusable en ese momento.
- [ ] **Testing de frontend:** no hay ningún framework instalado; si se decide adoptar uno, es una decisión de alcance mayor (nueva dependencia a justificar en `CLAUDE.md`) que aplica a todo el proyecto, no solo a este módulo.

## Mejoras al informe de Autodiagnóstico (revisión manual, 2026-08-10)

Origen: `Claude_22_julio_2026/mejoras-informe-autodiagnostico.md` (revisión manual de un informe real exportado). De los 9 ítems + 1 bug del documento, se resolvieron en esta ronda:

- **BUG-01 (desfase entre conteo narrativo y hallazgos listados):** el resumen ejecutivo del LLM podía declarar un número de brechas que no coincidiera con `len(hallazgos)` — dos fuentes de verdad para el mismo dato. La regla 5 del system prompt (`app/services/diagnostico_ia.py`) le pide al LLM que no declare esa cifra, pero **verificado en producción que la instrucción sola no bastó** (el modelo siguió declarando un número, ej. "35" cuando el real era 34). Fix definitivo: `_quitar_conteo_de_brechas` (guardarraíl determinista con regex, no solo la instrucción) quita del texto libre cualquier número seguido de "brecha(s)"/"hallazgo(s)" antes de persistirlo — cubierto por `test_generar_informe_quita_conteo_de_brechas_declarado_por_el_llm`. El conteo exacto sigue viviendo solo en el bloque determinista del informe exportado (ítem 2).
- **Ítem 1 (encabezado de identificación):** agregado solo al HTML exportado (`app/services/diagnostico_exportacion.py`), no al dashboard en pantalla — nombre, RUT, rubro y tamaño de la organización, quién respondió (perfil `updated_by` del diagnóstico) y su rol de membresía como proxy de "cargo" (no existe un campo de puesto/cargo real en `Profile` todavía), ID del diagnóstico y fecha. "Tamaño" muestra el valor libre `organizations.size`, no una clasificación PYME/gran empresa por umbral legal (esa clasificación no existe en el código).
- **Ítem 2 (conteo de hallazgos por riesgo):** bloque determinista Alto/Medio/Bajo/Total en el informe exportado, antes de la tabla por sección. Solo el total global, sin desagregado por sección ni gráfico (barras/donut) — se prefirió mantenerlo simple; ver backlog derivado abajo.
- **Ítem 3 (trazabilidad respuesta + riesgo base/ajustado):** `HallazgoOut` (API) y el HTML exportado ahora muestran la respuesta original de la pregunta y, cuando "Parcial" degrada el riesgo, tanto el riesgo base del catálogo como el ajustado ("Riesgo Medio — base Alto, ajustado por respuesta Parcial"). Se agregó también una sección de Metodología (escala de respuesta, cálculo de puntaje, regla de degradación) en el HTML exportado.
- **Trazabilidad de quién respondió (pedido del usuario, no del documento original):** `diagnostic_answers` ahora tiene `created_by`/`updated_by`/`updated_at` (migración `0008_diagnostic_answers_auditoria.py`); `Diagnostic.updated_by` se actualiza en cada `POST /diagnostico/respuestas`, y `Diagnostic`/`Finding.updated_at` tienen `onupdate=func.now()`. Antes de este fix, ninguna tabla del Autodiagnóstico registraba quién editó una respuesta ni cuándo — brecha real respecto a la convención de auditoría de `CLAUDE.md`.

### Backlog derivado — Mejoras al informe (ítems 4-9 del documento, diferidos por decisión explícita del usuario)

- [ ] **Ítem 2 (fase 2):** desagregado del conteo de hallazgos por sección y/o gráfico simple (barras o donut) — se implementó solo el total global.
- [ ] **Ítem 4 — Contenido accionable:** recomendación de acción concreta, responsable (rol) y plazo indicativo por severidad (Alto=30 días, Medio=90, Bajo=180) por hallazgo; exportar como plan de acción independiente (Excel/tabla) es fase 2 dentro del ítem.
- [ ] **Ítem 5 — Nota de DPD en autodesignación:** detectar cuando el Gerente General (u otro cargo directivo) se autodesigna delegado de protección de datos y agregar una nota sobre la alternativa de designar a un tercero (incluyendo que CumpleIA puede prestar ese servicio).
- [ ] **Ítem 6 — Fundamento legal por hallazgo:** citar el artículo específico de la Ley N.° 21.719 en hallazgos de riesgo Alto (al menos), extensible a todos si el catálogo llega a tener ese mapeo.
- [ ] **Ítem 7 — Preguntas N/A:** mostrar por sección cuántas preguntas quedaron en N/A vs. respondidas, para no leer un puntaje de sección como si estuviera completo cuando no lo está.
- [ ] **Ítem 8 — Comparación histórica (fase 2):** requiere que exista más de un `Diagnostic` por organización — hoy es get-or-create, a lo sumo uno (ver backlog de Autodiagnóstico más arriba, "Re-evaluaciones").
- [ ] **Ítem 9 — Cierre formal:** bloque de validación/firma (nombre, cargo, fecha) del responsable que revisa, y etiqueta de clasificación de confidencialidad del documento.

### Nota de estrategia — freemium vs. Carpeta de Evidencia (decisión del usuario, 2026-08-10)

El anexo de respuestas crudas y, en general, cualquier bitácora de auditoría fina (quién respondió qué y cuándo) se reserva deliberadamente para la Carpeta de Evidencia (Módulo 5, de pago) en vez de incluirse gratis en el informe del Autodiagnóstico (Módulo 1, "gancho freemium"). El resumen + puntajes + hallazgos ya bastan para mostrarle a la PYME que tiene brechas; el valor probatorio detallado (evidencia formal ante la Agencia) es lo que debería empujar la conversión a suscripción. Los campos de auditoría (`created_by`/`updated_by`/`updated_at`) sí se construyeron ya en el modelo de datos porque son la base necesaria para que el Módulo 5 los explote más adelante — no se exponen todavía como anexo en el informe gratuito.

## Módulo 2 — M2-T3.0, activación del RAT

- [x] `Treatment` guarda declaraciones explícitas `si`/`no`/`pendiente` para sistemas, terceros/proveedores y transferencias internacionales; `null` representa ausencia de declaración.
- [x] Activación server-side exige nombre, rol, una finalidad, categoría de datos, categoría de titulares, fuente de datos, regla de conservación y las tres declaraciones.
- [x] Transiciones permitidas: borrador→activo, activo→borrador, activo→archivado, borrador→archivado y archivado→activo; ambas activaciones validan requisitos.
- [x] M2-T3.1: listado RAT y navegación frontend.

## Módulo 2 — M2-T3.1, listado RAT y navegación frontend

**Estado:** DONE (2026-09-16)

- [x] Vista `/dashboard/rat`.
- [x] Integración con `GET /rat/treatments`.
- [x] Selector de organización.
- [x] Estados loading, empty y error.
- [x] UX específica para HTTP 402 y 403.
- [x] CTA `Nueva actividad`.
- [x] Navegación a `/dashboard/rat/nuevo`.
- [x] Navegación a `/dashboard/rat/[treatmentId]`.
- [x] Tarjeta RAT habilitada en dashboard.
- [x] TypeScript PASS.
- [x] Next production build PASS.

**M2-T3.2 completado. Siguiente:** M2-T3.3 — finalidades, categorías de datos, titulares y fuentes.

## Módulo 2 — M2-T3.2, información general RAT

**Estado:** DONE (2026-09-16)

- [x] Crear actividad desde `/dashboard/rat/nuevo`.
- [x] Cargar detalle desde `/dashboard/rat/[treatmentId]`.
- [x] Editar y guardar información general.
- [x] Integración con `POST`, `GET` y `PATCH /rat/treatments`.
- [x] Nombre, descripción, área de negocio y rol de la organización.
- [x] Descripción general del flujo de datos.
- [x] Fecha de inicio y próxima revisión.
- [x] Regla de conservación y método de eliminación.
- [x] Decisiones automatizadas y descripción condicional.
- [x] Barra de preparación basada en 10 requisitos de activación.
- [x] Estado visual `borrador` → `Registro en preparación`.
- [x] Advertencia de que el avance no representa cumplimiento legal.
- [x] Prueba funcional de creación, edición y listado.
- [x] TypeScript PASS.
- [x] Next production build PASS.

**Siguiente:** M2-T3.3 — finalidades, categorías de datos, titulares y fuentes.


## Módulo 3 — M3-T1, persistencia y reglas de bases de licitud

**Estado:** EN PROGRESO (revisión 2026-10-06).

Matriz de implementación, evidencia y brechas en
[Revisión de aceptación M3-T1](project/m3-t1-revision-aceptacion.md).
Diseño y alcance en [Bases de licitud](project/modulo3-licitud-diseno.md).
Suite completa backend de CI: 3977 passed en commit 7f94bbf (§232); no acredita cierre integral ni los commits posteriores.

- [x] Núcleo persistente, alcance por finalidad, snapshot/hash, RLS y lifecycle.
- [x] Seis bases ordinarias; geolocalización y consentimiento expreso sensible
  del titular con preparación, asociaciones y barreras de confirmación.
- [x] Screening EIPD; positivos/pendientes mantienen bloqueo.
- [x] Completar evidencia HTTP conjunta sensible/geolocalización (4 casos
  focalizados aprobados: pérdida de preparación, EIPD y conservación/reemplazo).
- [x] Ampliar concurrencia con constructor RAT real: consentimiento con
  sensibilidad/geolocalización, 8 casos nuevos; otras cinco bases conservan
  cobertura de concurrencia con RAT simulado.
- [x] Priorizar próximo régimen: salud/perfil biológico; primer alcance
  documental por consentimiento expreso, diseño §31.
- [x] Definir contrato/matriz documental de salud (§32).
- [x] Implementar schema de salud y pruebas (§33: 49 pruebas nuevas).
- [x] Persistencia/exposición de salud y asociaciones compatibles (§34).
- [x] Evaluador de salud y readiness (§35).
- [x] Integración del gate de salud para primer soporte; restricciones y EIPD conservados (§36).
- [x] HTTP conjunto salud/sensible/geolocalización y concurrencia de salud con RAT real
  por consentimiento_art12/contexto otro (§37: 18 casos nuevos; 35 verificaciones focalizadas).
- [x] Revisar alcance de representación sensible y criterios de cierre M3-T1 (§38);
  revisión no equivale a cierre ni habilita representación.
- [x] Verificar por HTTP representante_legal/mandatario en sensible, con y sin salud:
  rechazo, conservación del vigente y reparación a titular.
- [x] Validación integral posterior a representación (§39): 1429 passed.
- [x] Revisión focalizada de cambios y cadena Alembic (§40): head aplicado,
  46 archivos con formato/lint correctos; tablas M3 sin diferencias autogenerate.
- [x] Investigar/corregir drift global de metadata sin eliminar índices (§41):
  29 índices declarados y nombre de unique alineado; alembic check aprobado.
- [x] Preparar propuesta concreta de entrega inicial y pendientes (§42):
  [Propuesta de alcance](project/m3-t1-propuesta-entrega.md).
- [x] Decisión explícita: continuar alcance integral (§43); entrega inicial no
  adoptada como recorte de cierre.
- [x] Actualizar aceptación según decisión integral (§43).
- [x] Biometría: contrato/matriz de primera ruta consentimiento expreso (§44).
- [x] Biometría: schemas y pruebas (§45: 53 casos nuevos; 150 contratos aprobados).
- [x] Biometría: persistencia/API/asociaciones compatibles (§46): diez casos HTTP;
  suite integral 1492 passed y Alembic check aprobado.
- [x] Biometría: evaluador puro/readiness (§47): 73 pruebas puras y un caso HTTP
  nuevos; suite integral 1566 passed.
- [x] Biometría: integrar gate/EIPD y HTTP de primera ruta (§48): 19 pruebas
  transversales nuevas; suite integral 1585 passed.
- [x] Biometría: HTTP seis bases y concurrencia con RAT real (§49): 22 casos
  nuevos; 58 verificaciones focalizadas. Concurrencia real: consentimiento_art12.
- [x] Delimitar primera excepción biométrica: derechos art16ter -> art16bis(d),
  con dependencia sensible art16d y barrera EIPD conservada (§50).
- [x] Diseñar contratos/matriz de excepción sensible y biométrica de derechos (§51).
- [x] Implementar schemas/pruebas de ambas excepciones (§52): 102 casos nuevos,
  252 contratos seleccionados aprobados.
- [x] Persistencia/API de ambas excepciones (§53), con barrera explicita
  mientras falta cobertura de asociaciones y tres casos HTTP aprobados.
- [x] Asociaciones especiales v10/EIPD v11 de ambas excepciones (§54), con
  comparadores historicos, obsolescencia y reaporte explicito; 118 casos nuevos.
- [x] Evaluador puro de preparacion/aplicabilidad sensible de derechos (§55);
  172 casos aprobados, sin habilitar confirmacion.
- [x] Readiness e integracion sensible en detector/gates (§56), residualidad
  explicita en ambos sentidos y EIPD conservado; doce casos nuevos.
- [x] Evaluador puro biometrico de derechos y vinculos sensibles (§57),
  208 casos aprobados, sin habilitar confirmacion.
- [x] Readiness e integracion biometrica en detector/gates (§58), residualidad
  explicita y EIPD conservado; doce casos nuevos, sin confirmar excepciones.
- [x] Delimitar resolucion EIPD acotada (§59): registro externo, revision humana
  trazable y gate separado; screening positivo conservado, sin habilitacion actual.
- [ ] Contratos/matriz, schemas, persistencia/eventos y evaluadores de resolucion
  EIPD; aislamiento, obsolescencia y concurrencia antes de habilitar la frontera.
- [ ] Verificar/registrar listas y orientaciones oficiales aplicables antes de
  desbloquear confirmaciones; busqueda acotada no acredita inexistencia.
- [ ] Completar demás excepciones biométricas dentro del alcance integral.
- [ ] Completar representación, excepciones sensibles/salud y contextos restringidos,
  infancia/adolescencia, investigación y alcance granular según diseño propio.
- [ ] Validación y revisión final del alcance integral antes de declarar DONE.

Workflow completo EIPD diferido; frontend M3 no se agrega como requisito de
esta tarea mediante esta revisión. Sin cierre DONE ni commit.

- [x] M3-T1 §60: contratos/matriz de resolucion EIPD, documento parcial, condicionales y revision humana con campos de servidor definidos (solo diseño).
- [x] M3-T1 §61: schemas separados de resolucion/revision EIPD y 111 pruebas de contrato implementados; 419 pruebas de schemas aprobadas.
- [x] M3-T1 §62: asociacion/hash de resolucion v1 puros implementados; 89 pruebas nuevas y 296 focalizadas aprobadas.
- [x] M3-T1 §63: persistencia JSONB y eventos append-only/RLS de resolucion EIPD; migracion b51d3f6a9c20 y 36 casos PostgreSQL, suite integral 2470 passed.
- [x] M3-T1 §64: API documental/binding de resolucion EIPD; 25 HTTP con RAT real y suite integral 2495 passed, historial conservado.
- [x] M3-T1 §65: evaluador puro de preparacion documental EIPD; 159 pruebas nuevas y 455 focalizadas aprobadas, sin habilitar confirmacion.
- [x] M3-T1 §66: readiness documental y vigencia de ultima revision EIPD; 18 pruebas nuevas aprobadas, sin habilitar confirmacion.
- [x] M3-T1 §67: prerequisitos puros de revision EIPD; 38 pruebas nuevas y 215 focalizadas aprobadas; continuar bloqueado por frontera/fuentes pendientes.
- [x] M3-T1 §68: accion autenticada de revision EIPD, campos de servidor, historial y relectura bajo lock; 15 pruebas nuevas aprobadas.
- [ ] M3-T1: frontera/gates, concurrencia ampliada y fuentes pendientes antes de habilitar confirmacion.

- [x] M3-T1 §69: registro trazable de busqueda/fuentes EIPD y propuesta temporal; listas/orientaciones no verificadas, requisito global pendiente.

- [x] M3-T1 §70: base normativa fija autorizada por usuario y matriz/contrato de primera frontera EIPD, sin dependencia de fecha de entrada en vigor.
- [x] M3-T1 §71: evaluador puro de frontera §70 implementado; 106 pruebas nuevas y 695 focalizadas aprobadas, screening v1 preservado.
- [x] M3-T1 §72: deteccion EIPD v2 pura y nucleo compartido con v1; positivos e historia conservados, 56 pruebas nuevas.
- [x] M3-T1 §73: readiness v2/frontera separado y versionado, contexto RAT actual y contratos cerrados; 14 pruebas nuevas.
- [ ] M3-T1: composicion compartida, fuentes complementarias/aceptacion antes de habilitar continuar.

- [x] M3-T1 §74: contrato/matriz de composicion comun EIPD y separacion revision/confirmacion, sin circularidad.
- [x] M3-T1 §75: composicion pura §74 implementada; 80 pruebas nuevas y 468 focalizadas aprobadas, sin habilitar gates.
- [x] M3-T1 §76: composicion orientativa en readiness, contratos cerrados y 17 pruebas nuevas; bloqueos conservados.
- [x] M3-T1 §77: composicion compartida bajo lock en revision positiva/confirmacion; barreras conservadas y seis casos nuevos.
- [x] M3-T1 §78: concurrencia real de confirmacion y HTTP seis bases ordinarias para composicion; ocho casos adicionales.
- [x] M3-T1 §79: revision de aceptacion acotada y revalidacion registrada de fuentes; frontera no habilitada, instrumento complementario no verificado.
- [x] M3-T1 §80: HTTP preparado de ambas rutas protegidas con/sin negativa previa; cuatro casos nuevos y barreras conservadas.
- [x] M3-T1 §81: concurrencia real de ambas rutas protegidas preparadas, revision/confirmacion y commit/rollback; ocho casos nuevos.
- [x] M3-T1 §82: aceptacion §§80-81 actualizada y contrato de politica/gate v2 exclusivo de servidor, sin habilitar.
- [x] M3-T1 §83: politica pura y composicion v2 con contratos cerrados, identidad de evento/politica y 104 pruebas nuevas; v1 conservado.
- [x] M3-T1 §84: identidad de politica nullable en eventos, migracion c62e407bad31, contratos/mapper y 35 pruebas nuevas; historicos/RLS conservados.
- [x] M3-T1 §85: resolver fijo deshabilitado y readiness v2/identidad; una consulta de historial y 26 pruebas nuevas, gates v1 conservados.
- [x] M3-T1 §86: prerequisitos puros de revision v2, negativos parciales y positivos con composicion/politica; 110 pruebas nuevas y suite completa 3299 passed.
- [x] M3-T1 §87: revision autenticada v2 bajo lock con politica deshabilitada/metadatos de servidor; diez HTTP nuevos y suite completa 3309 passed.
- [x] M3-T1 §88: decision transversal/confirmacion v2 bajo lock, alcance ordinario conservado; once HTTP nuevos, concurrencia ampliada y suite completa 3320 passed.
- [x] M3-T1 §89: contrato de publicacion inmutable/selector auditado, orden de locks, revocacion y evidencia atomica de confirmacion; solo diseno.
- [x] M3-T1 §90: contratos/evaluadores puros de publicacion/seleccion/evidencia, coherencia/hash y 65 pruebas nuevas; suite completa 3385 passed.
- [x] M3-T1 §91: persistencia de control global, migracion d73f518cbe42, privilegios/RLS y consistencia diferida; 44 PostgreSQL nuevas y suite completa 3429 passed.
- [x] M3-T1 §92: evidencia append-only tenant, migracion e84a629dcf53, FK/RLS y 29 PostgreSQL nuevas; suite completa 3458 passed.
- [x] M3-T1 §93: servicios internos de publicacion/seleccion deshabilitada y lectura validada, bootstrap/seleccion concurrentes; 24 PostgreSQL nuevas y suite completa 3482 passed.
- [x] M3-T1 §94: resolver transaccional/bloqueo compartido limitado, migracion f95b73aed064; 15 PostgreSQL nuevas y suite completa 3497 passed.
- [x] M3-T1 §95: revision humana con selector auditado deshabilitado, identidad real y nueve PostgreSQL nuevas (cuatro concurrencias); Suite completa: 3506 passed en 313.64 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §96: readiness/confirmacion con selector auditado y orden compatible, ordinario sin selector conservado; 13 PostgreSQL nuevas; Suite completa: 3519 passed en 329.62 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §97: evidencia atomica conectada antes de reemplazo, guardia productiva conservada y 12 PostgreSQL nuevas de exitos sinteticos/fallos; Suite completa: 3531 passed en 334.47 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §98: confirmaciones exitosas concurrentes y revocacion conservan evidencia; 12 PostgreSQL nuevas; Suite completa: 3543 passed en 343.50 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §99: exitos independientes/aislamiento y PATCH concurrente; 12 PostgreSQL nuevas; Suite completa: 3555 passed en 345.51 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §100: contrato de autoridad personal (JWT/superadmin/canal separado), precondicion de proteger perfiles y matriz; solo documentacion.
- [x] M3-T1 §101: auditoria efectiva local y proteccion de identidad/autoridad de perfiles, migracion a06c84bf175e; 12 PostgreSQL nuevas; Suite completa: 3567 passed en 431.30 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §102: barrera personal limitada perfil/rol/lock, migracion b17d95c0286f y nueve PostgreSQL nuevas; 45 focalizadas aprobadas, sin conexion a escritores.
- [x] M3-T1 §103: escritores personales con actor derivado y 11 PostgreSQL nuevas; 44 focalizadas aprobadas; Suite completa: 3587 passed en 348.04 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §104: pool separado y dependencia JWT/sub local/autoridad, 17 pruebas nuevas; 47 focalizadas aprobadas. Suite completa: 3604 passed en 352.09 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §105: endpoints administrativos con JWT verificado/pool real, 38 HTTP nuevas; 85 focalizadas aprobadas. Suite completa: 3642 passed en 355.96 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §106: doce HTTP concurrentes (revocacion/rollback/cancelacion/seleccion/unicidad); 97 focalizadas aprobadas. Suite completa: 3654 passed en 369.30 s; Black/Ruff/Alembic check/diff correctos.
- [x] M3-T1 §107: revalidacion documental de fuentes base/busqueda complementaria y matriz de trazabilidad a commits; sin cambio de gates ni nueva suite.
- [x] M3-T1 §108: procedimiento de provision deshabilitada preparado, JSON de ejemplo validado; sin provision real ni cambios de gates.
- [x] M3-T1 §109: preflight readonly limitado y seis pruebas nuevas; 23 focalizadas aprobadas, sin escrituras/provision operativa.
- [x] M3-T1 §110: permisos efectivos de grupo/login/public/RLS en preflight e informe v1; ocho nuevas, 31 focalizadas aprobadas.
- [x] M3-T1 §111: expediente inicial con configuracion ausente/preflight failed esperado y head local comprobados; sin provision real.
- [x] M3-T1 §112: usuario selecciona local; inspeccion readonly y accion de provision concreta preparada, sin ejecutar tras rechazo automatico.
- [x] M3-T1 §113: provision tecnica local explicitamente autorizada, login limitado/credencial privada; preflight pending_selector (2), sin bootstrap.
- [x] M3-T1 §115: superadmin global local explicitamente autorizado y confirmado en perfil existente; sin cambios Supabase/politicas.
- [x] M3-T1 §116: UID aportado contrastado con perfil local autorizado; backend/rutas registrados, rechazo anonimo 401 probado.
- [x] M3-T1 §117: proceso local separado con secreto en memoria, health/401 y Supabase/JWKS 200; vinculo staff externo verificado por consulta admin.
- [ ] M3-T1: sesion/JWT personal real y humo autenticado, publicacion/seleccion deshabilitada y validacion/retirada operativas; fuentes/aceptacion pendientes.

## M3-T1 §118 — acceso personal local (2026-10-09)

- [x] Endpoint administrativo de lectura y pantalla local de comprobacion; 40 pruebas API y checks frontend aprobados.
- [x] Comprobar acceso con sesion personal real: resultado confirmado en captura aportada por el usuario (2026-10-09).
- [ ] Validar publicacion/seleccion de politica deshabilitada y auditoria con sesion personal.
- [ ] Completar fuentes complementarias, aceptacion y validacion operacional integral; activacion excepcional bloqueada.

## M3-T1 §119 — registro operacional

- [x] Consulta administrativa autenticada del snapshot validado y pantalla de revision; 54 pruebas focalizadas aprobadas.
- [x] Consulta con sesion personal confirmada por captura: revision 0, publicaciones 0, selecciones 0 (2026-10-09).
- [ ] Preparar publicacion deshabilitada y comprobar persistencia/auditoria; luego seleccionar con revision vigente.

## M3-T1 §120 — publicacion local deshabilitada

- [x] Propuesta fija autenticada, vista revisable y publicacion explicita con comprobacion posterior; 56 pruebas focalizadas aprobadas.
- [x] Publicacion con sesion personal confirmada por captura: 1 publicacion deshabilitada, 0 selecciones, revision 0 (2026-10-09).
- [ ] Preparar seleccion explicita con revision vigente y verificar evento/selector en la auditoria.

## M3-T1 §121 — seleccion deshabilitada

- [x] Preparar seleccion con revision vigente y comprobar evento/hash/selector; checks frontend y 56 pruebas API aisladas aprobadas.
- [x] Seleccion personal confirmada por capturas y snapshot tecnico readonly coherente: revision 1, 1 publicacion y 1 seleccion deshabilitada (2026-10-09).
- [ ] Revisar cierre operacional y pendientes de provision/rotacion/retiro y aceptacion integral; activacion bloqueada.

## M3-T1 §122 — cierre delimitado de validacion local

- [x] Consolidar secuencia personal deshabilitada, coherencia persistida y preflight posterior ok; head verificado.
- [x] Separar pendientes operacionales y juridicos en docs/project/m3-t1-eipd-cierre-validacion-local.md.
- [x] Preparar ejecutor focalizado que exige base aislada antes de pytest: §123, 60 pruebas aprobadas. Pytest directo no queda protegido por el wrapper.
- [ ] Validar rotacion/retiro y recuperacion, fuentes/aceptacion y alcance integral; M3-T1 EN PROGRESO.

## M3-T1 §123 — pruebas aisladas

- [x] Ejecutar suite focalizada mediante guardas de destino/head/roles/estado, con 60 aprobadas.
- [x] Ejecutar ensayo aislado de rotacion/retiro y recuperacion §124: 63 pruebas aprobadas; snapshot de pruebas sin cambios.
- [ ] Validar ciclo de vida del canal provisionado con historial real y renovacion segura de procesos; no ejecutado en §124.

## M3-T1 §125 — rotacion real preparada

- [x] Verificar canal/destino/head y preparar drenaje, reemplazo privado, recuperacion y comprobacion posterior.
- [x] Rotacion real local ejecutada §126: credencial anterior rechazada en conexion nueva; nuevo canal ok y snapshot completo intacto.
- [x] Acceso personal tras reinicio confirmado por captura y copia privada anterior retirada (§126).

## M3-T1 §127 — retiro reversible real

- [x] Drenar canal real, comprobar NOLOGIN con conexion nueva, restaurar LOGIN y verificar snapshot completo intacto/revision 1.
- [x] Acceso personal tras reinicio de recuperacion confirmado por captura §127. Retiro definitivo no ejecutado.

## M3-T1 §128 — investigacion documental

- [x] Delimitar primer incremento de investigacion con datos no sensibles/adultos y LIA, completitud/aplicabilidad y fuente primaria.
- [x] Implementar schema/evaluador puro §129; sin persistencia ni gates, can_confirm=false.
- [x] Ampliar aplicabilidad/limites §130: 20 casos nuevos; suite aislada 107 aprobadas.
- [x] Implementar binding independiente de investigacion y chequeo de obsolescencia §131; 119 pruebas aisladas aprobadas. Historicos intactos, sin conversion automatica.
- [x] Delimitar persistencia/API §132 en docs/project/m3-t1-investigacion-integracion.md.
- [x] Schema/modelo/migracion nullable sin backfill §133; 121 pruebas aisladas, upgrade/check en ambas bases y auditoria EIPD intacta.
- [x] Integrar servicios/API create/GET/PATCH con binding de servidor y pruebas de acceso §134; nuevas asociaciones especiales/EIPD pendientes.

### M3-T1 §134 — API del expediente de investigacion

- [x] Create/GET/PATCH con binding de servidor y omision/null/reaporte; contratos cliente cerrados.
- [x] 127 pruebas focalizadas aprobadas y 174 HTTP existentes de compatibilidad aprobadas; estados historicos protegidos.
- [x] Readiness documental/asociacion de investigacion §135. Confirmacion sigue bloqueada; M3-T1 EN PROGRESO.
- [ ] Nuevas versiones especiales/EIPD que cubran investigacion y aceptacion revisada antes de habilitar el gate.

### M3-T1 §135 — Readiness de investigacion

- [x] Completitud, aplicabilidad y asociacion vigentes/obsoletas expuestas sin escrituras; bloqueo compartido de confirmacion incluso con expediente completo.
- [x] 303 pruebas ampliadas aisladas aprobadas; Black/Ruff aprobados.
- [ ] Nuevas versiones de binding especial/EIPD e integracion posterior; M3-T1 EN PROGRESO y activacion bloqueada.

### M3-T1 §136 — Asociaciones para investigacion

- [x] Delimitar versiones sucesoras especiales V11/EIPD V12, material, compatibilidad y orden PATCH.
- [x] Implementar contratos/funciones puras nuevos con pruebas de hashes historicos intactos §137; 145 focalizadas aprobadas.
- [ ] Dispatch y servicio/API, luego contexto de resolucion/revision y aceptacion. Confirmacion investigacion/EIPD bloqueadas.

### M3-T1 §137 — Asociaciones puras sucesoras

- [x] Contratos cerrados especiales V11/EIPD V12 y hash/bind de expediente completo sin reparar bindings research.
- [x] 16 casos nuevos y 145 focalizados aprobados; funciones historicas verificadas intactas, Black/Ruff aprobados.
- [x] Dispatch evaluador y falta de cobertura historica §138; escritura API pendiente. Gates siguen bloqueados.

### M3-T1 §138 — Evaluacion versionada de investigacion

- [x] Dispatch especiales V11/screening V12 y falta de cobertura independiente para versiones anteriores con investigacion.
- [x] 8 casos nuevos; suite ampliada aislada 327 aprobadas, Black/Ruff aprobados.
- [x] Generacion API de asociaciones sucesoras y pruebas de orden PATCH §139. Confirmacion investigacion/EIPD bloqueadas.

### M3-T1 §139 — API de asociaciones sucesoras

- [x] Create/PATCH especiales V11/screening V12 con valores finales y conservacion de asociaciones omitidas.
- [x] Dos casos HTTP nuevos; 329 ampliadas y 162 regresiones frontera/screening V2 aprobadas.
- [ ] Revisar cobertura versionada del contexto de resolucion/revision EIPD de investigacion; gates bloqueados.

### M3-T1 §140 — Resolucion/revision EIPD de investigacion

- [x] Revisar cobertura V1 y delimitar contratos V2, compatibilidad historica y frontera de revision/eventos.
- [x] Implementar contexto/binding/Stored V2 y funciones puras con pruebas V1 intactas §141.
- [ ] Dispatch, frontera/composicion, metadatos de eventos y escritura API posteriores; gates bloqueados.

### M3-T1 §141 — Asociacion pura de resolucion V2

- [x] Contexto cerrado con investigacion explicitamente nullable, binding/Stored V2 separados y hashes nuevos sin reparacion.
- [x] 323 focalizadas aisladas aprobadas (9 nuevas y regresiones V1); Black/Ruff aprobados.
- [x] Dispatch documental/readiness/revision puro de investigacion §142; frontera/composicion/escritor pendientes. Gates bloqueados.

### M3-T1 §142 — Resolucion/revision evaluadas por version

- [x] Dispatch puro V1/V2 y cobertura research explicita; evento historico visible sin autoridad sintetica.
- [x] 327 focalizadas y 272 regresiones de frontera/screening/revision aprobadas; Black/Ruff aprobados.
- [ ] Frontera/composicion research y posterior lectura/escritura API V2; gates bloqueados.

### M3-T1 §143 — Frontera/composicion investigacion

- [x] Delimitar FrontierV2/ScreeningV3/CompositionV3 y cobertura ContextV2 sin reinterpretar historicos.
- [x] Implementar frontera V2 pura y pruebas con bloqueo conservador §144; 337 focalizadas aprobadas.
- [ ] Screening/composicion, luego API/metadatos de eventos y aceptacion revisada. Gates bloqueados.

### M3-T1 §144 — Frontera pura investigacion V2

- [x] Evaluacion documental/asociacion y motivos especiales/screening completos; discordancias y falta de cobertura historica detectadas.
- [x] 10 casos nuevos y 337 focalizados aislados aprobados; Black/Ruff aprobados.
- [ ] Screening/composicion V3 y luego API/metadatos de eventos/aceptacion. Gates bloqueados.

### M3-T1 §145 — Screening V3 conservador

- [x] Screening sobre ContextV2/frontera V2 conserva todos los motivos y bloquea continuacion/confirmacion.
- [x] Contratos historicos separados; once casos nuevos.
- [ ] Composicion V3 y posterior API/metadatos de eventos/aceptacion.

### M3-T1 §146 — Composicion V3 de investigacion

- [x] Contratos cerrados y composicion pura con ContextV2, screening V3 y resolucion versionada.
- [x] Motivos completos, vigencias separadas, revision ajena/obsoleta visible y confirmacion bloqueada.
- [ ] Lectura API versionada, escritor/metadatos de eventos y aceptacion revisada.

### M3-T1 §147 — Lectura API V3 de investigacion

- [x] Readiness V3 con RAT actual/research persistido y politica real o ausencia explicita.
- [x] Contratos de salida cerrados, lectura sin escritura y bloqueo conservador.
- [ ] Escritor de resolucion versionado, metadatos auditables de eventos y aceptacion.

### M3-T1 §148 — Escritor puro versionado

- [x] Seleccion V1/V2 por contexto final y antecedente persistido, sin downgrade V2.
- [x] Research declarado sin documento conserva cobertura V2; ordinario mantiene binding V1.
- [ ] Integrar POST/PATCH y consumidores, metadatos auditables y aceptacion.

### M3-T1 §149 — Escritor API versionado

- [x] POST/PATCH con contexto final, antecedente persistido, omision/null/reaporte y salida V1/V2.
- [x] Readiness por version sin aplicar composiciones historicas a V2; acciones V2 bloqueadas sin eventos.
- [ ] Metadatos auditables/prerequisitos versionados de revision y aceptacion.

### M3-T1 §150 — Metadatos auditables puros

- [x] Contrato cerrado/versiones estrictas y generador/comparador de identidad de material V1/V2.
- [x] Ausencia historica conservada; cobertura research explicita sin autoridad ni proyeccion.
- [ ] Persistencia append-only/lectura de metadata, prerequisitos V2 y aceptacion.

### M3-T1 §151 — Almacenamiento de metadata

- [x] Columna nullable sin backfill, contrato/hashes comprobados y lectura ORM/pura conservadora.
- [x] Migracion aislada/local verificada, historia intacta y 445 pruebas aprobadas.
- [ ] Visibilidad API, prerequisitos de eventos V2 y aceptacion; acciones bloqueadas.

### M3-T1 §152 — Metadata visible en readiness V3

- [x] Lectura actual/historica separada por identidad, una consulta y sin fallback ni escrituras.
- [x] 465 pruebas aprobadas; metadata vigente no levanta bloques de revision/confirmacion.
- [ ] Prerequisitos puros versionados de revision, registro controlado y aceptacion.

### M3-T1 §153 — Prerequisitos puros V3

- [x] Identidad V2/cobertura explicita generada desde servidor; negativas parciales y positivos con controles comunes.
- [x] 560 pruebas aisladas aprobadas; sin eventos ni activacion y contratos historicos intactos.
- [ ] Registro controlado de negativas V2 con metadata, locks/aislamiento y aceptacion; positivos bloqueados.

### M3-T1 §154 — Negativas HTTP V2 con metadata

- [x] Registro autenticado bajo locks/relectura con hashes y metadata de servidor atomicos.
- [x] 578 pruebas aisladas aprobadas: negativas, tenant, obsolescencia, rollback y regresiones historicas.
- [ ] Concurrencia especifica V2/cambio de politica, consumidores y aceptacion; positivos bloqueados.

### M3-T1 §155 — Concurrencia negativa V2

- [x] Relectura tras PATCH/selector, commit/rollback e historia intacta con bloqueos PostgreSQL observados.
- [x] 603 pruebas aisladas aprobadas; escritor existente conserva garantias sin cambio productivo.
- [ ] Negativas simultaneas/cancelacion, consumidores y aceptacion; positivos/confirmacion bloqueados.

### M3-T1 §156 — Simultaneidad y cancelacion V2

- [x] Negativas independientes serializadas, commit/rollback y ultimo evento con identidad exacta.
- [x] Cancelacion libera locks sin evento parcial; reintento vigente. 607 pruebas aisladas aprobadas.
- [ ] Lectura de prerequisitos por decision en readiness y aceptacion; positivos/confirmacion bloqueados.

### M3-T1 §157 — Diagnostico documental por decision

- [x] Readiness V3 expone prerequisitos y metadata actual por decision; sin autoridad ni eventos ficticios.
- [x] Kernel compartido con validacion humana preservada; 615 pruebas aisladas aprobadas.
- [ ] Salida versionada de eventos V2, consumidores y aceptacion; positivos/confirmacion bloqueados.

### M3-T1 §158 — Respuesta auditada versionada

- [x] POST/GET de representacion V2 con identidad persistida; contrato historico intacto y null sin inferir.
- [x] Lectura por tenant/padre/estado, permisos/suscripcion y 621 pruebas aisladas aprobadas.
- [ ] Consumidor frontend tipado y aceptacion; positivos/confirmacion/activacion bloqueados.

### M3-T1 §159 — Cliente frontend de revisiones

- [x] Tipos/cliente de requisitos y eventos auditados; negativos sin inyeccion ni autoridad derivada.
- [x] 11 pruebas de red simulada y type-check/lint frontend aprobados; backend sin cambios.
- [ ] Pantalla interna solo lectura y aceptacion; modulo/confirmacion/activacion bloqueados.

### M3-T1 §160 — Consulta interna solo lectura

- [x] Ruta bajo layout administrativo con sesion/contexto explicitos, requisitos y evento historico sin autoridad.
- [x] 4 interacciones Chromium aisladas + 11 regresiones del cliente, type-check/lint aprobados.
- [ ] Validacion real de sesion/expediente y aceptacion; modulo/confirmacion/activacion bloqueados.

### M3-T1 §163 — Presentacion de motivos de consulta

- [x] Etapas, campos y preguntas visibles; duplicados exactos con cantidad y detalle original.
- [x] 5 pruebas de interaccion, tipos y lint frontend aprobados.
- [x] Inspeccion visual con sesion y expediente ficticio local: etapas, campos y detalle original.
- [ ] Ampliar traducciones de campos; prueba directa de API entre cuentas pendiente.

### M3-T1 §164 — Etiquetas documentales

- [x] Ampliar traducciones de campos manteniendo identidad original en detalle.
- [x] Tipos y lint frontend aprobados.
- [x] Inspeccion manual: uso exclusivo y controles en español; detalle original preservado.
- [ ] Traducir rutas restantes (conclusion/balancing_summary/decision); API entre cuentas pendiente.

### M3-T1 §165 — Etiquetas de interes legitimo

- [x] Traducir secciones/campos LIA v1 y conservar identificadores del detalle.
- [x] Tipos y lint frontend aprobados.
- [ ] Inspeccion visual de rutas LIA en expediente ficticio; API entre cuentas pendiente.

### M3-T1 §166 — Diagnostico visible en español

- [x] Traducir detalle, etapas, categorias y campos; fallback desconocido en español.
- [x] 5 interacciones Chromium, tipos y lint aprobados.
- [x] Captura manual confirma detalle de justificacion en español (§167).
- [ ] API entre cuentas y cobertura de otras rutas pendientes.

### M3-T1 §168 — Navegacion por temas

- [x] Desplegables con cantidad de motivos distintos y total de ocurrencias conservado.
- [x] 6 interacciones Chromium, tipos y lint aprobados.
- [ ] Inspeccion manual con expediente ficticio; API entre cuentas pendiente.

### M3-T1 §169 — Amplitud y detalle

- [x] Decisiones a ancho completo, motivos separados y detalle con etiquetas destacadas.
- [x] Tipos/lint y 6 interacciones aprobados.
- [x] Captura de escritorio confirma ancho y detalle de justificacion/investigacion.
- [ ] Vista movil y otros temas; API entre cuentas pendiente.

### M3-T1 §173 — Estado documental de ultima revision

- [x] Proyeccion validada del estado existente y aviso sin autoridad separado de requisitos/historia.
- [x] 12 cliente, 7 interacciones, tipos y lint aprobados.
- [x] Captura del expediente ficticio: vinculo vigente, aviso sin autoridad y Continuar pendiente.
- [x] Captura historica: evento anterior intacto, aviso historico y bloque actual ausente.
- [ ] Prueba directa API entre cuentas y otros estados reales pendientes.

### M3-T1 §174 — Vista a ancho reducido

- [x] Capturas de vista general e Investigacion: ajuste de texto y detalle apilado legible.
- [ ] Dispositivo movil, otras anchuras/temas y medicion de overflow pendientes.
- [ ] Prueba directa API entre cuentas pendiente.

### M3-T1 §175 — Emulacion de 390 pixeles

- [x] Captura Edge Responsive 390 x 749: detalle de Investigacion legible y textos ajustados.
- [ ] Medicion de overflow, formularios, otros temas y dispositivo fisico pendientes.
- [ ] Mensajes de consola no inspeccionados; API entre cuentas pendiente.

### M3-T1 §176 — Medicion a 390 pixeles

- [x] Comparacion scrollWidth > clientWidth retorna false con Investigacion/detalle abiertos.
- [ ] Otros estados/anchuras, overflow interno y dispositivo fisico pendientes.

### M3-T1 §177 — Cabecera movil

- [x] Titulo, cuenta y cierre apilados bajo sm; correo largo ajustable.
- [x] Captura posterior a 390 pixeles confirma cabecera apilada y titulo legible.
- [ ] Accion de botones y otros anchos pendientes.

### M3-T1 §178 — Consulta movil

- [x] Resultado manual a 390 pixeles: borrador, vinculo vigente y Continuar pendiente.
- [ ] Consulta historica y cierre de sesion en vista movil pendientes.

### M3-T1 §179 — Historia movil

- [x] Captura a 390: evento original legible, aviso historico y bloque actual ausente.
- [ ] Cierre de sesion movil y API entre cuentas pendientes.

### M3-T1 §180 — Cierre de sesion movil

- [x] Captura /login tras cierre y reporte de redireccion al reabrir consulta sin sesion.
- [ ] Prueba directa API entre cuentas y revocacion no acreditadas por navegacion.

### M3-T1 §181 — Reingreso movil

- [x] Captura tras reingreso: panel y cuenta visibles, tres campos de expediente vacios.
- [x] Segunda captura del final: Revision vacia y resultados anteriores ausentes.

### M3-T1 §182 — Campo Organizacion requerido

- [x] Captura a 390: aviso nativo en Organizacion vacia y sin resultados visibles.
- [ ] Otros campos y validacion directa backend no acreditados por esta captura.

### M3-T1 §183 — Campos de expediente requeridos

- [x] Capturas a 390: aviso nativo en Tratamiento y Evaluacion vacios, sin resultados visibles.
- [ ] Validacion directa backend no acreditada por estas capturas.

### M3-T1 §184 — Revision requerida

- [x] Captura a 390: Revision vacia exige completar campo con expediente identificado.
- [ ] Validacion directa backend no acreditada por esta captura.

### M3-T1 §185 — Formato de Revision

- [x] Captura a 390: prueba rechazada por formato nativo, sin revision visible.
- [ ] Peticiones de red y validacion directa backend no acreditadas por esta captura.

### M3-T1 §186 — Recuperacion de consulta

- [x] Captura a 390: formato corregido recupera evento original sin aviso de formato.
- [ ] Prueba directa API entre cuentas pendiente.

### M3-T1 §187 — Limpieza al cambiar Organizacion

- [x] Captura a 390: Revision y resultado historico limpiados al cambiar organizacion.
- [ ] Rechazo API y aislamiento entre cuentas no acreditados por esta captura.

### M3-T1 §188 — Consulta con organizacion distinta

- [x] Captura a 390: mensaje no encontrado, sin datos historicos; GET 404 visible.
- [ ] Sesion de segunda cuenta y cobertura directa de API/RLS pendientes.

### M3-T1 §189 — Recuperacion tras rechazo por organizacion

- [x] Captura a 390: evento original recuperado y mensaje no encontrado ausente.
- [ ] Prueba directa API entre cuentas pendiente.

### M3-T1 §190 — Panel general adaptable

- [x] Cabecera movil apilada y textos Inventario/proceso/evaluacion aclarados; tipos/lint aprobados.
- [x] Captura posterior a 390 confirma cabecera apilada y textos actualizados legibles.
- [ ] Acciones de enlaces, medicion nueva de overflow y API entre cuentas pendientes.

### M3-T1 §191 — Redireccion segunda cuenta

- [x] Reporte y captura /dashboard: segunda cuenta no accede a consulta interna.
- [ ] Rechazo directo de API EIPD con segunda cuenta pendiente.

### M3-T1 §192 — Lectura RAT segunda cuenta

- [x] Captura segunda cuenta: tratamiento ajeno no encontrado, campos visibles vacios y GET RAT 404.
- [ ] Acceso directo API EIPD y cobertura integral RLS pendientes.

### M3-T1 §193 — GET historico EIPD segunda sesion

- [x] Network Console: GET historico v2 correcto retorna 404 y Evaluacion juridica no encontrada.
- [ ] Otros endpoints, escritura, reciprocidad y cobertura integral RLS pendientes.

### M3-T1 §194 — GET requisitos segunda sesion

- [x] Capturas readiness: GET 404 y Evaluacion juridica no encontrada, sin requisitos.
- [x] Intento previo 401 Token expirado distinguido del ensayo de acceso.
- [ ] Escritura, reciprocidad y cobertura integral RLS pendientes.

### M3-T1 §195 — Acceso original recuperado

- [x] Captura: readiness fetch 200, borrador/vinculo vigente y requisitos pendientes recuperados.
- [ ] Reciprocidad completa y otros endpoints pendientes.

### M3-T1 §196 — GET historico original 200

- [x] General/Response: GET v2 200, decision original y respuesta esquema 2.
- [ ] Escritura, reciprocidad y cobertura integral entre tenants pendientes.

### M3-T1 §197 — Regresion escritura aislada

- [x] 14 pruebas existentes de API negativa/writer v2 aprobadas en base aislada verificada.
- [ ] Suite completa y escritura manual entre cuentas no cubiertas por esta corrida.

### M3-T1 §198 — Permisos y confirmacion aislados

- [x] 45 pruebas existentes de permisos/reviews/readiness/confirmacion aprobadas en base aislada.
- [ ] Suite completa y escritura/reciprocidad manual entre cuentas pendientes.

### M3-T1 §199 — Concurrencia aislada

- [x] 26 pruebas existentes de concurrencia negativa/administrativa aprobadas en base aislada.
- [ ] Ensayo de usuarios reales concurrentes y suite completa no cubiertos por esta corrida.

### M3-T1 §200 — Balance de validacion

- [x] Evidencia reciente y limites consolidados en docs/project/m3-t1-balance-validacion.md.
- [ ] Inventario de fuentes oficiales/brechas de habilitacion excepcional; sin activar politica.

### M3-T1 §201 — Inventario fuentes EIPD

- [x] Fuente BCN/PDF art. 15 ter localizada; matriz contrato/brechas documentada.
- [ ] Instrumentos Agencia, revision por rutas y aceptacion pendientes; sin habilitacion.

### M3-T1 §202 — Contraste de rutas

- [x] Cadena normativa sensible/biometrica contrastada con frontera tecnica.
- [ ] Evidencias por ruta, instrumentos Agencia y aceptacion juridica pendientes.

### M3-T1 §203 — Evidencia por ruta

- [x] Lista revisable basada en contrato real, con resultados pendientes y limites.
- [ ] Ensayo de fixture dedicado admitido y aceptacion documental pendientes.

### M3-T1 §204 — Ensayo sintetico de frontera

- [x] 60 pruebas existentes de frontier HTTP/v2/requisitos aprobadas en base aislada.
- [x] Lista de evidencia enlaza grupos ensayados y distingue aceptacion pendiente.
- [ ] Trazabilidad por campo y aceptacion documental pendientes.

### M3-T1 §205 — Trazabilidad de campos

- [x] Campos de excepciones vinculados a pruebas especificas localizadas (revision estatica).
- [ ] Verificar/ampliar omisiones individuales en segundo sistema biometrico.
- [ ] Trazabilidad de documento/fuentes/politica y aceptacion pendientes.

### M3-T1 §206 — Omisiones segundo sistema

- [x] 15 casos nuevos; modulo biometrico 229 aprobadas en base aislada, Black/Ruff correctos.
- [ ] Respuestas no/pendiente, fundamento y evidencia parcial posteriores no cubiertos por nuevos casos.
- [ ] Aceptacion documental pendiente.

### M3-T1 §207 — Respuestas/evidencia segundo sistema

- [x] 14 casos nuevos; modulo 243 aprobadas en base aislada; formato/lint correctos.
- [ ] Combinaciones adicionales y aceptacion documental pendientes.

### M3-T1 §208 — Segunda fuente documental

- [x] Cinco casos nuevos; modulo 164 aprobadas en base aislada; formato/lint correctos.
- [ ] Variantes adicionales y trazabilidad de politica/aceptacion pendientes.

### M3-T1 §209 — Registros de aceptacion

- [x] Ocho casos nuevos; modulo de politica 112 aprobadas en base aislada; formato/lint correctos.
- [ ] Matriz detallada SourceRecordV1 y aceptacion real pendientes.

### M3-T1 §210 — SourceRecordV1

- [x] Matriz de campos y nueve casos nuevos; modulo politica 121 aprobadas en base aislada.
- [ ] Verificacion externa y aceptacion real pendientes.

### M3-T1 §211 — Regresion conjunta

- [x] 545 pruebas en una corrida focalizada aislada tras ampliaciones; 8.39 s.
- [ ] Expediente de revision de aceptacion y fuentes externas pendientes.

### M3-T1 §212 — Expediente revisable

- [x] Paquete de revision preparado con evidencia/limites y registro de decision pendiente.
- [ ] Designacion de revisor, verificacion externa y aceptacion autentica pendientes.

### M3-T1 §213 — Revision ficticia de desarrollo

- [x] Alcance ficticio hasta MVP incorporado; aceptacion real diferida.
- [x] Cuatro casos nuevos; modulo politica 125 aprobadas en base aislada; formato/lint correctos.
- [ ] Validacion con empresa/revisor reales posterior a MVP.

### M3-T1 §214 — Estado de politica en consulta

- [x] Proyeccion validada y vista sin autoridad; 13 cliente/8 interacciones/tipos/lint aprobados.
- [ ] Inspeccion manual con expediente ficticio pendiente.

### M3-T1 §215 — Politica visible validada

- [x] Captura a 480: fuentes/aceptacion pendientes, deshabilitada, aviso y readiness 200.
- [ ] Alternancia historica manual del bloque nuevo y otros estados reales pendientes.

### M3-T1 §216 — Politica/historia separadas

- [x] Captura a 390: evento historico, dos bloques actuales ausentes y /v2 fetch 200.
- [ ] Otros estados reales no cubiertos por esta captura.

### M3-T1 §217 — Estados simulados UI

- [x] Tres combinaciones de politica simuladas sin autoridad; 9 interacciones/tipos/lint aprobados.
- [ ] Sin politica operativa habilitada ni validacion real inferida de mocks.

- [x] M3-T1 §218: aviso visible de uso exclusivo de datos ficticios hasta MVP en consulta interna; conserva bloqueos operativos. No detecta datos reales automaticamente.

- [x] M3-T1 §219: enlace de inicio de sesion ante 401 en consulta EIPD; limpieza y recuperacion comprobadas con fixtures ficticios.

- [x] M3-T1 §220: compilacion de produccion frontend en copia temporal con configuracion ficticia; 23 pruebas cliente/interaccion aprobadas.
- [x] Validar runtime Node 22 para frontend (§221): 23 pruebas, tipos/lint y build aprobados; frontend/.nvmrc compartido con CI. Servidor activo sin reinicio.

- [x] M3-T1 §222: instalacion limpia Node 22 desde lockfile comprobada; CI usa npm ci y cache del lockfile. CI remoto aun no ejecutado para esta rama.
- [x] §223: Next/eslint-config-next 15.5.27 fijados y validados en copia aislada; 23 pruebas y build aprobados.
- [x] §224: instalacion/reinicio local aplicados: Next 15.5.27 con Node 22; login 200, admin sin sesion redirige /login, backend health 200.

- [x] M3-T1 §225: usuario comprueba visualmente requisitos y revision ficticia en Edge 390 x 749 tras actualizacion local Next; sin comprobacion nueva de status HTTP o login.

- [x] M3-T1 §226: ESLint CLI sustituye next lint y revisa tambien e2e/config/middleware; falso positivo callback fixture corregido sin desactivar reglas.

- [x] M3-T1 §227: aviso superior de pruebas ficticias hasta MVP y bloqueos visibles completo en captura Edge 390 x 749 del usuario.

- [x] M3-T1 §228: CI frontend incorpora 23 pruebas ficticias EIPD, comando verificado localmente con CI=true; ejecucion remota pendiente de PR.

- [x] M3-T1 §229: formato frontend global, lint, tipos y 23 pruebas EIPD aprobados localmente; artefactos Playwright excluidos de Prettier.

- [x] M3-T1 §230: 642 pruebas de las 26 suites del runner EIPD aprobadas en base aislada; verificacion posterior correcta. No suite integral del producto.

- [x] M3-T1 §231: Ruff/Black global backend aprobados; migracion historica preservada con excepcion I001 exacta; correcciones restantes solo formato/imports.

- [x] M3-T1 §232: PR #30 draft y CI remoto aprobado para 7f94bbf: 3977 pruebas backend y controles frontend con 23 pruebas ficticias. Sin merge/aceptacion juridica; revision tecnica pendiente.

- [x] M3-T1 §233: revision focal de permisos/tenant/canal admin y bloqueos de revisiones; sin hallazgo nuevo en alcance inspeccionado. Revision integral del PR pendiente.

- [x] M3-T1 §234: revision focal control global politica; docstring API actualizado y limite bloqueo servicio/SQL precisado. Sin nueva barrera SQL.

- [x] §235: CI agrupa por workflow/ref y prioriza ultimo commit en PR; cancelacion efectiva pendiente de observar tras publicar configuracion.


## Siguiente bloque funcional M3-T1 — §236

Representacion sensible: [diseño preliminar de desarrollo](project/m3-t1-representacion-desarrollo.md).
No habilitada; pruebas ficticias hasta MVP. Checklist historico no acredita facultad.

- [x] Delimitar campos candidatos y matriz documental conservadora (§236).
- [x] §237: contrato V1 separado y 39 pruebas ficticias de forma aprobadas; no persistencia, readiness o confirmacion.
- [ ] Diseñar binding sucesor, persistencia y diagnostico manteniendo historicos/bloqueos.
- [x] §238: binding independiente de representacion, 19 pruebas nuevas y 69 focalizadas aprobadas; can_confirm=false, sin integracion API.
- [x] §239: evaluador documental conservador, 30 pruebas nuevas y 88 relacionadas aprobadas; completo no autoriza ni verifica facultades.
- [ ] Representacion: integracion persistente/binding sucesor en API conservando bloqueos, historicos y limites de diagnostico.
- [x] §240: [plan persistente de representacion](project/m3-t1-representacion-persistencia.md), semantica PATCH/historicos/tenant y limite de cobertura EIPD; implementacion pendiente.
- [x] §241: centralizacion sin ciclo y contratos futuros Create/Update/Out, 107 pruebas relacionadas; endpoints activos sin nuevo campo. Persistencia pendiente.
- [x] §242: migracion/storage nullable de representacion, barrera SQL no confirmado y RLS probados; 116 relacionadas aprobadas, API del campo pendiente.
- [x] §243: CRUD de representacion conectado y gates conservadores; 127 pruebas del bloque aprobadas, readiness especifico pendiente (409 controlado).
- [x] §244: diagnostico representacion en readiness/interfaz, cobertura pendiente explicita y vigencia global suprimida; 132 backend y 31 frontend aprobadas. Sin habilitacion.

- [x] M3-T1 §260: CRUD de resolucion V3 y diagnostico V4 conectados en API; 892 pruebas aisladas y 37 frontend aprobadas; metadata2 no autoriza acciones. Migracion local aplicada sin cambios de contenido.
- [x] M3-T1 §§261–263: motivos V4 completos y lectura historica V3 de metadata1/2/null, sin inferir autoridad.
- [x] M3-T1 §§268–270: API/cliente/formulario de revisiones negativas V3 con identidad servidor, permisos, concurrencia y proteccion contra duplicados; confirmacion/activacion bloqueadas.
- [x] M3-T1 §§271–273: recorrido real Chromium/cliente/API/PostgreSQL ficticio y trabajo CI integrado aprobado en dbe1080; autenticacion sintetica, no login personal.
- [ ] M3-T1: delimitar siguiente ruta especial pendiente contra inventario §273 de [aceptacion](project/m3-t1-revision-aceptacion.md), diseno y fuentes; no retirar fallback sin evaluador y pruebas.
- [ ] M3-T1: validacion de sesion personal y revision tecnica integral antes de cierre; fuentes/aceptacion juridica pendientes. Pruebas ficticias hasta MVP.
