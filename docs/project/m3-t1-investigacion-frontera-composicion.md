# M3-T1 §143 — Frontera, screening y composicion de investigacion

## Revision de codigo y limite actual

HEAD bb3e941. EipdFrontierReadinessV1 solo admite rutas sensible_derechos,
sensible_biometrica_derechos/sin_resolver y ContextV1. EipdReadinessV2 usa esa frontera.
Composicion InputV1 y InputV2 contienen ContextV1/StoredV1; no cubren research.
Funciones puras de resolucion/revision versionadas §142 ya admiten material V2,
pero no estan conectadas a API. No quitar campos V2 para simular cobertura V1.
Ley fija, M3-T1 EN PROGRESO y confirmacion/activacion EIPD bloqueadas.

## Contratos sucesores previstos

- EipdFrontierReadinessV2 y evaluate_eipd_frontier_v2: ContextV2 cerrado; ruta
  investigacion_no_sensible_adultos o sin_resolver en este incremento. Conservar
  FrontierV1 para sus rutas anteriores, sin atribuirles investigacion. Salida incluye
  readiness research y asociacion, special/screening completos y motivos acumulados.
- EipdReadinessV3 y evaluate_eipd_screening_v3: evaluation_version Literal[3];
  contexto V2 y frontera V2. No confundir evaluation_version 3 con binding_version
  12 del screening documental. Mantener ScreeningV2 intacto para ContextV1.
- EipdControlCompositionInputV3 / CompositionV3: campos de identidad/estado/RAT de
  servidor, ContextV2, resolucion StoredV1 o StoredV2 con dispatch cerrado, ultimo
  evento y politica/identidad reales con contratos existentes. No extender InputV1
  ni InputV2. composition_version Literal[3] en resultado y permiso fijo false.

Entrada V3 de resolucion permite V1 expresamente para diagnosticar falta de cobertura,
no para aprobarla. Ninguna nueva union acepta version desconocida o metadatos libres.
Los schemas HTTP sucesores se agregaran solo cuando se conecte lectura/escritura.

## Frontera pura de investigacion

Primero revalidar ContextV2 completo y calcular resultado research de completitud y
asociacion con RAT/base/LIA finales. Alcance inicial mantiene interes_legitimo_art13d,
LIA preparada, RAT no sensible y titulares adultos no vulnerables; las demas rutas
requieren revision. Revisar rol responsable y alcance/finalidad sin inventar criterios
normativos nuevos. No interpretar un expediente aportado como declaracion especial
negativa o como aceptacion de excepcion legal.

Ejecutar evaluadores especiales y screening con research completo y base explicita.
Verificar especiales V11 y screening V12; versiones anteriores con research requieren
revision, asociaciones obsoletas se conservan. Reconciliar presencia del expediente,
declaracion de fines investigacion y condicion/alcance declarados: discordancias
requieren revision, nunca seleccionar automaticamente una ruta de autorizacion.

Acumular incompletitud, obsolescencia y falta de cobertura, sin filtrar otros motivos
sensibles/infancia/biometria o EIPD. validador_no_implementado y bloqueos historicos
siguen visibles. En el primer incremento frontera V2 no se declara preparada mientras
ese validador no este integrado/revisado; completitud research se muestra separada.
No puede confirmar ni habilitar una politica; no aceptar flags preparados del cliente.

## Screening V3 y composicion V3

Screening V3 transmite ContextV2 sin proyeccion, siempre legal_basis y research.
Conserva deteccion EIPD y motivos completos de screening, con frontera documental
separada. No convertir pendiente_revision/requiere_eipd en exencion por expediente
completo; ninguna preparacion autoriza confirmacion. No extender prepared_exceptions
para investigacion en este primer incremento.

Composicion V3 evalua identidad tenant/assessment y estado, RAT actual, base ordinaria,
frontera/screening, research, resolucion versionada, revision y politica. Orden de
etapas nuevo y fijo que incluya research, sin modificar STAGES de composicion V1/V2.
Reusar evaluadores puros de bases ordinarias, pero no componer V2 sobre material
proyectado sin declarar cobertura pendiente. Diferenciar coincidencia de hashes,
preparacion documental, decision humana e identidad/politica; ninguna sustituye otra.

Revision V1 con research permanece visible pero obsoleta/no cubierta. Revision V2
vigente aun debe cumplir controles de identidad, documento completo, research vigente,
RAT vigente y politica; decision continuar no activa gate por si sola. Politica
actual deshabilitada/fuentes y aceptacion pendientes conserva bloqueo. Nuevos tipos
no crean politica, evento ni actor/fecha. Si contexto ausente, resultados cerrados de
incompletitud/revision, nunca excepciones permisivas.

## Compatibilidad, API y eventos

Primero funciones/contratos puros y tests; luego integrar lectura versionada y decidir
metadatos de eventos y API V2 bajo locks. No introducir columnas ni backfill en este
paso. Conservacion V1/V2 de frontera/screening/composicion probada con fixtures fijas.
Historicos no reciben identidad V3 ni research sintetico. GET/readiness no escribe.
Contexto V2 sin research (null explicito) no se transforma en V1 silenciosamente:
frontera V2 informa ausencia/ruta sin resolver; caller selecciona dispatcher explicito.

## Pruebas y secuencia siguiente

1. Frontera V2 pura: material completo pero bloqueo conservador, ausencia/null,
   obsolescencia research, discordancia de declaraciones, datos sensibles/menores,
   cobertura antigua y coexistencia de motivos. Entradas cerradas y no mutacion.
2. Screening V3 y composicion V3 puros: deteccion conservada, identidad/estado/RAT,
   revision historica visible, politica bloqueada, orden determinista de motivos,
   can_confirm false y ninguna bandera externa preparada.
3. Lectura/API/resolucion V2 y metadatos de eventos con pruebas tenant/rollback/locks;
   reglas de seleccion/reaporte y contrato de salida definidos antes del escritor.
4. Aceptacion revisada y revision del validador especial antes de considerar habilitar.

Este paso documental no ejecuta suite nueva. Ultima validacion §142: 327 focalizadas
y 272 regresiones aprobadas. Sin codigo nuevo, migracion, cambio operacional ni
commit/push. Proximo: implementar frontera V2 pura con bloqueo conservador.
