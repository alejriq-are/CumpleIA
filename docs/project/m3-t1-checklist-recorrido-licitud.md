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

## 4. Pruebas o decisiones que siguen pendientes

- [ ] Coherencia del contenido del ensayo: Limitaciones del análisis conserva «sin anexos de respaldo adjuntos» pese a los anexos v1/v2 existentes. Revisar y actualizar ese texto mediante edición explícita; no confundir anexos ficticios adjuntos con controles verificados. No modificado durante la prueba de consulta.

- [ ] Creación manual nueva con otra finalidad ficticia adecuada. La creación y persistencia del flujo se probaron en el entorno integrado aislado, no como nueva evaluación de la cuenta del usuario.
- [ ] Verificación positiva de controles con implementación/evidencia ficticia y residual actual, si se incluye en el siguiente recorrido. La prueba negativa ya pasó; M1 del expediente sigue Propuesta.
- [ ] Persistencia de una consulta a autoridad guardada y conservación de sus datos al cambiar estado; el ensayo manual actual se limitó al formulario sin guardar.
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
