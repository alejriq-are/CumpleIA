# M3-T1 — Expediente de revisión jurídica y salida a MVP

Estado: preparado para revisión humana, **no aceptado**. Consulta documental:
16/10/2026. Base funcional: `9676dfc5341bab2717d91e4931f3acae0e3706e0`.
[Registro estructurado](policy-evidence/review-package-v1.json).
Este expediente no es un payload de publicación ni una instrucción de selección.
Política de infancia actual: `m3-t1-infancia-pruebas-negativas-v1`, fuentes y
aceptación pendientes, activación deshabilitada. Solo datos ficticios.

## Fuentes contrastadas y límites

| ID | Evidencia | Resultado de la consulta |
| --- | --- | --- |
| S1 | [Diario Oficial, Ley 21.719, 13/12/2024](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf); [copia pública original](policy-evidence/ley-21719-do-2024-12-13.pdf) | Publicación consultada; SHA-256 en el registro. No sustituye el texto consolidado. |
| S2 | [BCN, texto consolidado](https://www.bcn.cl/leychile/navegar?i=1209272) | Artículos 15 ter, 16, 16 bis, 16 ter, 16 quáter y disposiciones transitorias consultados. Versión consultada en línea; no se archiva un HTML ni se acredita autenticidad por un hash del PDF original. |
| S3 | [Ministerio de Economía, propuesta de prórroga](https://www.economia.gob.cl/2026/09/01/gobierno-propone-ampliar-plazo-para-implementar-nueva-ley-de-proteccion-de-datos-y-institucionalidad.htm) | Anuncio de propuesta hacia diciembre de 2027; no se trata como modificación promulgada. |
| S4 | Orientaciones/lista de operaciones EIPD de la Agencia | No verificadas en búsquedas acotadas en fuentes oficiales. No equivale a probar inexistencia. Requiere revisión humana de aplicabilidad y seguimiento. |

La publicación original contempla EIPD previa ante alto riesgo, supuestos
obligatorios y orientaciones de la Agencia; contempla descripción, finalidad,
necesidad/proporcionalidad, riesgos y mitigación. La consulta a la Agencia es
facultativa en el supuesto descrito, no se convierte en requisito universal del
producto. Fuente: [S1, artículo 15 ter](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf).

El texto consolidado diferencia infancia, adolescencia y datos sensibles de
adolescentes menores de 16, considerando interés superior, autonomía progresiva
y autorizaciones. No se reduce todo tratamiento de menores de 16 a una única
regla de consentimiento parental. El régimen reformado consultado conserva la
entrada en vigor calculada al 01/12/2026; se debe revalidar antes del piloto.
Fuente: [S2, artículo 16 quáter y primero transitorio](https://www.bcn.cl/leychile/navegar?i=1209272).

## Política propuesta para aceptar, sin activación

Esta es una propuesta de controles del producto, no requisitos legales añadidos:

1. Mantener solo revisiones negativas durante desarrollo. Una resolución completa,
   una fuente identificada, un hash coincidente o una prueba aprobada no conceden
   autoridad jurídica, no confirman el expediente ni activan EIPD.
2. Distinguir declaración de fuente, verificación documental, revisión de
   aplicabilidad y aceptación jurídica. Registrar autoridad emisora, instrumento,
   versión, URL, copia/evidencia disponible, fecha de consulta, cobertura, análisis
   y responsable. La revisión puede rechazar la suficiencia de las fuentes.
3. El revisor debe resolver expresamente las fronteras de edad (casos 13, 14,
   15, 16, 17 y 18), datos sensibles, autorizante y representación; excepciones
   sensibles/biométricas y coexistencia de supuestos. No cambiar reglas por
   interpretación automática ni usar una EIPD como base de licitud independiente.
4. Aceptar una versión exacta con alcance, limitaciones, fuentes y pendientes.
   Cambios materiales o normativos requieren nuevo artefacto y revisión. La
   aceptación no permite cambiar el historial ni volverlo aplicable retroactivamente.
5. Separar revisor jurídico, aceptación técnica y administrador autorizado a
   publicar/seleccionar. El permiso de una organización no otorga autoridad global.
   La aceptación puede permanecer asociada a una política **deshabilitada**.

## Acta mínima que falta

El responsable humano debe aportar identidad/rol y, para un registro de
plataforma, identidad verificable compatible con `accepted_by`; decisión
(acepta/requiere cambios/rechaza), versión y alcance revisados, fuentes y su
verificador, fundamento, reservas, fecha UTC, referencia y evidencia del acta,
commit de validación técnica. No poner nombres/UUID ficticios en un acta real.
Una respuesta automática, el autor del commit o una autorización de push no son
esta acta. El registro JSON deja todos esos campos sin completar.

El contrato global existente (`backend/app/services/eipd_policy.py`) exige
responsable/evidencia/commit para declarar aceptación; no verifica por sí mismo
la autenticidad del acta. La política de infancia V1 fija ambos estados pendientes
(`backend/app/schemas/eipd_child_persistence.py`). Incorporar aceptación de infancia
exigirá un contrato sucesor versionado y compatible; no mutar V1 ni sus snapshots.
No publicar ni seleccionar una política nueva en el entorno operativo en este bloque.

## Criterios de salida a MVP

Son decisiones de producto propuestas; todos los gates siguen pendientes de
aceptación/evidencia de liberación. La copia PDF o este documento no los satisfacen.

| Gate | Evidencia necesaria para cerrar | Responsable propuesto |
| --- | --- | --- |
| G1 Alcance MVP | Rutas y funciones incluidas/excluidas, contrato y casos de aceptación; decidir si el piloto ofrece solo documentación con EIPD bloqueada. | Responsable de producto |
| G2 Revisión jurídica | Acta anterior; vigencia y fuentes revalidadas; instrumentos complementarios revisados o limitación motivada y aceptada; sin afirmar certificación oficial. | Revisor designado |
| G3 Política versionada | Nueva referencia/hash, actores autenticados, autoridad separada, publicación/selección auditada; negativos conservados y activación deshabilitada. | Responsable técnico y administrador autorizado |
| G4 Validación técnica | CI del commit candidato y matriz del flujo afectado: tenant/rol/suscripción, aislamiento, inmutabilidad y FK RESTRICT, contexto obsoleto, conflictos/concurrencia, rollback, política corrupta y bloqueo de positivos. No se arrastran conteos históricos como evidencia de un candidato nuevo. | Responsable técnico |
| G5 Operación del piloto | Entorno identificado, secretos y accesos gestionados, restauración comprobada, retención/privacidad, soporte e incidentes, monitoreo y condiciones de retiro del piloto. | Responsable operativo |
| G6 Datos reales | Autorización separada del propietario del producto; alcance/empresa piloto y responsabilidades definidos, revisión jurídica y operativa, migración/contratos para procedencia real sin convertir registros ficticios, minimización y pruebas previas. | Producto, revisor y operación |
| G7 Activación EIPD | Decisión nueva y explícita; diseño/pruebas de positivos, evidencia atómica, revocación, vigencia y control por política. No es requisito para un MVP que excluya dicha función. | Producto, revisor y responsable técnico |

Orden propuesto: cerrar alcance y revisión; validar el candidato y operación;
aprobar piloto/ingreso de datos reales por separado. Mantener G7 cerrado mientras
la instrucción del usuario siga bloqueando activación. Si el MVP excluye una
función, documentar la exclusión y el bloqueo, no simular cumplimiento.

## Continuidad

Bloque dependiente detenido: falta designación y acta de revisión humana, cierre
de fuentes complementarias y decisión de alcance del MVP. Desarrollo con datos
ficticios puede continuar en bloques que no dependan de esa aceptación. Una vez
recibida la revisión, preparar el contrato sucesor y su prueba de compatibilidad;
publicación operativa, datos reales y activación requieren decisiones separadas.
