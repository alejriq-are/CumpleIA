# M3-T1 — Representacion sensible: siguiente bloque de desarrollo

Estado: DISEÑO PRELIMINAR, sin contrato implementado ni ruta habilitada.
Fecha: 2026-10-14. Pruebas exclusivamente ficticias hasta MVP.

## Problema y objetivo

El consentimiento ordinario ya distingue titular, representante_legal y mandatario
(ConsentAssessmentV1.given_by), pero el alcance sensible no acredita automaticamente
la facultad del tercero. Una declaracion o checklist completo no demuestra el
vinculo, alcance o vigencia de esa facultad. Se necesita un expediente separado y
versionado para registrar esos datos y diagnosticar faltantes sin autorizar acciones.

Este documento define requisitos del producto, no una conclusion juridica sobre
quien puede consentir. Analisis de fuentes/aplicabilidad debe preceder cualquier
futura habilitacion; no se inventan facultades por parentesco, rol o referencia.

## Primer alcance propuesto

- Representante legal o mandatario en expediente sensible por consentimiento.
- Cobertura conservadora de todo el alcance seleccionado del RAT, como hoy.
- Datos, referencias y personas de prueba ficticios; no nombres/RUT/documentos reales.
- Mantener separadas las evaluaciones de salud, biometria e investigacion.
- Infancia/adolescencia, capacidad no resuelta, facultad discutida o cobertura parcial
  siguen pendientes de su diseño propio; no se resuelven por este expediente.
- No modificar las rutas de excepcion sin consentimiento ni la politica EIPD.

## Campos candidatos del contrato documental V1

| Campo | Funcion y limite |
| --- | --- |
| schema_version | Literal 1, contrato cerrado, sin campos extra |
| representation_kind | representante_legal o mandatario; no deriva autoridad |
| representative_reference | Referencia documental ficticia, no UUID del usuario autenticado |
| represented_subjects_reference | Identifica documentalmente los titulares cubiertos |
| authority_document_reference / authority_document_version | Identidad del documento aportado; sin validar autenticidad externamente |
| authority_basis_description | Fundamento declarado de la representacion; no enum juridico inventado |
| express_authority_analysis | Analisis aportado del alcance de la facultad para el consentimiento sensible |
| scope | Finalidad, categorias y grupos del alcance seleccionado; no ampliacion implicita |
| scope_match_analysis | Explica correspondencia del documento con ese alcance |
| issued_on / valid_from / valid_until | Fechas documentadas opcionales, sin caducidad creada por el producto |
| validity_analysis | Explica vigencia/limitaciones; ausencia de fecha no equivale a vigencia indefinida |
| limitations / revocation_information | Restricciones, revocacion o incertidumbre declaradas |
| evidence | Referencias/versiones/descripcion, reutilizar contrato de evidencia existente tras verificar compatibilidad |
| notes | Observaciones, no sustituyen campos de evaluacion |

No proposed ready/can_confirm/accepted_by/hash editable. Identidad persistida, actor,
fecha y binding son datos de servidor. Un borrador puede estar incompleto; schema
valida forma, evaluador decide motivos documentales. No usar texto libre del cliente
como decision autorizante ni copiar datos del perfil a la persona representada.

## Matriz de comportamiento a implementar

| Caso ficticio | Resultado previsto |
| --- | --- |
| titular sin representacion | Mantener comportamiento actual; no exigir este bloque |
| representante/mandatario sin expediente | Motivo de acreditacion pendiente |
| clase distinta de given_by | Incoherencia, no completar diagnostico |
| referencia vacia o evidencia ausente | Motivos documentales diferenciados |
| facultad o vinculo no documentados | Revision pendiente, no inferencia |
| revocacion/limitacion incompatible declaradas | Motivo explicito, no preparacion positiva |
| fechas contradictorias o vigencia no resuelta | Error de contrato o motivo segun campo; sin plazo legal inventado |
| alcance distinto o cambio RAT/finalidad | Binding desactualizado, reaporte explicito |
| documentacion completa ficticia | Solo diagnostico documental; confirmacion sigue bloqueada en esta primera etapa |
| salud/biometria/EIPD concurrentes | Conservar todos los requisitos/bloqueos propios |
| lectura historica | Mantener identidad guardada, sin reconstruir nueva acreditacion |
| usuario de otra organizacion | Permisos/RLS y filtros de padre, sin exposicion de datos |

## Secuencia de implementacion

1. Revisar campos contra schemas existentes, fijar contrato V1 y casos de forma.
2. Implementar schema y pruebas puras ficticias, sin persistencia ni habilitacion.
3. Diseñar binding sucesor separado: no reescribir hashes/contextos historicos.
4. Incorporar persistencia/API con migracion nueva si corresponde, permisos/RLS.
5. Evaluador puro con motivos estructurados, integracion readiness y obsolescencia.
6. Ensayo aislado de aislamiento, reaporte, coexistencia y concurrencia.
7. Revisar aplicabilidad y alcance antes de proponer cualquier habilitacion futura.

La siguiente tarea concreta es el paso 1–2; no activar flujo positivo por completar
un schema. La primera etapa tiene can_confirm=false. Revisiones de desarrollo
ficticias; aceptacion real/empresa posterior al MVP segun acuerdo del usuario.
