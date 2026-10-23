# Bases de Licitud — checklist operativo

Estado: **ajustes LIC-UX-005 a LIC-UX-012 implementados y validados localmente**.
Recorrido asistido y bloque de ajustes: 21–22/10/2026. Pendiente revisar las pantallas
actualizadas con el usuario. EIPD permanece bloqueada; solo datos ficticios.

## Punto para retomar

Abrir la evaluación existente de **CumpleIA Demo → [FICTICIA] Gestión de trabajadores**,
finalidad **[FICTICIA] Administrar antecedentes básicos de trabajadores adultos durante el ensayo**.
No intentar crear otro borrador para la misma finalidad.

- Evaluación: `2b117053-f5e6-4c9d-b5f6-c9557a8db5bf`, versión 1, borrador.
- Documento: `SIMULADA-EIPD-TRABAJADORES-001`, etiqueta **ENSAYO-2**, fecha **21/10/2026**.
- Valoración: **revisión 4**, asociada al documento actual al terminar el recorrido manual.
- R1: inherente **Media / Grave → Alto**; residual previsto **Baja / Grave → Medio**,
  fundamento conservado; residual actual **Sin evaluar**, sin fundamento de prueba.
- M1: dimensión **Probabilidad**, eficacia **Parcial**, verificación **Propuesta**.
- Anexo `SIMULADA-ANEXO-R1-M1-001`: versiones **1 y 2** guardadas y descargadas íntegramente.
- Consulta a autoridad: **Sin declarar**, antecedentes vacíos y plegados; prueba temporal descartada sin guardar.

**Próximo paso:** recargar y revisar los cambios visuales, sin volver a guardar por el
solo hecho de comprobarlos. Nueva ruta: Completar datos → Documentar EIPD →
**4. Valorar riesgos**. El acceso exterior duplicado fue retirado.

## 1. Recorrido manual ya comprobado

- [x] Abrir evaluación existente; rechazo de creación duplicada para la misma finalidad. No se creó una evaluación nueva en este recorrido manual.
- [x] Alcance RAT de trabajadores adultos; preparación de infancia oculta en adultos.
- [x] Editar fundamento, confirmación de guardado y persistencia tras recarga del texto añadido el 21/10.
- [x] Guardar EIPD incompleta; ENSAYO-2 y fecha persistentes. Diagnóstico conserva 25 pendientes; no equivale a fallo de guardado ni aprobación.
- [x] R1: horizonte 12 meses, daño/exposición/fundamentos y nivel inherente persistentes.
- [x] M1: Probabilidad / Parcial / Propuesta y fundamento persistentes, sin evidencias de verificación.
- [x] Residual previsto Medio guardado y persistente tras reinicio del equipo; actual sin evaluar.
- [x] Rechazo de residual actual reducido con M1 propuesta y sin evidencia: «El residual actual exige controles asociados verificados; usa residual previsto mientras falte verificación».
- [x] Cambios temporales de la prueba rechazada descartados; JSON posterior confirma residual actual con dimensiones null y fundamento vacío.
- [x] Evidencia totalmente vacía descartada al guardar sin exigir tipo. Evidencia parcial rechazada conservando referencia; al completar tipo, guardado y persistencia confirmados.
- [x] Evidencia guardada: referencia SIMULADA-FUENTE-PRUEBA-001 y tipo ficticio de revisión documental de fuentes.
- [x] Autoridad: inicial plegada, apertura automática al seleccionar En curso, textos conservados al cambiar a No solicitada. Ensayo sin guardar; recarga devuelve Sin declarar/vacío/plegado. No acredita persistencia de una consulta guardada.
- [x] Anexos v1/v2 conservados tras recarga, vínculos R1/M1 y descargas exactas byte a byte.
- [x] CSV y TXT de 2 MiB + 1 byte rechazados en cliente conservando formulario; hallazgo de aviso distante registrado y corregido en el bloque UX. No equivale a ensayo directo de esos rechazos contra la API.
- [x] Revisar documentos reúne RAT, licitud/LIA (Borrador, base Pendiente de definir y fundamento), EIPD y anexos.
- [x] Cambio guardado en EIPD vuelve histórica la revisión 3; actualización explícita crea revisión 4 asociada al documento actual.
- [x] Expediente JSON (3): ENSAYO-2/fecha, R1/M1, evidencia de fuentes, índice de cuatro revisiones y anexos v1/v2, sin archivos binarios. Hash global y hashes de los tres documentos recalculados correctamente; SHA-256 y tamaños de anexos coinciden con originales.
- [x] Exportación conserva activación deshabilitada y can_confirm/allows_real_data/authorizes_action/mvp_ready false.

Las omisiones observadas en la tabla eran de presentación: los fundamentos sí
aparecen en el expediente JSON. La tabla fue rediseñada en este bloque; no se
sobrescribieron documentos ni valoraciones del usuario para probarla.

Integridad de anexos comprobada:

| Archivo | Bytes | SHA-256 |
| --- | --- | --- |
| SIMULADA-ANEXO-R1-M1-001-v1.txt | 822 | d64013f17c1c754b10aea4415bf19d17793a47b0f6908a6f350a0f9faf735704 |
| SIMULADA-ANEXO-R1-M1-001-v2.txt | 1014 | c7b53587cfe25d4fb25f226548bb7ec26e09b153fa5b98d543f233ec609b446f |

## 2. Ajustes implementados

- [x] **LIC-UX-005:** cambios sin guardar inmediatamente antes de Guardar; conservación ante rechazo y retiro tras éxito.
- [x] **LIC-UX-006:** títulos/etiquetas/leyendas destacados, respuestas diferenciadas y casillas separadas de su texto con selección accesible.
- [x] **LIC-UX-007:** creación con confirmación visible; conflicto conocido explica que no se creó ni guardó otro borrador, ofrece acceso a borradores existentes y conserva formulario. No confunde conflicto con respuesta incierta.
- [x] **LIC-UX-008:** resumen comprensible, sin «contrato documental EIPD de infancia» en adultos; ayudas específicas de infancia según alcance.
- [x] **LIC-UX-009:** escala de lectura coherente, ayudas esenciales legibles, revisión en escritorio/móvil.
- [x] **LIC-UX-010:** valorar riesgos dentro de EIPD como paso 4; pasos 5 Medidas, 6 Fuentes y evidencias, 7 Riesgo residual y seguimiento. Estados/borradores conservados al navegar.
- [x] **LIC-UX-011:** descripción y daño en bloque propio; tabla por etapa con probabilidad/impacto/nivel/estado; controles en tabla separada con implementación y verificación distintas. Detalle de fundamentos, frecuencia/horizonte, seguimiento, evidencias y anexos; datos faltantes explícitos; controles múltiples y valoraciones históricas tratados sin inventar niveles vigentes.
- [x] **LIC-UX-012:** errores de formato, archivo vacío y tamaño diferenciados junto al selector; errores y avisos próximos a Guardar, con foco accesible y campos conservados.
- [x] Ayudas bajo Residual previsto y Residual actual verificado; diferencia entre previsión y controles implementados/comprobados.
- [x] Resumen residual: «Evaluación del riesgo residual actual pendiente» si no hay niveles evaluados; mayor nivel entre evaluados y aviso separado si quedan riesgos pendientes.
- [x] Guardado confirmado sigue visible cuando falla únicamente el diagnóstico posterior; no se presenta un fallo de lectura como fallo de escritura.

## 3. Validación del bloque

- [x] Revisión visual asistida de Base y fundamento: capturas del usuario confirman títulos/etiquetas destacados, ayudas legibles y aviso de cambios sin guardar inmediatamente entre Fundamento y Guardar (LIC-UX-005). Texto temporal [FICTICIA] Prueba visual del aviso añadido sin guardar; descartado mediante recarga: la captura posterior del fundamento guardado no contiene el texto temporal.


- [x] **34 pruebas Chromium** dirigidas a creación/edición, navegación, preservación de borradores, errores, roles, anexos y tablas.
- [x] **4 pruebas aisladas** de listado/recorrido; incluye Chromium con API y PostgreSQL temporal, JWT ficticio y comprobación de datos guardados y confirmed_at null.
- [x] Tipos, lint y formato de los archivos afectados.
- [x] Capturas ficticias revisadas en escritorio y móvil, sin desbordamiento de la página; tablas anchas con desplazamiento propio.
- [x] Capturas del usuario confirman valoración dentro de Documentar EIPD como paso 4 y tablas separadas de descripción, valoración y controles.
- [ ] Continuar confirmación visual asistida de los ajustes restantes.
- [x] CI d01b555 aprobada: corrección de las aserciones de expediente validada por GitHub Actions (39868291972); no equivale a validar cambios posteriores.

- [x] Presentación LIA ajustada: títulos generales «Base de licitud y fundamento»; LIA vigente solo con interés legítimo. LIA guardada con otra base permanece consultable como antecedente previo que no fundamenta la base actual; descarga conserva los datos originales. Ocho pruebas Chromium dirigidas, tipos y lint aprobados; CI del nuevo ajuste pendiente.

- [x] Revisión visual asistida de LIA: captura del usuario confirma título «Base de licitud y fundamento», consulta sin mención a LIA con base «Pendiente de definir» y fundamento guardado completo, sin el texto temporal del ensayo visual.

- [x] Capturas del usuario verifican fundamentos inherente y residual previsto de R1, residual actual sin fundamento registrado, evidencia SIMULADA-EVIDENCIA-R1-001 y anexos versiones 1 y 2 vinculados al control. Revisión 4 vigente, resumen de residual actual pendiente y ambas descargas visibles. Acción, responsable y fecha aparecen sin registrar, coherentes con los campos no completados del ensayo.

- [x] Validación visual de tamaño de anexo: al seleccionar TXT de prueba superior a 2 MiB aparece junto al selector «El archivo supera el tamaño máximo de 2 MiB. Selecciona un archivo más pequeño». Guardar visible deshabilitado; v1/v2 siguen en la lista. Formulario vacío y confirmación ficticia desmarcada: esta captura no acredita conservación de campos escritos ni bloqueo atribuible únicamente al tamaño.

- [x] Validación visual de formato: al sustituir el TXT sobredimensionado por el CSV de prueba, el aviso junto al selector cambia a «Formato no admitido. Selecciona un archivo PDF o TXT UTF-8». La captura muestra Guardar deshabilitado, confirmación desmarcada y campos vacíos; conservación de campos escritos pendiente de ensayo asistido.

- [x] Prueba visual de corrección de archivo: al sustituir CSV por TXT válido desaparece el aviso rojo y permanecen referencia SIMULADA-PRUEBA-CONSERVACION-001 y descripción ficticia; no se guardó el anexo.
- [x] Formulario de anexos aclarado: la sección clasifica qué parte del documento respalda el archivo; vínculos R/M opcionales en bloque desplegable separado, con códigos de ejemplo e indicación de que pueden quedar vacíos. Cambiar sección conserva vínculos. Once pruebas dirigidas aprobadas, tipos/lint/formato; comprobación de guardado ampliada confirma conservación de R1/M1 al cambiar sección y descarga intacta. Pendiente revisión visual del usuario.

- [x] Captura del usuario confirma ayuda de sección y desplegable de vínculos opcionales con etiquetas de códigos R1/M1. Anexos guardados ahora muestran el nombre completo de la sección y filas separadas para riesgos/medidas vinculados; nombres compartidos con el selector, sin modificar asociaciones guardadas. Prueba dirigida de guardado/descarga y nombres legibles aprobada; tipos, lint y formato correctos. Confirmación visual del usuario: v1 y v2 muestran «Sección relacionada: Fuentes y evidencias», «Riesgos vinculados: R1» y «Medidas vinculadas: M1» en líneas separadas; formulario de nuevo anexo vacío tras recarga.

- [x] Ensayo manual de anexo sin vínculos: captura muestra SIMULADA-ANEXO-BASE-001 versión 1, sección Base y fundamento y «Sin vínculos registrados» para riesgos y medidas. Se reutilizó el TXT ficticio v2; los dos anexos R1/M1 previos continúan visibles. Formulario posterior vacío. La captura no muestra el mensaje de éxito. El usuario confirma tras recarga la persistencia del nuevo anexo sin vínculos y de los tres registros con sus secciones y asociaciones.

- [x] Ensayo visual LIA sin guardar: tras selección temporal de Interés legítimo, captura confirma «LIA: análisis en borrador», nueve campos de análisis vacíos y aviso de cambios sin guardar junto a Guardar borrador. Captura posterior confirma LIA oculta con Consentimiento y fundamento conservado; pendiente descartar selección temporal mediante recarga; no se declaró persistencia ni se guardó LIA.

- [x] Originales ES - DESCARGABLE CONSENTIMIENTO.xlsx y ES - DESCARGABLE LIA.xlsx recibidos y revisados en lectura: cotejo de 19/31 preguntas y estados/conclusiones, con celdas y SHA-256. Actualizada auditoría LIC-FORM-001; implementación de formularios completos sigue pendiente.

- [x] Contrato LIC-FORM-001 registrado para desarrollo posterior: inventario completo de campos, referencia a 50 preguntas originales, estados/condicionales, evidencias, persistencia/compatibilidad, decisiones pendientes y pruebas de aceptación. [Implementación posterior](m3-t1-consentimiento-lia-implementacion.md). No se implementaron nuevos formularios en este bloque documental.

- [x] Prueba manual del 23/10: guardado EIPD confirma éxito y recarga conserva la consulta ficticia En curso y ambos textos. No equivale a una consulta real ni a revisión/aprobación jurídica; captura posterior confirma revisión 4 histórica y requiere reevaluación tras el cambio documental.

- [x] Cambio documental de consulta a autoridad: captura de Revisar documentos muestra «El documento cambió desde la revisión 4», revisión 4 histórica/requiere reevaluación y residual actual pendiente. Permanecen visibles los tres anexos.
- [x] Tras recarga y consulta sin editar desaparece «Guarda primero los cambios del documento» y permanece revisión 4 histórica/requiere reevaluación. La captura no reproduce un aviso de cambios pendientes tras descartar ediciones; no se confirmó defecto. Tres anexos conservados.

- [x] Nueva valoración tras cambio documental: captura confirma revisión 5 asociada al documento actual, sin aviso de revisión histórica; residual actual permanece pendiente y tres anexos conservados. Captura previa del editor muestra inherente Media/Grave/Alto, previsto Baja/Grave/Medio, actual sin evaluar y M1 Probabilidad/Parcial/Propuesta con fundamentos. No se ha visto el mensaje de guardado en esta secuencia; JSON posterior cotejado: revisión 5 vigente y asociación actual confirmadas, índice de revisiones 1–5 conservado.

- [x] Exportación posterior verificada: expediente-mvp-2b117053-f5e6-4c9d-b5f6-c9557a8db5bf (4).json, generado 23/10/2026 03:57:51 UTC (00:57:51 Chile). SHA-256 del archivo 7c09fef2bc1e49d3873a56c9ba8fbce6f93f867a1c00891b638cf8c6700c0db8. Recalculadas y coincidentes huellas del paquete y de RAT/licitud-LIA/EIPD. Revisión 5 current=true y huella igual a soporte actual; índice 1–5 presente. Consulta en_curso y SIMULADA-CONSULTA-001 conservadas; base legal null (Pendiente de definir), borrador y confirmed_at null. Tres anexos: R1/M1 v1-v2 en fuentes, Base v1 sin vínculos; tamaños y SHA-256 del índice coinciden con TXT ficticios conocidos (sin afirmar nueva descarga binaria). Inherente Alto, previsto Medio, residual sin resolver; M1 propuesta. allows_real_data/authorizes_action/can_confirm/mvp_ready false, activación deshabilitada.

- [x] Inicio de prueba positiva ficticia: creado TXT sintético SIMULADA-VERIFICACION-M1-001 (casos y resultados predefinidos, sin pruebas reales). Captura confirma guardado de anexo y descarga versión 1; vínculos visibles R1/M1, formulario reiniciado. Sección de tarjeta no visible en la captura. Pendiente declarar implementación documental M1 y aportar referencia en valoración antes de ensayar residual actual. No se ha acreditado verificación real.

- [x] Prueba positiva ficticia, preparación M1: capturas del editor muestran Medida implementada Sí, análisis/fundamento de implementación sintética y eficacia parcial simulada. Corregidos texto anterior de implementación pendiente y prefijo Referencia: del identificador. Captura final confirma Borrador EIPD guardado en servidor, evidencia tipo «[FICTICIA] Acta sintética de verificación.» y referencia exacta SIMULADA-VERIFICACION-M1-001. Diagnóstico 22 pendientes, EIPD bloqueada. No se ha guardado aún residual actual ni M1 verificada en valoración.

- [x] Prueba positiva ficticia, guardado de valoración: captura confirma éxito «Valoración guardada como nueva revisión», residual actual Baja/Grave → Medio con fundamento sintético, M1 Probabilidad/Parcial/Verificada y referencia SIMULADA-VERIFICACION-M1-001. Inherente Media/Grave/Alto y previsto Baja/Grave/Medio conservados. El ensayo usa resultados predefinidos; no hubo verificación real de controles ni activación EIPD. Número de nueva revisión y persistencia/consulta tras recarga aún pendientes.

- [x] Prueba positiva ficticia tras recarga: captura de Revisar documentos confirma revisión 6 asociada al documento actual y «Nivel más alto de riesgo residual actual entre los riesgos evaluados: Medio», sin aviso de evaluación residual pendiente; conserva exigencia de revisión humana. Anexos anteriores visibles; cuarto anexo sintético guardado en paso anterior. Pendiente JSON final para validar revisión 6, historial 1–6 y cuatro anexos/evidencias, sin afirmar verificación real.

- [x] Redacción del resumen residual ajustada por solicitud del usuario: «La valoración está guardada. Una persona responsable debe revisar sus fundamentos y evidencias antes de aprobarla.». Sustituye la frase ambigua sobre revisión humana; no cambia estados ni habilita una aprobación desde este resumen.

- [x] JSON final del ensayo positivo: expediente-mvp-2b117053-f5e6-4c9d-b5f6-c9557a8db5bf (5).json generado 23/10/2026 04:24:04 UTC (01:24:04 Chile), SHA-256 2704a288400568876c4fa8966c7901ed2bfbad7116db814184ca14a0f962b920. Coinciden huellas de paquete y tres documentos. Revisión 6 current=true con huella de soporte actual; índice 1–6 y los cinco registros previos idénticos al JSON (4). Tres anexos previos idénticos; cuarto SIMULADA-VERIFICACION-M1-001 v1 sección medidas vincula R1/M1; tamaños y hashes coinciden con cuatro archivos de ensayo conocidos (sin comprobar descarga binaria nueva). M1 Sí/Verificada/Probabilidad/Parcial con referencia exacta. Inherente Alto, previsto Medio, actual Medio, unresolved=false. Consulta ficticia En curso conservada y permisos/activación bloqueados.

- [x] Prueba negativa de dimensión: tras intentar reducir el impacto residual de Grave a Moderado con M1 Probabilidad/Parcial/Verificada, captura muestra rechazo «La reduccion residual exige un control eficaz sobre la dimension reducida», error enfocado y cambios pendientes conservados, sin confirmación de éxito. Captura posterior a recarga confirma residual actual Baja/Grave/Medio y fundamento sintético anterior conservados: la reducción de impacto y texto del intento rechazado no persistieron. Captura posterior del resumen confirma revisión 6 asociada al documento actual y residual Medio; prueba negativa cerrada sin cambio de revisión vigente.

- [x] Confirmación visual de la nueva redacción: resumen de revisión 6 muestra «La valoración está guardada. Una persona responsable debe revisar sus fundamentos y evidencias antes de aprobarla.».

- [x] Prueba negativa de evidencia: al vaciar solo las referencias de M1 manteniendo Probabilidad/Parcial/Verificada, captura confirma rechazo «Un control verificado exige implementacion declarada, evidencia registrada, dimension, eficacia y fundamento». Campo de referencia vacío y cambios pendientes conservados, sin confirmación de éxito. Captura posterior de Revisar documentos confirma revisión 6 asociada al documento actual y residual Medio: el intento rechazado no reemplazó la valoración vigente. El campo de referencia no aparece directamente en esta captura; la referencia guardada de revisión 6 fue comprobada previamente en JSON (5). El anexo no fue eliminado. Rechazo y conservación de revisión verificados.

## 4. Pruebas o decisiones que siguen pendientes

- [ ] **LIC-COH-001 (backlog):** coherencia de sección 7 tras ensayo positivo: el JSON (5) conserva resumen/fundamento manual de residual pendiente, residual_risk_level sin_resolver y plan de verificar M1, pese a valoración estructurada revisión 6 Medio y control sintético Verificada. Limitaciones además dice sin anexos, aunque hay cuatro. No es pérdida de persistencia; son campos documentales independientes no actualizados en el ensayo. Actualizar contenido explícitamente, distinguiendo verificación sintética de real; considerar ayuda/aviso de revisión de coherencia sin sobrescribir texto ni mapear silenciosamente escalas diferentes. Guardar el documento volverá histórica la valoración actual y requerirá reevaluación explícita.

- [ ] **LIC-FORM-001:** completar consentimiento/LIA en la interfaz. Auditoría confirma contratos y controles existentes en servidor, consentimiento sin formulario y LIA parcial (nueve textos). 190 pruebas existentes aprobadas; formularios completos aún pendientes. Ver [cobertura y aceptación](m3-t1-consentimiento-lia-cobertura.md). La prueba manual mantiene selección Consentimiento sin guardar; recargar para volver a Pendiente de definir.

- [ ] Coherencia del contenido del ensayo: Limitaciones del análisis conserva «sin anexos de respaldo adjuntos» pese a los anexos v1/v2 existentes. Revisar y actualizar ese texto mediante edición explícita; no confundir anexos ficticios adjuntos con controles verificados. No modificado durante la prueba de consulta.

- [x] Creación manual de otra evaluación ficticia en la cuenta del usuario: finalidad de coordinación de citas, tratamiento [FICTICIA] Gestión de clientes, versión 1 borrador. Alta y consulta del alcance observadas; fundamento inicialmente no ingresado (confirmado por el usuario), agregado después desde Base y fundamento y visible completo en Revisar documentos. Ver secuencia de capturas al final. No implica cobertura integral de exportación, historial ni aislamiento.
- [x] Exportación de prueba positiva ficticia verificada: JSON (5) confirma revisión 6 vigente, M1 Verificada, implementación Sí y evidencia sintética, residual Medio, historial 1–6 y cuatro anexos. Huellas y conservación aprobadas; EIPD/datos reales siguen bloqueados. La prueba negativa anterior ya pasó; no se acreditan controles reales. Queda aparte la coherencia del resumen manual de sección 7.
- [x] Persistencia de consulta ficticia a autoridad: confirmación de guardado y captura posterior a recarga con estado En curso, referencia SIMULADA-CONSULTA-001 y análisis «[FICTICIA] Ensayo de registro y persistencia. No corresponde a una consulta real.». Respuesta/recomendaciones/evidencias vacías, recomendaciones abordadas Sin declarar; diagnóstico conserva 24 pendientes y EIPD bloqueada.
- [x] Conservación de antecedentes guardados al cambiar estado: captura muestra No solicitada con análisis ficticio y SIMULADA-CONSULTA-001 intactos y visibles. Cambio temporal sin guardar; captura posterior de consulta tras recarga confirma descartado el estado local pendiente. En curso ya comprobado como estado persistido. Las capturas previas ya verificaron En curso persistido tras recarga.
- [ ] Recorrido ampliado de infancia con el bloque visual actualizado, si se prioriza. La visibilidad por alcance tiene pruebas dirigidas y antecedentes previos; no repetir automáticamente el recorrido completo.
- [ ] **LIC-RISK-001:** definir alcance de criterios configurables: solo descripciones/umbrales o también escalas, matriz y reglas. Congelar método/versión por valoración, sin recalificar históricos silenciosamente. No implementado en este bloque.
- [ ] **LIC-AUD-001:** diseñar bitácora de acciones exitosas/rechazadas, actor, fecha, resultado/motivo, correlación, integridad, aislamiento, permisos, retención y consulta/exportación; coordinar con Carpeta de Evidencia. Historial de revisiones existente no equivale a cobertura completa. No implementado en este bloque.
- [ ] Revisión/adopción formal EIPD general y RAT/LIA, razones estructuradas de cambio y revisión jurídica humana: contratos separados; LIC-UX-004 no está integralmente cerrado.

## 5. Límites y continuidad

Rama autorizada: **feature/m3-t1-licitud-persistencia**. Base del bloque:
**6bf7870**, con CI anterior aprobada (4518 backend, 2 omitidas; 211 frontend;
2 integradas). El commit del bloque y su CI se informan al publicar.

Solo datos ficticios. **Activación EIPD bloqueada. Sin merge ni despliegue.**
Las pruebas aisladas no modifican el expediente manual. Actualizar este documento
al obtener nueva evidencia; no duplicar historial ni repetir pruebas amplias sin causa.


### Referencia de evidencia inexistente — ensayo manual 23/10/2026

- Captura aportada por el usuario: `codex-clipboard-de6ee7bb-2402-4d98-9cdf-c45e61ee4281.png`. En M1 se reemplazó temporalmente la referencia por `SIMULADA-EVIDENCIA-INEXISTENTE-999`, manteniendo dimensión Probabilidad, eficacia Parcial y estado Verificada.
- Tras intentar guardar aparece el rechazo «Un control verificado exige implementacion declarada, evidencia registrada, dimension, eficacia y fundamento», junto con el aviso de cambios pendientes. La referencia inexistente permanece visible para corrección; no se observa confirmación de guardado. Resultado observado: rechazo correcto del intento con referencia no registrada.
- Cierre tras recarga: el usuario confirma «Punto 2, OK», referido a recuperar la referencia original `SIMULADA-VERIFICACION-M1-001`. La captura posterior `codex-clipboard-311a7570-ec7a-4804-9798-f4a7bb7b7cdb.png` muestra la revisión 6 asociada al documento actual y residual Medio. La recuperación del campo se acredita por confirmación del usuario; el número, vigencia y nivel se observan directamente en la captura. Prueba cerrada: el intento rechazado con referencia inexistente no sustituyó la valoración guardada.


### Descarga del anexo de verificación de M1 — ensayo manual 23/10/2026

- Archivo descargado aportado por el usuario: `C:/Users/aleja/Downloads/SIMULADA-VERIFICACION-M1-001 (1).txt`. Lectura y comparación efectuadas sin modificar el archivo. Tamaño: 1251 bytes; SHA-256 `d6756f8db2bac63eeb5ba2e02526d51592f8c110aba994ffbf5826f1d8114552`.
- Coincidencia con el original local `SIMULADA-VERIFICACION-M1-001.txt` y con tamaño/hash del índice `support.annexes` del expediente JSON (5). El registro corresponde a referencia SIMULADA-VERIFICACION-M1-001, versión 1, sección medidas, riesgo R1 y medida M1. El sufijo de descarga «(1)» no cambia su contenido ni su versión documental.
- Contenido inspeccionado: acta sintética expresamente ficticia, casos predefinidos de acceso permitido/denegado; mitigación parcial de probabilidad, impacto Grave y residual de ensayo Baja/Grave/Medio. Declara que no representa pruebas ejecutadas ni implementación real. Descarga e integridad verificadas para este archivo; no implica aceptación jurídica ni habilitación EIPD.


### Conservación de campos ante CSV no admitido — ensayo manual 23/10/2026

- Captura `codex-clipboard-ee6c75a3-6d31-4a54-abbd-0e9b10cb32a8.png`: referencia SIMULADA-CONSERVACION-002, descripción «[FICTICIA] Prueba de conservación de campos ante archivo no admitido.» y sección Base y fundamento permanecen completas tras seleccionar un CSV. Aparece «Formato no admitido. Selecciona un archivo PDF o TXT UTF-8» y aviso de anexo pendiente de guardar. Conservación de los tres campos verificada visualmente.
- Captura posterior al intento de guardar `codex-clipboard-da53ff0a-2f21-40b9-9acc-a91693ace94d.png`: aparece un segundo rechazo de formato junto a Guardar; referencia, descripción y sección permanecen intactas, con aviso de anexo pendiente y sin confirmación de éxito ni nueva tarjeta del anexo de prueba en la lista visible. Rechazo y conservación visual verificados; no se realizó inspección nueva de base de datos. El botón continúa habilitado y el mismo error se muestra junto al selector y junto al guardado: mejora de presentación registrada como LIC-UX-014. El usuario confirma después «OK, ejecutada recarga» para descartar el formulario temporal sin guardar; no se aportó captura nueva de la lista tras esa recarga.


### Nueva evaluación para una segunda finalidad de clientes — ensayo manual 23/10/2026

- Tratamiento [FICTICIA] Gestión de clientes, organización CumpleIA Demo. Antes del ensayo, la lista mostraba una evaluación versión 1 borrador para atender consultas y seguimiento comercial de clientes adultos, y el selector solo ofrecía esa finalidad (capturas 7892f4c2 y bd344f74).
- En RAT se añadió «[FICTICIA] Coordinar citas de atención solicitadas por clientes adultos durante el ensayo.». Captura e3a6128b: mensaje «Finalidades guardadas», ambas finalidades visibles y la original conserva la marca Principal. No se declaró persistencia tras recarga a partir de esa sola captura.
- Captura `codex-clipboard-8d0b5152-f735-4a5e-9af0-abb04a57bd3f.png`: nueva finalidad seleccionada en Bases de licitud, categorías Datos de contacto/Datos de identificación y titulares Clientes marcados; base Pendiente de definir. Mensaje «Borrador creado. Abre la evaluación para continuar.» y dos enlaces independientes en Evaluaciones guardadas, ambos versión 1 (borrador), para citas y para consultas/seguimiento. Creación manual con otra finalidad observada correctamente.
- Fundamento previsto del ensayo: «[FICTICIA] Prueba de creación de una evaluación independiente para coordinar citas de clientes adultos. Base de licitud pendiente de análisis.». El campo del formulario de creación aparece vacío tras éxito; esta captura no permite comprobar el fundamento persistido. Pendiente abrir/reabrir la evaluación de citas y verificar finalidad, alcance, fundamento, versión/estado. Tampoco se infiere de la lista que el contenido interno de la evaluación previa haya sido cotejado.


### Consulta inicial del nuevo borrador de citas

- Captura 5c267cbc y posteriores b2f3d98c, 83a7acf2 y bed12bd8: evaluación de citas versión 1 borrador, identificador visible 03739945-ebaf-43d0-956f-bd8b2af786b3, tratamiento d19cff6f-f107-4bc3-a727-9a3e7a6bcde3. La consulta del alcance RAT muestra finalidad de citas, titulares Clientes y categorías contacto/identificación; también fuentes, conservación y condiciones del RAT asociado. Estos antecedentes no acreditan que se haya completado la evaluación jurídica ni validado su aplicabilidad a la nueva finalidad.
- La vista indica explícitamente «No hay un documento EIPD guardado», «Sin valoración estructurada guardada» y «Sin anexos registrados». Ausencias observadas en esta consulta; no se trasladaron visualmente los registros R1/M1 y anexos del expediente de trabajadores. No se infiere una prueba integral de aislamiento por estas capturas.
- Observación de claridad pendiente: «Otro antecedente registrado» aparece para varios campos distintos, incluso regla de conservación y método de eliminación cuyos textos son visibles. Antes de ajustar etiquetas se debe mapear cada clave real a su significado y explicar procedencia del RAT, sin inferir respuestas nuevas ni convertir ausencia en No. El usuario consulta por datos que aparecen sin haberlos completado en la evaluación nueva.
- Pendiente desplegar «Consultar evaluación de licitud» para comprobar base y fundamento guardados; ese bloque permanece cerrado en las capturas aportadas.


### Consulta de base y fundamento del borrador de citas

- Captura `codex-clipboard-3e56cde7-84e2-4d1a-8772-70750c38b977.png`: finalidad de citas correcta, evaluación versión 1, estado Borrador, base Pendiente de definir y Fundamento «Sin información registrada». EIPD, valoración y anexos siguen ausentes en esta consulta.
- Discrepancia pendiente de aclarar: el guion de creación indicó un fundamento, pero no existe captura previa al envío que pruebe que se escribió. No declarar pérdida de persistencia ni prueba completa aprobada. Inspección puntual: LicitudWorkspace envía justification (o null si vacío); DossierDocumentView consulta value.justification y LegalAssessmentEditor carga out.justification. Esta coincidencia de campo no acredita el contenido de la solicitud concreta. Pendiente confirmar con el usuario si pegó el texto antes de Crear y consultar Base y fundamento sin editar antes de intentar corregir.


### Aclaración del fundamento vacío — borrador de citas

- El usuario confirma «no pegue fundamento». Capturas 224ded39 y 2aea1886: formulario de creación tras éxito y editor Base y fundamento muestran campo vacío; editor informa contenido cargado del servidor, base Pendiente de definir y versión 1 borrador. La consulta previa «Sin información registrada» es coherente con el dato no ingresado; no hay evidencia de pérdida de fundamento en este ensayo.
- Creación y reapertura del borrador sin fundamento verificadas visualmente. Sigue pendiente el ensayo de ingresar el texto en el editor, guardar y comprobarlo tras recarga/consulta. No se da por probada la persistencia de texto que no fue ingresado durante la creación.


### Fundamento guardado y consultado — cierre del bloque de creación de citas

- Captura bc3bcb78: editor Base y fundamento muestra completo el texto ficticio indicado para la finalidad de citas, manteniendo Pendiente de definir. No se atribuye por esa sola captura una recarga o un mensaje de éxito no visible.
- Captura `codex-clipboard-01ced902-0fb5-4315-9018-edcc9c45a856.png`: Revisar documentos → Consultar evaluación de licitud muestra finalidad correcta, versión 1, estado Borrador, base Pendiente de definir y fundamento íntegro: «[FICTICIA] Prueba de creación de una evaluación independiente para coordinar citas de clientes adultos. Base de licitud pendiente de análisis.». La vista identifica contenido guardado; prueba de guardado y consulta del fundamento cerrada visualmente. La captura no acredita por sí sola una nueva recarga ni exportación.
- Continúa el aviso de ausencia de documento EIPD guardado. No se completó evaluación jurídica ni se habilitó EIPD. El fundamento vacío anterior correspondía a omisión de ingreso, aclarada por el usuario; no se registró como fallo de persistencia.


### Exportación del expediente de citas — verificación 23/10/2026

- Archivo aportado `expediente-mvp-03739945-ebaf-43d0-956f-bd8b2af786b3.json`, generado 2026-10-23T14:00:46.237569Z (11:00:46 Chile). SHA-256 del archivo `a42b25eae3b6879d6ae41a8bddbeb0951c0ba6536e0d0f14eb987dd6963d6a7b`. Lectura sin modificar el original.
- 18 comprobaciones dirigidas aprobadas: identidad de evaluación/tratamiento/organización coherente entre bloques; versión 1 borrador; finalidad de citas exacta; categorías contacto/identificación y titulares Clientes; fundamento completo; base null (Pendiente de definir); snapshot RAT idéntico entre documentos RAT y licitud. El JSON confirma el identificador de tratamiento d19cff6f-f107-4bc3-a727-9a3e7a6bcde3 y corrige su transcripción anterior en este checklist.
- risk_evaluation null, risk_history y annexes vacíos; EIPD sin_documento con contenido/hash null; consentimiento y LIA null; sin confirmación. No contiene las referencias de R1/M1 y anexos del expediente de trabajadores comprobadas en el ensayo. Esta inspección valida este archivo, no sustituye una prueba integral de aislamiento multi-tenant.
- Huellas de ambos documentos con contenido y packet_hash recalculadas con JSON canónico sort_keys/UTF-8, coincidentes. packet_hash `e49068e1f3df57bca4124fc746fdc1f8e2d1441b97315bbf43fb143ccafcc6e5`. No se recalculó rat_context_hash ni document_hash de soporte, sujetos a sus contratos propios.
- mvp_ready, allows_real_data, authorizes_action y can_confirm false; activación deshabilitada en expediente y soporte. Reporte local de comprobaciones: outputs/expediente-citas-verificacion.json. Creación, posterior guardado/consulta del fundamento y exportación del nuevo borrador comprobados; no constituye evaluación jurídica completa.


### Inicio del recorrido ampliado de menores — 23/10/2026

- Capturas 83fd753b y 537fdf3e: selección del tratamiento [FICTICIA] Programa de fidelización con menores y apertura de su evaluación existente versión 1 borrador para participantes sintéticos de 10 a 13 años. No se crea otro borrador. Resumen visible con instrucciones generales; no se infiere diagnóstico específico de infancia por esa pantalla.
- Captura `codex-clipboard-85ae07e4-7058-4148-9299-c0ee65bbe292.png`: Completar datos → Alcance del RAT, solo lectura, muestra finalidad del programa de ensayo, titulares [FICTICIA] Participantes de 10 a 13 años, categoría Datos de identificación y fuente [FICTICIA] Registros sintéticos generados para el ensayo. No se obtienen datos de menores reales. Aviso explícito de contexto guardado que no se reemplaza automáticamente al editar RAT.
- Navegación condicional observada: aparecen «3. Infancia» y «Preparar resolución documental de infancia», además de base, EIPD y anexos. Prueba visual del alcance y disponibilidad del acceso de infancia aprobada; pendientes contenido del formulario, diagnóstico y demás pasos del recorrido. Sin edición ni guardado nuevos en esta secuencia.


### Consulta del formulario de infancia y diagnóstico inicial

- Capturas `codex-clipboard-34d652b6-4409-4a7d-8126-f7c1d48eb742.png` y `codex-clipboard-de1a94f7-5821-473d-876d-bde7d5d72e36.png`: documento de infancia cargado del servidor, expediente borrador. Niños y niñas marcado; adolescentes y adolescentes menores de 16 con datos sensibles desmarcados. Categoría Datos de identificación y grupo [FICTICIA] Participantes de 10 a 13 años seleccionados.
- Análisis de edad/alcance identifica participantes sintéticos, sin menores reales ni datos sensibles; interés superior, autonomía progresiva y autorización contienen análisis expresamente pendientes. Referencia de autorización vacía; notas conservan segunda edición del ensayo limitado a cinco participantes sintéticos. Datos sensibles de adolescentes menores de 16, ruta propuesta y otorgante declarado aparecen Sin declarar; no se modificaron ni se interpretaron como respuestas positivas.
- Requisitos EIPD de infancia: confirmación y activación bloqueadas, consulta incluye infancia y resoluciones anteriores no cubren este documento. Lista visible incluye base no implementada para confirmación, detección especial, screening y cuatro filas con idéntico texto «Revise el documento de infancia y su asociacion», además del bloqueo final. Observación de claridad: identificar motivos subyacentes antes de sustituir textos; no deduplicar razones distintas solo porque comparten una etiqueta genérica.
- Pendiente exportación del estado inicial para contrastar documento, asociaciones/históricos y motivos disponibles antes de cualquier edición nueva. Esta consulta no acredita autorización, suficiencia documental ni eficacia de controles reales.


### Exportación inicial de infancia — verificación 23/10/2026

- Archivo aportado `expediente-mvp-67fa99b7-45b9-4d8c-971e-a7dda20ac2b5 (2).json`, generado 2026-10-23T14:17:46.500965Z; SHA-256 `5f358b570162ac4a52c26ce5612d4a81f8e09e57155c4002f35b925fd4dff2e6`. Evaluación 67fa99b7-45b9-4d8c-971e-a7dda20ac2b5, tratamiento 970144d6-0874-4498-9230-729f8f7c02cb, organización CumpleIA Demo, versión 1 borrador.
- 22 comprobaciones dirigidas aprobadas: identidades coherentes, snapshots RAT iguales entre documentos/contexto, documento de infancia coincidente con el contexto de resolución, grupo ninos_ninas y categoría identificación no sensible, códigos de titulares coincidentes, autorización/ruta/otorgante/sensitive_under16 null y evidencia vacía. Notas coinciden con segunda edición limitada a cinco participantes sintéticos. Base null, sin confirmación; soporte sin valoración, historial de riesgos ni anexos.
- Exporta resolución de prueba versión 2, referencia SIMULADA-PILOTO-INFANCIA-RES-002, binding 4, creada 18/10/2026, con análisis/riesgos/medidas pendientes. Incluye un evento de esa resolución: requiere_cambios, material_status coincide, faculty_current false y authorizes_action/can_confirm false. Esto no prueba que las resoluciones anteriores cubran el documento actual ni que el otorgante tenga facultades vigentes. El archivo no representa el historial completo.
- Huellas de los tres contenidos documentales y paquete recalculadas y coincidentes; huellas internas de documento/contexto/material de resolución y documento de infancia verificadas usando el envoltorio domain/version/material definido en research_binding.digest, eipd_child_persistence y child_adolescent_binding. No comparar estas huellas internas con JSON plano. packet_hash `31448bfe373f55d687def965243ec5c5dc286eff28f8e04e33c8bf42d3344f19`. Reporte local outputs/expediente-infancia-inicial-verificacion.json.
- Bloqueos globales conservados: mvp_ready/allows_real_data/authorizes_action/can_confirm false y activación deshabilitada. El JSON no exporta los códigos de readiness que originan las cuatro filas genéricas observadas. Inspección de eipd_child.build_eipd_child_composition_v5 confirma que asigna el mismo mensaje a los issues de infancia, conservando field/code; no se identifican cuatro causas concretas solo a partir de este archivo. Pendiente revisar diagnóstico detallado antes de proponer mensajes específicos.


### Consulta separada de resoluciones y revisiones de infancia

- Capturas 636986a2 y 6070ee64: vista Preparar resolución documental de infancia muestra referencia/versión/notas vacías, declaración ficticia desmarcada y preparación para revisión deshabilitada. El historial se actualiza desde ese bloque, pero la lista no se presenta en modo prepare. Se corrigió la indicación de buscarla debajo: la consulta de resoluciones está en Revisar documentos.
- Captura 2bbd7a66: Revisar documentos → Resoluciones y revisiones de infancia lista Consultar resolución 1 y Consultar resolución 2. Avisos de consulta histórica, inmutabilidad y bloqueos visibles; sin valoración estructurada ni anexos.
- Captura `codex-clipboard-687b4163-256c-4737-bc35-ae739f742662.png`: resolución 1, referencia SIMULADA-PILOTO-INFANCIA-RES-001, versión PRUEBA-1, fecha 2026-10-17T22:57:19.627599Z, notas ficticias con análisis/riesgos/medidas/evidencias pendientes. Revisión documental propia «Requiere cambios», referencia SIMULADA-PILOTO-INFANCIA-REV-001, fecha 2026-10-17T23:10:23.749310Z. Formulario de revisión vacío y registro deshabilitado; se avisa que la observación no modifica original ni justifica otra versión.
- Captura `codex-clipboard-9674aab9-babe-438c-9acf-88cf2adf735e.png`: resolución 2, referencia SIMULADA-PILOTO-INFANCIA-RES-002, PRUEBA-2, fecha 2026-10-18T19:15:51.829681Z. Notas refieren documento de infancia actualizado y cinco participantes sintéticos. Revisión documental propia «No continuar», fecha 2026-10-18T19:19:47.599128Z; referencia visible con inicio «IMULADA-PILOTO-INFANCIA-REV-002.» (no se normaliza ni corrige un registro histórico a partir de la captura). Política m3-t1-infancia-pruebas-negativas-v1. Formulario vacío y registro deshabilitado.
- Separación de actuaciones: esta revisión documental «No continuar» no es el evento de organización «requiere_cambios» exportado con evidencia SIMULADA-PILOTO-INFANCIA-ACTA-002. Son canales distintos; no se registra una contradicción por sus resultados diferentes. Pendiente consultar en interfaz Decisión documental de organización, sin registrar nuevas decisiones ni conceder facultades.


### Canal de decisión de organización — consulta de resolución 2

- Captura `codex-clipboard-3f46b62f-672f-49cc-8c3e-30cf41fb6c36.png`: Tipo de actuación «Decisión documental de organización» abre Aceptación documental por organización. Explica que requiere persona facultada, corresponde a esa resolución y no confirma ni activa EIPD. Mantiene visible por separado el contenido RES-002/PRUEBA-2 y la revisión documental «No continuar».
- Historial documental de esta versión muestra «Requiere cambios», acta SIMULADA-PILOTO-INFANCIA-ACTA-002 y mensaje «Material coincide. Facultad actual no disponible», coherente con el evento y faculty_current false del JSON inicial. Coincidencia de material no equivale a autorización.
- Declaraciones ficticias sin marcar, campos de nueva decisión vacíos y botón de registro deshabilitado. No se registró nueva actuación. No se atribuye el estado deshabilitado exclusivamente a la facultad: la captura tiene otros requisitos incompletos. Historial de facultades del expediente aparece cerrado; pendiente desplegarlo para observar otorgamiento/revocación. No conceder ni revocar facultades durante esta consulta.


### Historial de facultades consultado — cierre de consulta histórica de infancia

- Captura `codex-clipboard-d5242cf6-e2ec-4c78-bfbd-27d6dd453c3d.png`: Historial de facultades del expediente desplegado muestra revisión 1 otorgar, rol responsable, con designación/prueba SIMULADA-PILOTO-DES-001 y SIMULADA-PILOTO-FAC-001; revisión 2 revocar, misma persona, referencia SIMULADA-PILOTO-REVOCACION-002. Textos explicitan prueba ficticia sin documento jurídico real ni valor jurídico.
- El evento de organización previo «Requiere cambios» permanece visible, con acta SIMULADA-PILOTO-INFANCIA-ACTA-002, material coincide y facultad actual no disponible. La revisión documental «No continuar» y el contenido RES-002/PRUEBA-2 continúan visibles por separado. Consulta de otorgamiento/revocación y conservación visual del evento histórico verificadas.
- No se otorgaron/revocaron facultades ni registraron nuevas decisiones en este recorrido. No se intentó una decisión nueva con todos sus campos completos, por lo que esta captura no demuestra por sí sola un rechazo nuevo del servidor ante facultad revocada. Sigue aparte la prueba de edición/guardado/reapertura de infancia con los ajustes actuales; este bloque cierra únicamente consulta de alcance, documento, exportación inicial, dos resoluciones, revisiones y facultades históricas.
