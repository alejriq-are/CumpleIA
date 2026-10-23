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

- [ ] Creación manual nueva con otra finalidad ficticia adecuada. La creación y persistencia del flujo se probaron en el entorno integrado aislado, no como nueva evaluación de la cuenta del usuario.
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
