# LIC-FORM-001 — Contrato de desarrollo de consentimiento y LIA

Estado: pendiente de desarrollo. Registro solicitado por el usuario el 23/10/2026.
Base técnica comprobada: a236ccd, rama feature/m3-t1-licitud-persistencia.
Este documento define el trabajo posterior; no declara implementados los formularios,
no autoriza datos reales, activación EIPD, merge ni despliegue.

## 1. Objetivo y acuerdo

Completar la experiencia de Base y fundamento con un checklist de consentimiento
cuando se elija Consentimiento y una evaluación LIA completa cuando se elija Interés
legítimo. Adaptar las buenas prácticas de los originales al marco chileno; no copiar
el derecho europeo ni resolver licitud únicamente mediante casillas.

Documentos de referencia originales aportados por el usuario:
- ES - DESCARGABLE CONSENTIMIENTO.xlsx, hoja Checklist: 19 preguntas, A29 estado,
  A30 conclusión. SHA-256 f751ad4b0a0661038d93872f0683f09547dd3f83d3844150ea88f3f063eff3ad.
- ES - DESCARGABLE LIA.xlsx, hoja LIA: 31 preguntas, A40 estado, A41 conclusión.
  SHA-256 60ae2ad591af5e8d3e0d901b2e2346227ab3fa5ab58da96d43d9a086579afb85.

[Auditoría y mapeo de las 50 preguntas](m3-t1-consentimiento-lia-cobertura.md)
contiene la correspondencia celda/criterio/campo/adaptación. Es parte de este contrato.
[Diseño previo](modulo3-licitud-diseno.md), secciones 17 y 18, define contratos v1.
No modificar los originales ni incorporar su publicidad/contactos al producto.

## 2. Situación inicial verificada

| Área | Existe | Falta |
| --- | --- | --- |
| Consentimiento | ConsentAssessmentV1, CREATE/PATCH/GET, evaluador de preparación y aplicabilidad | Editor, tipado de cliente, consulta legible completa y diagnóstico por control |
| LIA | LiaAssessmentV1, ocho grupos, evaluador/RAT, persistencia y nueve textos editables | Resto de campos/respuestas/condicionales, consulta y diagnóstico completos |
| Evidencia | Metadatos de consentimiento; anexos versionados por sección | Asociación explícita punto evaluado ↔ evidencia/anexo y su versión |
| Guardado | Borradores parciales y conservación del campo omitido en PATCH | Cubrir nuevos campos sin pérdidas, especialmente al cambiar de base |

Las 190 pruebas de servicios/esquema ejecutadas durante la auditoría pasaron.
Eso no demuestra la existencia de las pantallas pendientes ni certifica cumplimiento.
No volver a declarar la brecha resuelta por la mera existencia de modelos o tablas.

## 3. Alcance de producto

### 3.1 Navegación y estados

Mantener Completar datos → 2. Base y fundamento. Título general Base de licitud y
fundamento. Dentro del editor, base/fundamento comunes y formulario condicional:
- consentimiento_art12 → Evaluación del consentimiento.
- interes_legitimo_art13d → Evaluación del interés legítimo (LIA).
- Pendiente u otra base → sin formulario activo de consentimiento/LIA; antecedentes
  guardados siguen disponibles en consulta, identificados como previos.

No activar ambos evaluadores por defecto. En bases distintas puede haber requisitos
especiales propios ya implementados; no sustituirlos ni eliminarlos en este bloque.
La organización y finalidad RAT, evaluación/versión y rol deben permanecer identificables.

Distinguir: sin iniciar, borrador guardado, cambios sin guardar, diagnóstico documental
incompleto/requiere revisión/completo. Completo documental no significa válido o aprobado.
Mostrar confirmación de guardado junto a la acción, error con foco y campos conservados,
y advertencia de diagnóstico no actualizado cuando falle una lectura posterior al guardado.

### 3.2 Consentimiento: campos existentes obligatorios en la cobertura de UI

Encabezado: given_by (Titular / Representante legal / Mandatario), grant_method
(Escrito / Verbal / Electrónico / Acto afirmativo / Otro documentado), notas.
No preseleccionar otorgante ni mecanismo favorable cuando no existen datos guardados.

Cada pregunta tiene identificador estable, etiqueta/ayuda chilena, respuesta,
comentario y acceso a evidencia. Respuestas: Sí, No, Pendiente; No aplica únicamente
cuando la aplicabilidad lo permita. Campo no respondido se mantiene pendiente, nunca Sí.

| ID existente | Contenido a presentar |
| --- | --- |
| consentimiento_libre | Voluntariedad real, sin coacción; desgloses del original A4:A9 |
| consentimiento_informado | Información comprensible, responsable/finalidad/datos/aviso y revocación |
| consentimiento_especifico_finalidad | Finalidad concreta y elección granular |
| consentimiento_previo | Obtención previa al tratamiento |
| voluntad_inequivoca | Manifestación inequívoca, no silencio |
| accion_afirmativa_clara | Acto afirmativo, sin aceptación premarcada ni por inacción |
| revocacion_posible | Posibilidad real de revocar |
| revocacion_medio_equivalente | Medio similar o equivalente al de obtención |
| revocacion_expedita | Procedimiento expedito |
| revocacion_fidedigna | Mecanismo fidedigno |
| revocacion_gratuita | Gratuidad |
| revocacion_disponible_permanentemente | Disponibilidad permanente |
| responsable_puede_acreditar | Respaldo de obtención del consentimiento |
| contexto_contrato_servicio | Identificar si se solicita en contexto contractual/de servicio |
| mandatario_facultad_expresa | Facultad expresa del mandatario; condicional |
| tratamiento_necesario_contrato_servicio | Necesidad del tratamiento en ese contexto; condicional |

Aplicabilidad se obtiene del servidor: las últimas dos preguntas dependen de otorgante
y contexto contractual. No marcar No como resultado desfavorable para una pregunta
que solo identifica contexto. Revisar derechos/obligaciones y reglas especiales cuando
actúe representante o mandatario; este formulario no acredita automáticamente facultades.

Agrupación sugerida: obtención y contexto, libertad/finalidad, información/acción,
revocación, evidencia, conclusión. Mantener ayudas breves y detalle expandible.
Los 19 criterios fuente deben conservarse identificables, incluso si se agrupan.

### 3.3 LIA: cobertura completa del contrato existente

| Grupo de LiaAssessmentV1 | Campos que deben poder editarse/consultarse |
| --- | --- |
| purpose_and_interest | purpose_description, legitimate_interest, interest_holder, controller_benefit, third_party_benefit, public_benefit, interest_importance, consequences_without_processing, relevant_rules, ethical_considerations |
| necessity | contributes_to_purpose, linked_to_interest, achievable_without_personal_data, less_intrusive_alternative, fewer_data_possible, categories_necessary_and_relevant, necessity_analysis, proportionality_analysis, alternatives_analysis, minimization_analysis |
| nature_and_scope | exclusively_professional_context, volume_and_scope, special_rules_description, additional_risk_factors |
| reasonable_expectations | prior_relationship, relationship_description, significant_change_of_use, informed_at_direct_collection, third_party_information, technology_or_context_changes, foreseeable_purpose_and_method, innovative_processing, expectations_evidence, expectations_analysis |
| impact | negative_effects, severity, likelihood, loss_of_control, intrusion_analysis, reasonable_opposition_likelihood, rights_and_freedoms_analysis, vulnerable_people_impact, transparently_explainable, relevant_unmitigated_impacts, impact_analysis |
| safeguards | measures (lista de medidas): description + mitigated_impact; safeguards_analysis |
| transparency_and_opposition | information_method, interest_communication, opposition_channel, opposition_procedure, responsible_area |
| conclusion | balancing_summary, identified_interest, necessity_and_proportionality_result, main_impacts, relevant_safeguards, rights_protection_reasoning, decision |

Respuestas estructuradas LiaResponseV1: answer + comment, conservando valores
si/no/no_aplica/pendiente y aplicabilidad del evaluador. No convertir estos objetos
en simples textos. interest_holder conserva responsable/tercero/ambos. decision
conserva puede_basarse/no_puede_basarse/requiere_revision; presentarla como conclusión
aportada que requiere fundamento, distinta de la aprobación jurídica del documento.

Condiciones a reflejar desde el evaluador existente:
- Beneficios del responsable/tercero según titular del interés.
- Relación previa → descripción cuando corresponda.
- Origen directo/tercero del RAT → deber informativo correspondiente.
- Regímenes especiales y grupos vulnerables → análisis específicos.
- Medidas de salvaguarda y descripción de impacto mitigado según disparadores existentes.
- Finalidad LIA distinta de RAT → requiere revisión, sin sobrescribir silenciosamente.
- RAT incompleto o aplicabilidad no resuelta → mostrar pendiente y motivo.

severity/likelihood de LIA usan el contrato existente baja/media/alta/pendiente.
No equipararlos a la matriz EIPD de cuatro niveles ni recalcular históricos. Si
se quiere unificar metodologías, diseñarlo aparte con LIC-RISK-001.

### 3.4 Evidencias y anexos

Conservar ConsentEvidenceV1: evidence_type, reference, obtained_on, mechanism,
notes. La fecha debe ser fecha, no texto ambiguo. Distinguir referencia documental
sin archivo de archivo adjunto y de evidencia revisada. No inventar un estado de
verificación real a partir de la carga o de marcar una casilla.

Requisito pendiente de diseño físico: asociar evidencia a la evaluación, criterio
estable y, cuando exista archivo, al anexo exacto/reference + versión + hash.
Un mismo archivo puede respaldar varios criterios; una referencia ambigua no debe
seleccionar por defecto la última versión. Reutilizar anexos de sección Base y
fundamento sin exigir vínculos R1/M1. No reutilizar esos campos como IDs de preguntas.

La evidencia enlazada debe respetar permisos y organización en consulta/descarga;
no exponer otra organización ni insertar contenido personal en logs. No añadir
servicio/almacenamiento externo. Archivos no se ejecutan ni se consideran instrucciones.

### 3.5 Consulta y diagnóstico

Revisar documentos debe mostrar todo lo guardado: respuestas, comentarios,
evidencias, anexos/versión, condiciones, conclusión y pendientes. Tablas con columnas
Criterio / Respuesta / Fundamento / Respaldo; agrupar LIA por sus ocho secciones.
No sustituir valores faltantes por positivos; indicar Sin registrar/Pendiente.
Conservar detalle técnico/exportación íntegra, sin poner JSON como vista principal.

Consumir los resultados de preparación existentes (issues/applicability) y traducir
sus códigos a mensajes en español con enlace al campo. Guardado y diagnóstico son
operaciones distintas: no presentar un fallo de lectura como fallo de escritura.
Un diagnóstico sobre datos guardados debe identificarse como tal si hay cambios
locales sin guardar. No presentarlo como evaluación del borrador local actualizado.

## 4. Persistencia, compatibilidad y versiones

1. Tipar consent_assessment en el cliente de licitud y completar tipos LIA. Reutilizar
   CREATE/PATCH/GET actuales; verificar el contrato real antes de añadir endpoints.
2. Guardar legal_basis, justification y evaluación activa de forma coherente, sin
   borrar evaluaciones de bases anteriores. Campo omitido en PATCH significa conservar.
   No enviar null para ocultar un bloque ni un objeto vacío que reemplace datos.
3. El PATCH reemplaza material aportado según contrato: componer desde el documento
   cargado y preservar campos no editados; no asumir deep merge del servidor.
4. Cambiar de base en memoria conserva las ediciones de ambos formularios durante
   navegación interna. La recarga no se promete como recuperación de cambios sin guardar.
   Definir guardado de formulario inactivo explícitamente; no persistirlo en secreto.
5. No generar una nueva versión histórica formal por simple visualización. Mantener
   las reglas actuales de borrador/confirmado/reemplazado; no editar confirmados.
6. Datos nuevos de desglose/evidencia deben tener contrato de almacenamiento/versionado
   y pruebas de roundtrip antes de mostrar controles como completados. Nunca agregar
   claves que Pydantic descarte o rechace sin una decisión consciente del esquema.
7. No reinterpretar el Sí histórico de una pregunta agrupada como Sí de todos los
   desgloses nuevos. Su estado inicial será pendiente de documentar donde falten datos.
8. Cambios de RAT/base/material pueden afectar fingerprints y diagnósticos de documentos
   relacionados: probar invalidación existente y no reparar hashes/históricos en silencio.
9. Si se necesitan nuevas tablas, deben incorporar organización/RLS y migraciones
   append-only; no modificar migraciones aplicadas. No asumir que una columna JSONB
   elimina la necesidad de versionar su contrato semántico.

## 5. Decisiones por resolver antes de programar extensiones

| Decisión | Requisito fijo | Pendiente técnico/producto |
| --- | --- | --- |
| Desglose de las 19 prácticas de consentimiento | Cada criterio debe quedar rastreable y persistido | Extensión compatible versionada o contrato sucesor; mapear IDs antiguos/nuevos y reglas de diagnóstico |
| Evidencia por criterio LIA/consentimiento | Referencia inequívoca de archivo/versión cuando exista | Formato validado y ubicación; no suponer campos ya disponibles |
| Estado de práctica recomendada | Separar recomendación de obligación | Redacción y efecto en diagnóstico de revisión periódica/marketing |
| Conclusión y revisión | Guardado/completitud no aprueban jurídicamente | Encaje con futura revisión formal de RAT/LIA; no reutilizar una decisión EIPD como aprobación general |
| Criterios jurídicos | Cada afirmación con fuente chilena, versión/vigencia y fundamento | Revisión humana de redacción y preguntas adaptadas; responsables concretos por designar |
| Cambios concurrentes | Evitar pérdida de modificaciones | Revisar mecanismo actual y resolver conflicto/recarga explícitos antes de prometer protección nueva |

Estas decisiones no son requisitos opcionales ni una aprobación pendiente para
crear la documentación. Impiden inventar silenciosamente una extensión de datos;
resolverlas al inicio del desarrollo y dejar sus decisiones en este contrato/ADR.

## 6. Adaptación chilena que debe preservarse

Usar la matriz del informe de cobertura como inventario obligatorio. Separar
exigencias legales, recomendaciones de buena práctica y controles internos de
producto. Cada pregunta tendrá fuente/celda original, ID estable, regla chilena
contrastada, régimen/vigencia, ayuda, aplicabilidad, dato guardado y prueba asociada.
Revalidar fuentes vigentes al implementar, sin congelar como actual una norma futura.

Puntos críticos ya detectados:
- A24 consentimiento: no borrar universalmente todos los datos por revocación;
  documentar efectos, otras bases válidas y excepciones/deberes de conservación.
- A20: distinguir manifestación inequívoca ordinaria de consentimiento expreso en
  supuestos especiales; no extrapolar todas las categorías europeas.
- A27: revisión periódica es recomendación de la plantilla, no caducidad universal.
- A9: analizar voluntariedad con desequilibrio de poder; especialmente trabajadores.
- A23: reglas de marketing según contexto chileno; no afirmar obligación específica
  sin contrastar la normativa sectorial/de consumo correspondiente.
- LIA A18/A20: proteger categorías especiales/infancia conforme al régimen chileno;
  LIA general no autoriza por sí sola esos tratamientos.
- LIA A37: capacidad de explicar/informar, no voluntad subjetiva de hacerlo.

## 7. Secuencia de desarrollo propuesta

| Paquete | Entrega concreta | Condición de salida |
| --- | --- | --- |
| FORM-01 | Modelo de pantallas y decisiones de esquema para desgloses/evidencias; mapeo normativo de 50 preguntas | Ningún campo visible sin destino validado de persistencia; diferencias legales identificadas |
| FORM-02 | Editor de consentimiento, cliente tipado y preservación | Formularios incompletos guardan/reabren; condicionales y errores comprobados |
| FORM-03 | Editor LIA completo y condiciones RAT | Todos los campos existentes accesibles; pendientes/condiciones correctos |
| FORM-04 | Evidencias por criterio, consulta completa y diagnóstico enlazado | Archivo/versión identificables y vista coherente con material guardado |
| FORM-05 | Integración real aislada, regresiones, recorrido asistido y documentación | Criterios de aceptación aprobados y límites comunicados |

La secuencia es propuesta de ejecución, no cinco implementaciones ya iniciadas.
No duplicar evaluadores del servidor en el cliente ni ampliar las reglas jurídicas
sin contrato y revisión. Mantener commits coherentes por capacidad validada.

## 8. Pruebas de aceptación necesarias

| Caso | Resultado verificable |
| --- | --- |
| Base pendiente/otra base | Formularios inactivos; antecedentes anteriores consultables con identificación |
| Selección consentimiento/interés legítimo | Solo formulario activo correspondiente; no se pierde fundamento |
| Otorgante/método vacíos y preguntas pendientes | Borrador guardable, preparación incompleta sin falsos positivos |
| Mandatario/contexto contrato | Aplicabilidad exacta; No aplica permitido solo cuando corresponde |
| Sí histórico agrupado | No llena automáticamente desgloses nuevos |
| Respuestas desfavorables | Motivos de revisión visibles, sin aprobar automáticamente por número de Sí |
| LIA relación/origen/vulnerabilidad/salvaguardas | Condiciones conservan datos y señalan pendientes correctamente |
| Finalidad LIA diferente del RAT | Requiere revisión; sin normalización que borre la diferencia |
| Guardar/recargar/cambiar pestaña/base | Respuestas, comentarios, grupos y evidencia persistidos sin pérdida |
| Error 403/422/conflicto/red incierta | No falso éxito; conserva ediciones; verifica estado antes de reintentar cuando sea incierto |
| Guardado exitoso y diagnóstico fallido | Confirmación de escritura y aviso de diagnóstico independiente |
| Evidencia solo referencia / archivo v1-v2 | Tipos distinguibles; cada vínculo apunta a su versión, sin cambiar al subir otra |
| Anexo sin riesgos/medidas | Puede respaldar Base y fundamento con vínculo al criterio; R/M opcionales |
| Consulta/exportación | Material íntegro, estados de la base activa y antecedentes claramente diferenciados |
| Lector/escritor y organización distinta | Guardas servidor y RLS; descarga y consulta sin cruce entre organizaciones |
| Cambio RAT/material | Diagnóstico y vínculos/contextos vigentes según reglas; historial no reescrito |
| Móvil/escritorio/accesibilidad | Etiquetas, ayudas, tablas desplazables, foco de error y avisos junto a Guardar legibles |
| EIPD, confirmación y datos reales | Ninguno se habilita por completar checklist o LIA |

Ejecutar tests relevantes de schema/servicios/API, tipos/lint/formato frontend,
Chromium dirigido y recorrido con API/PostgreSQL aislado para escrituras/roles.
Reutilizar fixtures ficticios. Las 190 pruebas de auditoría son base de regresión,
no sustituyen la cobertura nueva. Vincular evidencia al commit exacto/CI comprobada.

## 9. Archivos de integración previstos

Confirmados para inspección/modificación al retomar:
- frontend/components/licitud/LegalAssessmentEditor.tsx
- frontend/lib/api/licitud.ts
- frontend/lib/licitud/lia-fields.ts
- frontend/components/licitud/DossierDocumentView.tsx
- frontend/components/licitud/AssessmentFlow.tsx
- frontend/components/licitud/AssessmentSupportPanel.tsx (solo integración de respaldo si corresponde)
- backend/app/schemas/licitud.py
- backend/app/services/consentimiento.py
- backend/app/services/lia.py
- backend/app/services/licitud.py
- frontend/e2e/licitud-workspace.spec.ts, mvp-dossier.spec.ts, assessment-support.spec.ts
- backend/tests/test_services_consentimiento.py, test_services_lia.py, test_schemas_lia.py

Crear componentes de formulario separados si mejora legibilidad, conservando
el coordinador de guardado y los borradores. Identificar rutas/tests/migraciones
adicionales al resolver el esquema; la lista no autoriza ediciones sin relación.

## 10. Retoma y cierre

Leer este contrato, auditoría de cobertura, AGENTS.md y HANDOFF; verificar rama,
HEAD, estado y contrato real antes de tocar código. Las rutas originales están en
el documento de cobertura y el chat; comprobar archivos/hashes si se vuelven a leer.
No necesitar los Excel para redescubrir preguntas: las 50 ya están mapeadas.

Último estado observado del expediente manual: evaluación de trabajadores versión 1;
base persistida Pendiente de definir. El usuario seleccionó Consentimiento
solo en memoria para una prueba, sin guardar; descartar mediante recarga antes de
retomar pruebas sobre el expediente. No usarlo para respuestas positivas ficticias.
Tres anexos guardados: R1/M1 versiones 1 y 2, y SIMULADA-ANEXO-BASE-001 versión 1
sin vínculos. Control M1 sigue propuesta y residual actual pendiente.

Cierre futuro exige: implementación y pruebas anteriores, recorrido asistido,
consulta/exportación completas, documentación/backlog actualizados y revisión
jurídica de la adaptación. Registrar pendientes reales sin equipararlos a aprobación.
LIC-AUD-001 y LIC-RISK-001 conservan su alcance independiente.
