# M3-T1 — Preparacion documental de investigacion v1

Fecha: 2026-10-09. §128. Estado: DISENO PREPARADO; NO IMPLEMENTADO.
Base revisada: f9313a887437ed05df9dfced4b8d581838e3eee6.

## Alcance elegido

Siguiente incremento: expediente documental para investigacion_art16quinquies,
datos no sensibles y titulares adultos, asociado al alcance RAT y con la base
ordinaria de interes legitimo/LIA vigente. La restriccion inicial es de producto,
no una limitacion juridica general del articulo. Rutas sensibles, infancia y otros
regimenes pendientes seguiran derivando a revision; no abrir gates excepcionales.

Observacion de codigo: special_conditions.py evalua salud y biometria en ruta de
consentimiento; el regimen investigacion no tiene rama de validador y deriva a
validador_no_implementado. La representacion sensible tambien sigue pendiente.
No interpretar las matrices historicas como ausencia de todos los validadores.

## Fuente primaria y separacion del criterio de producto

Consultado texto de Ley 21.719 publicado por BCN/Ley Chile:
https://nuevo.leychile.cl/navegar?idNorma=1209272, articulo 16 quinquies.
La norma vincula este regimen a finalidades exclusivas de interes publico,
exige acreditar medidas de calidad/seguridad, agrega gestion de riesgos para datos
sensibles y establece anonimizar datos antes de publicar resultados. Permite
conservacion indeterminada bajo sus condiciones; el producto no la presume por
marcar una finalidad. Fuente consultada no equivale a aceptacion juridica del
expediente ni a verificacion de instrucciones complementarias de la Agencia.

Reutilizar LIA como condicion del primer incremento es una decision conservadora
de implementacion; no afirmar que un expediente LIA de este producto sea requisito
formal universal impuesto por el articulo. Ley fija sin condicionarla a fechas.

## Contrato propuesto y aplicabilidad

Nombre previsto ResearchAssessmentV1; schema cerrado extra=forbid, campos opcionales
en borrador. No modificar schemas historicos ni sus hashes. Reutilizar las
respuestas/evidencias documentales existentes para si/no/pendiente.

| Grupo | Datos del expediente | Completitud propuesta |
| --- | --- | --- |
| Finalidad | Tipo historico/estadistico/cientifico/estudio-investigacion, descripcion, analisis de interes publico | Obligatorios para preparar esta ruta |
| Exclusividad | Respuesta y analisis sobre uso exclusivo, controles frente a reutilizacion incompatible | Si requerido; no/pendiente impiden preparacion |
| Calidad y seguridad | Medidas, aplicacion efectiva declarada y evidencia referenciada | Analisis y evidencia presentes; no certificar eficacia real por existencia de campos |
| Difusion | Si/no/pendiente sobre publicacion de datos/resultados | Determina aplicabilidad del grupo de anonimizacion |
| Anonimizacion | Procedimiento, analisis y evidencia de medidas previas a publicar | Obligatorios si difusion=si; pendiente bloquea resolver aplicabilidad |
| Conservacion | Descripcion del criterio y condiciones documentales | No conceder plazo indefinido automaticamente |
| Alcance | Selectores de categorias y titulares vinculados al RAT | Subconjunto valido y cobertura conservadora completa del alcance inicial |

Difusion=no: grupo de anonimizacion no aplicable, conservando razonamiento. No
confundir seudonimizacion con anonimizacion. Documento fuera de regimen/alcance es
residual y requiere revision. Categorias sensibles o menores/vulnerabilidad no se
resuelven con este contrato inicial; mantener evaluaciones existentes de esas rutas.

## Integracion por pasos

1. Agregar schema y evaluador puro de completitud/aplicabilidad; sin persistencia,
   sin levantar validador_no_implementado en el evaluador especial ni confirmar.
2. Probar si/no/pendiente, campos/evidencias, difusion y alcance, datos sensibles,
   asociaciones residuales y coherencia con LIA; usar entorno de pruebas aislado.
3. Disenar version nueva de binding documental con tests de compatibilidad; no
   recalcular ni reinterpretar hashes historicos. Luego persistencia/migracion/API.
4. Integrar readiness especial y gate solo tras revisar coherencia con las seis
   bases, tenant/RLS, RAT vigente, EIPD y confirmacion/reemplazo/concurrencia.
5. Revisar criterios de aceptacion antes de declarar ruta preparada funcionalmente.

## Criterios de aceptacion del primer incremento

- Evaluador puro devuelve issues y aplicabilidad deterministas, sin efectos DB.
- Si/no/pendiente y ausencia documental nunca se interpretan como autorizacion.
- LIA/finalidad/alcance incompatibles requieren revision; no inventar autorizacion.
- Positivo documental no habilita confirmacion mientras integracion este pendiente.
- Pruebas de escritura solo mediante base aislada; no tocar selector EIPD revision 1.

Pendiente implementacion. M3-T1 EN PROGRESO; activacion EIPD bloqueada.
