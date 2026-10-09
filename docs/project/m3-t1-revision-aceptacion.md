# M3-T1 — Revisión de aceptación

Fecha de actualizacion: 2026-10-09 (§122). Estado: EN PROGRESO. Revisión documental y de código;
no modifica reglas ni amplía el alcance. Última suite completa registrada:
3654 passed (§106), posterior a concurrencia administrativa HTTP.
Checkpoints inferiores son históricos; el total no acredita cierre integral.

## Estado actual del canal operativo local

Secuencia personal local validada hasta politica deshabilitada seleccionada, revision 1.
Ver [cierre delimitado §122](m3-t1-eipd-cierre-validacion-local.md). Pendientes de
rotacion/retiro, fuentes, aceptacion y alcance integral; no confundir esta secuencia
con cierre de M3-T1 ni con habilitacion excepcional.

## Fuentes y criterio

Diseño: modulo3-licitud-diseno.md, especialmente §13.2, §15, §17–24 y
checkpoints §25–28. Evidencia: backend/app/{db,schemas,services,api} y tests.
El backlog general docs/backlog.md no tenía entrada M3-T1; se añade referencia
a esta matriz. Los checkpoints antiguos son históricos: sus frases de pendientes
no representan por sí solas el estado actual. El número total de pruebas no
certifica todas las combinaciones ni constituye validación jurídica externa.

## Matriz de implementación y evidencia

| Criterio | Estado observado | Evidencia |
| --- | --- | --- |
| Evaluación por finalidad, serie/versiones y alcance M2 | Implementado y probado | schemas/licitud.py; services/licitud.py; tests/test_services_licitud.py; tests/test_api_licitud.py |
| Tablas, constraints, índices, JSONB y migraciones | Implementado; head local b17d95c0286f verificado §122 | db/models.py; alembic/versions/5997a757f17b_modulo3_licitud_persistencia.py y migraciones posteriores |
| Tenant/RLS y FK compuestas | Probado en PostgreSQL/app_user | tests/test_rls_isolation_licitud.py y tests/test_api_licitud.py |
| Canonización, hash y snapshot desde M2 | Implementado y probado | tests/test_services_licitud.py; HTTP con RAT real |
| Seis bases ordinarias y preparación propia | Implementado y probado | services/{consentimiento,lia,contract,legal_obligation,rights_defense,economic_obligations}.py; pruebas de servicios/API |
| Borrador, confirmación, reemplazo e inmutabilidad | Implementado y probado | tests/test_confirmation_licitud.py; tests/test_concurrent_creation_licitud.py; tests/test_api_licitud.py |
| Screening EIPD, motivos y asociación vigente | Implementado; positivos/pendientes bloquean | services/eipd.py; tests/test_eipd_persistence.py; pruebas transversales |
| Geolocalización preparada | Implementado y probado | services/geolocation.py; tests/test_services_geolocation.py; tests/test_transversal_geolocation.py; HTTP/confirmación |
| Consentimiento expreso sensible del titular | Implementado y probado | services/sensitive_consent.py; tests/test_services_sensitive_consent.py; test_api_sensitive_confirmation_six_bases |
| Compatibilidad documental histórica | Probada; documento nuevo no cubierto requiere revisión | pruebas API de persistencia/compatibilidad; comparadores especiales v1–v10 y EIPD v1–v11 |
| Excepciones sensible/biometrica de derechos | Preparacion/readiness integradas; confirmacion bloqueada por EIPD | services/{sensitive_rights_exception,biometric_rights_exception,special_conditions,licitud}.py; seis HTTP por cada excepcion (§56/§58) |
| Resolucion EIPD e historial | Persistencia/asociaciones/API, evaluador documental, readiness/vigencia, accion humana y composicion orientativa implementados; continuar/gates pendientes | eipd_resolution.py; db/models.py; migracion b51d3f6a9c20; 36 pruebas PostgreSQL/RLS (§63) y 25 HTTP documentales (§64); 18 pruebas de readiness/vigencia (§66) |
| Regímenes especiales restantes | Pendiente funcional; bloqueo explícito | services/special_conditions.py mantiene validador_no_implementado para rutas no soportadas |
| Representación en ruta sensible | Pendiente funcional delimitado | sensitive_consent.py: representacion_no_preparada; no implica prohibición jurídica de representación |
| Coexistencia sensible/geolocalización | Probada a nivel transversal y HTTP conjunto | test_sensitive_and_geolocation_transversal; test_api_sensitive_geolocation_joint_confirmation (4 casos) |
| Concurrencia/rollback de ruta sensible | Seis bases con RAT simulado; coexistencia sensible/geolocalización con RAT real y base consentimiento | test_confirm_postgres_reemplazo_y_rollback_real; test_concurrencia_real_revalida_tras_bloqueo; test_confirmation_concurrent_real_rat_joint |

Las rutas pendientes incluyen excepciones sensibles del catálogo, excepciones y
contextos restringidos de salud, biometría, infancia/adolescencia e investigación. La vulnerabilidad
sigue produciendo revisión. No se declara ilícita una ruta por faltar su validador.

## Brechas y siguiente orden propuesto

1. **Completado 2026-10-06:** evidencia HTTP de coexistencia sensible/geolocalización;
   confirmación conjunta, respuestas no/pendiente en cualquiera, asociaciones
   obsoletas y reaporte, conservación íntegra del confirmado, EIPD positivo,
   reparación/reemplazo y protección posterior. 4 casos focalizados aprobados.
2. **Ampliado 2026-10-06:** relectura/concurrencia con constructor RAT real,
   coexistencia sensible/geolocalización y base consentimiento. Ocho casos cubren
   confirmación commit/rollback, cambios pendientes de ambos documentos y cambio
   de sensibilidad M2 durante espera. No extrapolar esta cobertura RAT real a
   las otras cinco bases; estas conservan concurrencia con RAT simulado.
3. Elegir el próximo régimen no soportado y fijar su alcance antes de implementar;
   definir expediente, completitud/aplicabilidad, gate y aceptación. No se elige
   todavía un régimen ni se inventan requisitos legales en esta revisión.
4. Delimitar representación sensible y cobertura granular categoría/titular si
   se incorporan: hoy se revisa representación y se exige cobertura conservadora
   de categorías sensibles y todos los grupos del alcance RAT.
5. Consolidar criterios de cierre de M3-T1 y revisión de cambios antes de marcar
   DONE. No se deduce cierre por la cantidad de pruebas.

## Diferidos y aspectos no exigibles sin ampliar alcance

- Workflow completo de EIPD: diferido explícitamente en diseño §10 y §18.13.
  El screening y bloqueo actuales sí forman parte de esta revisión.
- Interfaz frontend M3: no se encontró ruta licitud; §13.2 define persistencia,
  contratos, reglas y pruebas, sin criterio explícito de entrega frontend M3-T1.
  No se convierte aquí en requisito de cierre; requiere delimitación de roadmap.
- Metadata de evidencia no equivale a verificar externamente documentos; M5
  conserva la frontera de carpeta de evidencia indicada en el diseño.

Sin cambios de código, migraciones ni commit. M3-T1 continúa EN PROGRESO.


## Avance posterior a la revisión: coexistencia HTTP

Añadido test_api_sensitive_geolocation_joint_confirmation: dos expedientes por
respuestas no/pendiente (4 casos), PostgreSQL/app_user/RLS y RAT real.
Preparación conjunta confirma; cambiar documento sin reaporte vuelve asociaciones
obsoletas. Reaportar controles no aprueba documento negativo/pendiente. GET y POST
conservan los mismos resultados especiales/EIPD; rechazo no modifica borrador ni
confirmado. EIPD positivo bloquea ambos expedientes completos; reparar y aportar
screening negativo permite reemplazo. Confirmado rechaza PATCH posterior.

Validación focalizada: 4 passed, 85 deselected en tests/test_api_licitud.py.
Black/Ruff/whitespace correctos. Última suite completa anterior: 1217 passed;
no se presenta este conteo como ejecución completa posterior. Sin cambios de
implementación ni migraciones; sin commit. Próximo paso: revisar el límite de
concurrencia con constructor RAT simulado. M3-T1 EN PROGRESO.


## Avance: concurrencia con constructor RAT real

Test_confirmation_concurrent_real_rat_joint en test_concurrent_creation_licitud.py:
filas M2 reales, constructor no simulado, dos conexiones app_user/RLS, espera
observada mediante pg_blocking_pids y caché inicial del borrador en segunda sesión.
Tras commit de primera confirmación, segunda rechaza; tras rollback, segunda
confirma. Cambios a pendiente de prueba sensible o aviso geográfico rechazan y
conservan el confirmado. Cambio de is_sensitive en M2 durante bloqueo se relee,
rechaza y conserva los snapshots históricos, sin actualizar el borrador en rechazo.

Validación: 8 casos nuevos aprobados; módulo completo 13 passed. Sin cambios de
implementación ni migraciones; última suite completa anterior 1217 passed.
No se repite suite general para ampliación focalizada de pruebas. Formato/lint/
whitespace correctos, sin commit. Alcance real RAT: base consentimiento y ambos
regímenes; las otras bases no se afirman cubiertas por esta nueva prueba.

Siguiente paso: priorizar y delimitar el próximo régimen especial pendiente.
M3-T1 EN PROGRESO.


## Priorización posterior

Salud/perfil biológico es el siguiente régimen, diseño §31. Primer alcance:
preparación documental por consentimiento expreso, con fundamento/contexto propios.
Delimitación completada; contrato físico, matriz, persistencia y gate pendientes.
Excepciones sin consentimiento permanecen fuera del primer soporte.


## Diseño de contrato de salud

§32 fija HealthAssessmentV1 y matriz de completitud/aplicabilidad. Contextos
restringidos documentan sustento pero conservan revisión en primer soporte.
Diseño terminado; implementación pendiente. Siguiente: schema y pruebas.


## Schema de salud implementado

§33: HealthAssessmentV1 y tipos auxiliares cerrados con borradores parciales.
107 pruebas focalizadas aprobadas, incluidas 49 nuevas; sin persistencia/HTTP/gate.
Próximo paso: persistencia/exposición y asociaciones. Salud sigue bloqueada.


## Persistencia de salud implementada

§34: JSONB nullable, exposición HTTP y asociaciones especiales v8/EIPD v9.
Históricos conservados con revisión de documento no cubierto; residual bloquea.
Nueve casos HTTP nuevos; suite completa posterior 1287 passed. Evaluador/gate
salud pendientes; M3-T1 EN PROGRESO, sin commit. Próximo: evaluador/readiness.


## Preparación de salud implementada

§35: evaluador puro y health nullable en readiness. Suite general 1354 passed,
65 pruebas puras nuevas y dos HTTP; ajuste final de motivo ausente validado por
las 65 puras. Contextos restringidos continúan revisión; completo no habilita
confirmación. Próximo paso: gate con barreras concurrentes. M3-T1 EN PROGRESO.


## Salud preparada integrada

§36 habilita primer soporte documental por consentimiento de salud, conservando
restricciones y dependencias. Suite completa 1407 passed. HTTP con seis bases y
contextos otro/laboral; rollback/concurrencia con RAT simulado y filas/locks reales.
Coexistencia de tres regímenes preparada verificada en transversal puro; HTTP
conjunto y concurrencia específica de salud con constructor RAT real pendientes.
No extrapolar la prueba RAT real de sensible/geolocalización a salud.
M3-T1 EN PROGRESO, sin commit.


## Evidencia conjunta de salud, sensible y geolocalización

Seis casos HTTP nuevos con los tres regímenes preparados por consentimiento:
respuestas no/pendiente en cada expediente, asociaciones obsoletas, rechazo,
conservación del vigente, reparación, bloqueo EIPD positivo, reemplazo y protección
del confirmado. GET y POST conservan los motivos de preparación y EIPD.

Doce casos concurrentes nuevos con constructor RAT real y PostgreSQL/app_user/RLS:
confirmación con commit/rollback, cambio de cada expediente y cambio del RAT
mientras otra confirmación espera el bloqueo. La segunda sesión precarga el
borrador para comprobar la relectura; se conserva un único confirmado y su historia.
Alcance: base consentimiento_art12, salud en contexto otro. Las otras cinco bases
mantienen la evidencia previa de concurrencia con constructor RAT simulado.

Validación focalizada: módulo de concurrencia 25 passed y HTTP conjunto 10 passed,
18 casos nuevos. Última suite completa anterior: 1407 passed; no se reejecutó en
este paso de pruebas/documentación. Black/Ruff/whitespace correctos. Sin cambios
de implementación, migración nueva ni commit. M3-T1 EN PROGRESO.
Próximo: revisar alcance de representación sensible y criterios de cierre.


## Representación sensible y criterios de cierre revisados

Revisión de alcance de producto, sin ampliar las autorizaciones implementadas.
Se mantiene §24.3: given_by titular puede preparar la ruta sensible;
representante_legal y mandatario conservan el expediente y requieren revisión
con representacion_no_preparada. Salud depende de esa preparación sensible.
No se deduce una prohibición jurídica ni se habilita infancia/adolescencia.
El soporte de representación queda pendiente de diseño de acreditación, vínculo,
alcance, vigencia, completitud y asociaciones; no basta con cambiar given_by.
Cobertura parcial categoría/grupo sigue pendiente de una matriz explícita en RAT.

Evidencia existente: test_sensitive_representation_review cubre ambos valores;
test_sensitive_transversal_blockers cubre representante_legal;
test_health_coherence_dependency comprueba dependencia para representante_legal.
No se encontró prueba HTTP específica de representación en la ruta sensible.
Próximo paso concreto: ambos valores por HTTP, con y sin salud; GET/POST coherentes,
asociaciones reaportadas, rechazo que preserve borrador y confirmado anterior,
y reparación a titular que permita el reemplazo. Es verificar el límite actual,
no implementar ni autorizar la representación.

Criterios de cierre, derivados de §13.2 y de los límites actuales:

| Criterio | Situación y condición pendiente |
| --- | --- |
| Persistencia, constraints, índices, migraciones y RLS | Implementados; revisar diff final y cadena Alembic antes del cierre |
| Snapshot M2, canonización/hash y compatibilidad | Implementados; mantener asociaciones especiales v8/EIPD v9 y lectura histórica |
| Seis bases ordinarias, sensible titular, geolocalización y salud del primer alcance | Implementados; no extrapolar a rutas bloqueadas |
| Confirmación/reemplazo, bloqueo y conservación histórica | Evidencia existente; añadir HTTP específico de representación |
| Regímenes/rutas pendientes y alcance parcial | Mantener revisión explícita; no declarar todos los regímenes implementados |
| Evidencia final de integración | Reejecutar suite completa después del siguiente cambio; 1407 es la última ejecución completa anterior |
| Delimitación de entrega y revisión final | Revisar cambios y pendientes explícitos antes de declarar DONE; no cerrar por conteo de pruebas |

La revisión de criterios no equivale a satisfacerlos. Regímenes especiales
restantes siguen pendientes funcionales; su eventual diferimiento para cierre
requiere una decisión explícita de alcance, no una reclasificación silenciosa.
Workflow completo EIPD sigue diferido; frontend no se agrega como requisito por
esta revisión. Metadata documental no verifica externamente evidencia.
Este paso solo actualiza documentación; no reejecuta pruebas ni crea migración
ni commit. M3-T1 EN PROGRESO.


## 39. Representación sensible verificada por HTTP

Cuatro casos de test_api_sensitive_representation_preserves_confirmed:
representante_legal/mandatario, cada uno con y sin salud, junto a geolocalización.
RAT real y PostgreSQL/app_user/RLS. Mandatario aporta facultad expresa en checklist
para aislar el límite de representación sensible, que sigue requiriendo revisión.
GET informa representacion_no_preparada; POST rechaza con los mismos motivos
especiales/EIPD. Rechazo conserva íntegros borrador y confirmado anterior.

Cambiar given_by vuelve obsoleta la asociación especial; el hash EIPD no incluye
el checklist general y permanece vigente. Reaportar controles no habilita la
representación. Reparar a titular permite reemplazo con screening negativo;
EIPD positivo mantiene bloqueo. El nuevo confirmado rechaza PATCH posterior.
No se amplía soporte de representación ni se modifica implementación.

Validación: cuatro casos focalizados y suite completa 1429 passed en 140.16s.
Black/Ruff/whitespace correctos. Sin migración nueva ni commit.
M3-T1 EN PROGRESO. Próximo: revisar diff final y cadena de migraciones, y dejar
explícita la decisión de alcance de regímenes pendientes antes de declarar DONE.


## 40. Revisión de cambios y cadena de migraciones

Rama feature/m3-t1-licitud-persistencia, HEAD 2fd8881; cambios sin commit.
Revisión de router/API, modelos, confirmación y transacción runtime:
permisos view/edit y suscripción en servidor; sesión runtime app_database_url;
confirmación bloquea serie, relee borrador con populate_existing, valida contexto
M2 y preparación antes de reemplazo, libera índice parcial con flush y deja
commit/rollback al caller. get_db hace rollback ante excepción.
Esta revisión focalizada no constituye auditoría exhaustiva de seguridad.

Alembic heads/current: único head e28a0c3f6d97, aplicado localmente.
Cadena lineal 5997a757f17b -> 7c9e1a3b5d20 -> 8d2f4a6c9e31 ->
9e3b5d7f1a42 -> ae4c6e8b2f53 -> bf5d7f9c3a64 -> c06e8a1d4b75 ->
d17f9b2e5c86 -> e28a0c3f6d97. Migraciones nuevas agregan columnas JSONB
nullable/check objeto y downgrade elimina check/columna. No se ejecutó downgrade
ni upgrade de ensayo; no se alteraron migraciones aplicadas.

Black --check y Ruff: 46 archivos Python nuevos/modificados aprobados.
git diff --check correcto. Última suite integral: 1429 passed (§39), no repetida.
Inventario incluye archivos sin seguimiento: git diff --stat por sí solo no
representa la totalidad de la entrega.

Hallazgo abierto: alembic check global falla por diferencias fuera de las tablas
M3 (índices presentes en DB y ausentes en metadata, y nombre de unique constraint
DiagnosticAnswer). Comparación autogenerate limitada a legal_assessment_series y
legal_assessments devuelve cero diferencias. Esto no verifica políticas RLS ni
compara exhaustivamente check constraints; su evidencia proviene de migraciones
y pruebas existentes. No generar una migración que elimine índices a partir de
este resultado. Procedencia y corrección del drift global quedan por investigar;
no se atribuye automáticamente a este trabajo ni se declara preexistencia probada
para todas las diferencias.

Próximo paso: inventariar y contrastar drift global contra migraciones/metadata
para decidir una corrección concreta sin perder índices. Luego queda la decisión
explícita de alcance de regímenes pendientes. M3-T1 EN PROGRESO; sin commit.


## 41. Drift global de metadata corregido

Inventario: 31 operaciones propuestas por autogenerate; 29 eliminaciones de
índices y remove/add de una unique por diferencia de nombre. Procedencia
contrastada con migraciones 0001_initial_schema (tenant y HNSW),
0002_modulo1_cuestionario_config (activa/unique), 0005_diagnostico_api
(reference_documents) y 0010_modulo2_rat_persistencia (tenant/relaciones).

Modelos declaran ahora los 29 índices históricos en __table_args__: organization_id,
relaciones M2, ux_config_versiones_activa unique con predicado activa, y
knowledge_chunks_embedding_idx con HNSW/vector_cosine_ops. DiagnosticAnswer usa
nombre explícito uq_diagnostic_answers_diagnostic_id_pregunta_id. No cambia
la restricción de unicidad, las columnas ni las reglas funcionales.

Alembic check global aprobado: No new upgrade operations detected.
No se genera migración, no se ejecuta DDL ni se eliminan índices. Se corrige
metadata para reflejar la base creada por migraciones. Esta comparación no
constituye auditoría exhaustiva de checks/RLS ni ensayo de downgrade.

Black/Ruff y git diff --check correctos. Suite integral posterior:
1429 passed en 140.69s. Sin commit. M3-T1 EN PROGRESO.
Próximo: consolidar la propuesta concreta de alcance de entrega y los regímenes
pendientes, para resolver explícitamente los criterios de cierre sin declarar
soportadas las rutas que mantienen revisión.


## 42. Propuesta concreta de alcance de entrega

m3-t1-propuesta-entrega.md consolida alcance backend ya soportado, límites y
pendientes funcionales, evidencia y condiciones de cierre. Recomienda entrega
inicial de seis bases ordinarias, sensible titular, geolocalización y primer
soporte de salud; no marca diferidos los regímenes pendientes automáticamente.
Decisión pendiente: aceptar esa delimitación o continuar alcance integral.
M3-T1 EN PROGRESO; propuesta no equivale a DONE ni autorización de publicación.
Solo documentación; última suite 1429 passed y Alembic check aprobado (§41).
Sin pruebas reejecutadas, cambios de código, migraciones ni commit.


## 43. Decisión de alcance integral y siguiente régimen

Decisión explícita del usuario, 2026-10-06: continuar con el alcance integral.
La propuesta de entrega inicial de §42 no se acepta como recorte para cierre.
Representación, excepciones sensibles/salud, contextos restringidos, biometría,
infancia/adolescencia, investigación y cobertura granular continúan pendientes
funcionales; no se convierten en diferidos por esa propuesta. Workflow completo
EIPD conserva su diferimiento anterior. M3-T1 EN PROGRESO.

Siguiente régimen priorizado: biometricos_art16ter, ya declarado mediante
biometricos_identificacion_unica. Implementación incremental dentro del alcance
integral: empezar por ruta consentimiento expreso, sin dar por resueltas las
excepciones ni los regímenes concurrentes.

Fuente consultada: Ley 21.719, artículo 16 ter, texto oficial BCN:
https://www.bcn.cl/leychile/navegar?idNorma=1209272
El artículo vincula la ruta al inciso primero del art16 y exige informar sistema,
finalidad, período de uso y ejercicio de derechos. Sin consentimiento remite al
inciso segundo del art16bis; no reutilizar automáticamente el expediente sanitario
ni inferir excepción por elegir una base art13.

Decisiones de producto para diseñar el contrato siguiente: expediente biométrico
independiente, metadata del sistema y operaciones, alcance coincidente con RAT,
finalidad y período de uso documentados, canal/procedimiento para derechos,
constancia de información al titular y evidencia referenciada. Reutilizar
checklist/consentimiento sensible preparados en la primera ruta. No almacenar
plantillas biométricas, imágenes, huellas o grabaciones en este expediente.
Declaración específica explícita; el indicador sensible de M2 no identifica por
sí solo biometría. Infancia, salud y otros regímenes conservan sus propias barreras.

Próximo paso: contrato BiometricAssessmentV1 y matriz de completitud/aplicabilidad,
con campos cerrados/versionados, parciales en borrador, respuestas fundadas,
residualidad y asociaciones. Después schema/pruebas, persistencia/asociaciones,
evaluador/readiness, gate y evidencia HTTP/concurrencia. No habilitar gate antes
de esa secuencia. Excepciones biométricas seguirán pendientes dentro del alcance
integral hasta diseñar sus rutas propias; este primer bloque no las difiere.

Solo decisión/diseño preliminar; sin cambios de código, migraciones ni commit.
Última suite 1429 passed, Alembic check aprobado (§41), no reejecutados aquí.


## 44. Contrato y matriz de preparación biométrica

Diseño documental, 2026-10-06; no implementa schema ni habilita confirmación.
Fuente: artículo 16 ter completo en texto oficial BCN,
https://www.bcn.cl/leychile/navegar?idNorma=1209272 . Información específica:
sistema, finalidad, período de utilización y ejercicio de derechos; primera
ruta vinculada a consentimiento expreso. Los mecanismos documentales siguientes
son decisiones de producto para acreditar preparación, no requisitos textuales
adicionales atribuidos a la ley. Excepciones siguen pendientes dentro del alcance
integral y requieren diseño propio; no se importan desde salud automáticamente.

### 44.1 Contratos cerrados y borradores parciales

BiometricAssessmentV1: extra forbid; schema_version Literal[1] = 1.
Textos/respuestas/scope/route nullable; listas default_factory; no campos
approved, result, can_confirm ni no_aplica aportados por cliente.

| Campo | Tipo | Función |
| --- | --- | --- |
| purpose_description | str nullable | Finalidad evaluada en RAT |
| biometric_data_description | str nullable | Descripción de categorías, sin valores biométricos |
| processing_operations | str nullable | Operaciones cubiertas |
| scope | SpecialScopeV1 nullable | Categorías/grupos del alcance |
| route | Literal consentimiento_expreso nullable | Primera ruta implementable |
| unique_identification_analysis | str nullable | Tratamiento técnico y relación con identificación única |
| unique_identification_confirmed | ContractResponseV1 nullable | Declaración fundada de pertenencia al régimen |
| systems | list BiometricSystemV1 | Información específica por sistema utilizado |
| systems_coverage_analysis | str nullable | Cómo se cubren los sistemas de las operaciones declaradas |
| all_systems_documented | ContractResponseV1 nullable | Declaración de cobertura, no inferida por servidor |
| evidence | list ContractEvidenceV1 | Referencias generales documentales |
| notes | str nullable | Observaciones |

BiometricSystemV1: extra forbid; todos los textos/respuestas nullable y listas
vacías permitidas en borrador. Un registro agrupa la información de un sistema;
no duplicar globalmente los cuatro requisitos perdiendo su vínculo por sistema.

| Campo | Tipo | Función |
| --- | --- | --- |
| system_reference | str nullable | Identificador documental estable, no UUID M2 obligatorio |
| system_name | str nullable | Identificación comprensible del sistema |
| system_description | str nullable | Sistema y modalidad de uso, sin imágenes/plantillas |
| specific_purpose | str nullable | Finalidad específica de este sistema |
| purpose_alignment_analysis | str nullable | Relación de finalidad específica con finalidad RAT |
| use_period_description | str nullable | Período de utilización, incluyendo evento/criterio si corresponde |
| retention_alignment_analysis | str nullable | Coherencia documentada con conservación RAT |
| rights_exercise_description | str nullable | Procedimiento para ejercer derechos |
| rights_contact_channel | str nullable | Canal documentado; sin comprobar disponibilidad externa |
| information_reference | str nullable | Referencia al aviso/información proporcionada |
| system_identification_disclosed | ContractResponseV1 nullable | Identificación informada |
| purpose_disclosed | ContractResponseV1 nullable | Finalidad específica informada |
| use_period_disclosed | ContractResponseV1 nullable | Período informado |
| rights_exercise_disclosed | ContractResponseV1 nullable | Forma de ejercicio informada |
| evidence | list ContractEvidenceV1 | Referencias de información por sistema |

No fechas normativas inferidas, límites de duración por defecto, consulta de
registros ni datos biométricos crudos. evidence_date opcional factual se reutiliza
del tipo existente. No resolver coherencia de períodos comparando prosa como si
fuera una regla temporal ejecutable. Finalidad general compara canonización v1;
finalidad específica puede ser más concreta y se vincula mediante análisis,
no se exige igualdad literal con RAT. system_reference no vacío en preparación;
duplicados no vacíos por canonización v1 producen revisión, no deduplicación
silenciosa. M2/snapshot v1 no aporta inventario operativo de sistemas: cobertura
es documental; no afirmar exhaustividad verificada mediante all_systems_documented.

### 44.2 Matriz de completitud y aplicabilidad

| Control | Aplicabilidad | Ausente/pendiente/sin fundamento | Negativo/contradicción |
| --- | --- | --- | --- |
| Textos generales, scope y route | Siempre | incompleto | Finalidad/rol/ruta/alcance incoherente: revisión |
| Análisis y respuesta de identificación única | Siempre | incompleto | No fundada: revisión de declaración/clasificación |
| systems y cobertura | Siempre | Lista vacía, análisis/respuesta ausente: incompleto | all_systems_documented no: revisión |
| Textos de cada sistema | Cada registro aportado | Campo vacío: incompleto con índice numérico | Referencia duplicada: revisión |
| Cuatro respuestas informativas por sistema | Cada sistema | Ausente/pendiente/fundamento vacío: incompleto | No fundada: revisión |
| Evidencia general y por sistema | Siempre/cada sistema | Lista vacía o tipo/referencia vacío: incompleto | Metadata no verifica contenido externamente |
| Checklist general y sensible expreso | Primera ruta | Propagar incompleto | Propagar revisión, incluida representación |
| Rutas o regímenes concurrentes sin soporte | Si detectados | Mantener motivos propios | No quedan preparados por este expediente |

Los cuatro requisitos por sistema siempre aplican. No introducir no_aplicable
por falta de información ni suprimir un requisito por modalidad biométrica.
El primer contrato no contiene condicionales factuales adicionales: cesión,
muestras, restricciones de salud y EIPD conservan expedientes/controles propios.
Motivos estables con field por systems.<índice>.<campo>, question_id conservado
para dependencias; ordenar índices numéricamente. Precedencia incompleto >
requiere_revision > completo. No mutar contratos, snapshots ni documentos.

### 44.3 Coherencia, asociación y persistencia previstas

Evaluador puro evaluate_biometric_assessment_v1(document, snapshot, special,
consent, sensitive_consent), revalidando contratos cerrados. Rol responsable;
declaración biometricos_identificacion_unica si y condición biometricos_art16ter
por consentimiento con uses_consent_assessment true. sensitive_condition_id
permanece exclusivo del régimen sensibles_art16; no extenderlo a biometría.
Condición sensible consentimiento_expreso_art16 y expediente sensible preparados
siguen dependencias propias. No inferir biometría desde flags/nombres de categorías.

Scopes biométrico/declaración/condición no vacíos, semánticamente únicos,
coincidentes y válidos en RAT; categorías seleccionadas sensibles. Primera
cobertura conservadora: todas las categorías sensibles y todos los grupos del
alcance evaluado, coherente con consentimiento sensible. Cobertura parcial por
pares sigue pendiente dentro del alcance integral, sin inferencia desde prosa.
Documento biométrico sin detección produce revisión residual; declaración y
expediente sin clasificación sensible coherente no corrigen M2 automáticamente.

Persistencia prevista: biometric_assessment JSONB nullable/none_as_null, check
objeto, exposición CREATE/PATCH/GET; omisión preserva y null borra solo borrador.
Objeto reemplazado entero. Migración nueva append-only, head actual e28a0c3f6d97.
Asociaciones futuras especiales v9 y EIPD v10 incorporarán documento biométrico
final; mantener versiones históricas y hash RAT. Documento no nulo con asociación
anterior: asociacion_biometria_no_cubierta. GET nunca reasocia automáticamente.

Readiness biometric nullable; gate futuro biometria_no_preparada 400 incompleto/
409 revisión, respetando barreras concurrentes. EIPD debe evaluar preparación de
ruta por consentimiento y conservar positivos/pendientes; nunca deducir excepción
por base art13. Hasta integración completa, detector mantiene
validador_no_implementado en biometría, incluso si existe expediente preparado.

### 44.4 Secuencia y aceptación

1. Schema auxiliar/principal y pruebas de contratos, parciales, extra forbid,
   schema_version, respuestas y alcance; sin persistencia ni gate.
2. Migración/persistencia/API/asociaciones históricas, SQL NULL y objeto; RLS,
   exposición cerrada, rechazo de edición de confirmado, obsolescencia/reaporte.
3. Evaluador puro/readiness: cada campo faltante, respuesta no/pendiente,
   duplicados, scopes, representación, dependencias y ausencia de mutación.
4. Gate/EIPD compartido y HTTP: preparado, reparación, positivos EIPD, asociación
   obsoleta, rechazo que conserva vigente, reemplazo y protección histórica.
5. Concurrencia/rollback con PostgreSQL y constructor RAT real en alcance
   explícito; revalidar tras espera. Luego continuar rutas/regímenes pendientes
   del alcance integral; este bloque no habilita excepciones biométricas.

Solo documentación. Última suite 1429 passed y Alembic check aprobado (§41),
no reejecutados. Sin migración nueva ni commit. M3-T1 EN PROGRESO.
Próximo: implementar schemas BiometricSystemV1/BiometricAssessmentV1 y pruebas.


## 45. Schemas biométricos y pruebas implementados

Añadidos BiometricSystemV1/BiometricAssessmentV1 cerrados extra forbid según §44,
route inicial consentimiento_expreso y schema_version 1. Textos/respuestas/scope
nullable y listas independientes admiten borradores parciales. Se reutilizan
SpecialScopeV1, ContractResponseV1 y ContractEvidenceV1, sin alterar sus contratos.
Sistemas conservan orden y referencias tal como aportadas: duplicados semánticos
quedan para revisión del futuro evaluador, no se eliminan en schema.

53 casos biométricos nuevos: respuestas si/no/pendiente en campos generales y
por sistema, parciales, listas independientes, serialización/roundtrip/fechas,
rechazo de campos extra, aprobación calculada, versiones/rutas no soportadas,
no_aplica, alcance inválido y evidencia inválida. Rechazo de claves template,
embedding/fingerprint; no equivale a inspeccionar datos crudos incluidos en prosa.

Validación seleccionada con contratos licitud/sensible/salud: 150 passed.
Black/Ruff/whitespace correctos. Última suite integral anterior: 1429 passed (§41),
no reejecutada para este cambio aislado de contratos. Sin migración nueva ni commit.
No se incorpora aún biometric_assessment a CREATE/PATCH/GET ni a asociaciones:
biometría sigue bloqueada por validador_no_implementado.

M3-T1 EN PROGRESO, alcance integral. Próximo paso: persistencia/exposición del
expediente biométrico y asociaciones especiales v9/EIPD v10 compatibles;
mantener bloqueo hasta evaluador/gate y conservar pendientes del alcance integral.


## 46. Persistencia biométrica y asociaciones compatibles

biometric_assessment JSONB nullable con none_as_null/check objeto, modelos y
CREATE/PATCH/GET cerrados. Migración append-only f39b1d4e7a08 desde e28a0c3f6d97,
aplicada localmente; Alembic check global aprobado. Omisión conserva expediente,
null borra SQL NULL en borrador, PATCH reemplaza objeto completo.

Escrituras nuevas: especiales v9/EIPD v10 incluyen documento biométrico final.
Constructores/comparadores históricos especiales v1–v8/EIPD v1–v9 conservados.
Documento no nulo con asociación anterior: asociacion_biometria_no_cubierta;
documento ausente permite comparación histórica. GET no reasocia ni reescribe.
Cambio sin reaporte vuelve ambas asociaciones obsoletas; guardar controles usa
el estado final de documentos. Hash RAT sin cambios.

Diez casos HTTP nuevos: nueve pares históricos (1/1, 1/2, 2/3, 3/4, 4/5, 5/6,
6/7, 7/8, 8/9) y régimen biométrico declarado. Serialización/fechas, scopes y
contratos inválidos 422, organización ajena 403, omisión/preservación, sustitución,
obsolescencia/reaporte, residual 409, check DB rechaza array y SQL NULL. GET/POST
coherentes, rechazo conserva borrador. El caso declarado conserva
validador_no_implementado; dependencia sensible ausente mantiene precedencia
incompleta/400. Eliminado residual y reaportados controles, confirma ruta ordinaria;
confirmado rechaza PATCH biométrico tanto objeto como null sin alterar histórico.

Suite integral: 1492 passed en 150.93s. Ampliación final de aserciones de protección
verificada después con diez casos focalizados aprobados (sin cambios posteriores
de implementación). Black/Ruff/whitespace correctos. Sin commit.
M3-T1 EN PROGRESO, alcance integral. Biometría todavía sin evaluador ni gate
habilitado; persistir no autoriza el régimen. Próximo: evaluador puro y readiness
biométrico, manteniendo bloqueo hasta integrar confirmación/EIPD.


## 47. Evaluador puro y preparación biométrica

Implementado evaluate_biometric_assessment_v1 con resultado incompleto /
requiere_revision / completo, motivos inmutables y aplicabilidad. Revalida
contratos, preserva dependencias sensibles/checklist y question_id, verifica
textos/respuestas/evidencia generales y por sistema, declaración y condición,
rol/finalidad, alcances coincidentes y cobertura conservadora. Referencias de
sistema duplicadas por canonización generan revisión; orden numérico de índices.
Finalidad específica se documenta mediante análisis, sin exigir igualdad literal
con RAT ni comparar períodos en prosa como una autorización automática.

Readiness agrega biometric nullable cuando hay expediente o régimen detectado.
Gate compartido agrega biometria_no_preparada si no completo, 400 incompleto/
409 revisión, respetando otras barreras. Preparación completa no habilita POST:
detector biométrico conserva validador_no_implementado y EIPD se mantiene sin
integración biométrica de preparación. No cambia hash ni asociaciones existentes.

73 pruebas puras nuevas: campos generales/por sistema, respuestas no/pendiente,
fundamento ausente, dependencias, rutas/declaración/alcance/representación,
evidencia, sistemas múltiples, duplicados semánticos, orden numérico,
modelos mutados y ausencia de mutación. Un caso HTTP nuevo: completo aún rechaza,
respuesta pendiente/obsolescencia/reaporte, motivos GET/POST, conservación del
borrador, reparación y borrado que vuelve preparación incompleta. Diez casos
HTTP de persistencia anteriores también aprobados en validación integral.

Suite completa posterior: 1566 passed en 154.38s. Black/Ruff/whitespace y Alembic
check correctos. Sin migración nueva ni commit. M3-T1 EN PROGRESO, alcance integral.
Próximo: integrar preparación biométrica en detector/gate y EIPD, conservando
regímenes concurrentes bloqueados, asociaciones y restricciones de primera ruta.
Luego HTTP/concurrencia con RAT real y las excepciones pendientes del alcance.


## 48. Gate biométrico y contraste EIPD integrados

Detector admite biometricos_art16ter por consentimiento cuando el evaluador
biométrico resulta completo. Motivos generales/por sistema y dependencias se
propagan conservando question_id; regímenes detectados no se eliminan. Otras
rutas mantienen validador_no_implementado. Scopes, titular, responsable y
consentimiento sensible preparado conservan límites del primer soporte.

EIPD contrasta preparación de la propuesta biométrica por consentimiento:
no completa agrega ruta_especial_pendiente. Excepciones conservan
excepcion_especial_no_validada; una base art13 no aprueba esa ruta. Positivos/
pendientes EIPD y asociaciones obsoletas siguen bloqueando. Gate compartido
biometria_no_preparada permanece, y confirmación relee después de lock.

Diecinueve pruebas transversales nuevas: preparación conjunta sensible/biométrica
sin mutación, cinco positivos EIPD, expediente ausente/pendiente/obsoleto,
excepción, sensible/checklist ausente y representación; otros seis indicadores
especiales no quedan preparados por el expediente biométrico. Módulos biometría/
salud: 176 passed. Once casos HTTP biométricos aprobados. Caso completo actualizado
ahora confirma, nuevo borrador pendiente/obsoleto rechaza conservando vigente,
borrado impide preparación, EIPD positivo impide reemplazo, reparación/reaporte
con screening negativo permite reemplazo y confirmado rechaza PATCH posterior.

Suite integral posterior: 1585 passed en 155.13s. Black/Ruff/whitespace y Alembic
check aprobados; head f39b1d4e7a08. Sin migración nueva ni commit.
M3-T1 EN PROGRESO, alcance integral. Evidencia HTTP biométrica nueva usa base
consentimiento_art12. Próximo: ampliar HTTP a las seis bases ordinarias y
concurrencia biométrica con constructor RAT real; no extrapolar esta cobertura.
Excepciones biométricas y otros pendientes integrales conservan trabajo propio.


## 49. Biometría en seis bases y concurrencia con RAT real

Seis casos HTTP nuevos, test_api_biometric_confirmation_six_bases: preparación
biométrica/sensible por consentimiento y base general correspondiente; las seis
bases ordinarias conservan su expediente propio. LIA documenta régimen especial
y fuente titular en M2. Comprueba expediente biométrico pendiente/borrado,
asociaciones obsoletas y reaporte, EIPD positivo, confirmación/reemplazo,
protección posterior y rechazo con conservación íntegra de borrador y confirmado.
Una base art13 no sustituye consentimiento de esta ruta biométrica.

Dieciséis casos nuevos, test_biometric_confirmation_concurrent_real_rat_joint:
biometría/sensible/salud/geolocalización preparados, consentimiento_art12 y
constructor RAT real, PostgreSQL/app_user/RLS. Dos conexiones; segunda sesión
precarga borrador y se observa espera mediante pg_blocking_pids. Commit de primera
confirmación rechaza segunda; rollback permite segunda. Cambio pendiente de cada
uno de los cuatro expedientes o cambio de sensibilidad RAT durante espera se
relee y rechaza. Se conserva un único confirmado y documentos históricos,
snapshot/hash/fecha, sin reasociarlos ni reemplazarlos al rechazar.

Validación focalizada: módulo de concurrencia 41 passed y HTTP biométrico
17 passed, 58 verificaciones en total, incluidas 22 nuevas. Black/Ruff/whitespace
correctos. Este paso solo agrega pruebas/documentación; suite integral anterior
1585 passed (§48), no reejecutada; no presentar 1607 como suite ejecutada.
Sin cambios de implementación, migración nueva ni commit.

Límite de evidencia: HTTP con seis bases; concurrencia biométrica con RAT real
solo consentimiento_art12 y coexistencia preparada de cuatro regímenes. No se
extrapola concurrencia biométrica de otras cinco bases ni se habilitan excepciones.
M3-T1 EN PROGRESO, alcance integral. Próximo: priorizar y diseñar la primera ruta
biométrica sin consentimiento, contrastando la remisión de art16ter a art16bis;
no reutilizar autorización sanitaria ni inferir excepción desde base general.
Otros pendientes integrales mantienen trabajo propio.


## 50. Primera excepción biométrica: formulación, ejercicio o defensa de derechos

Delimitación dentro del alcance integral, 2026-10-06. Se prioriza el supuesto de
art16bis inciso segundo letra d, al que remite art16ter para tratamiento biométrico
sin consentimiento. Fuente oficial revisada: Ley 21.719, artículos 16, 16bis y 16ter,
https://www.bcn.cl/leychile/navegar?idNorma=1209272 . El supuesto exige necesidad
para formulación, ejercicio o defensa de un derecho ante tribunal u órgano
administrativo. No basta elegir defensa_derechos_art13e ni reutilizar una
referencia sanitaria o una autorización sensible diferente.

### 50.1 Dependencias y límites concretos

Separar tres niveles: base ordinaria, excepción sensible art16d y excepción
biométrica art16ter por remisión art16bis(d). La excepción sensible de defensa aún
carece de validador; será dependencia a implementar, no una aprobación implícita.
No exigir consentimiento sensible/checklist como prerrequisito de esta ruta sin
consentimiento. Las seis bases mantienen validación propia; primer caso HTTP
priorizado utilizará defensa_derechos_art13e por coherencia, sin hacerla condición
jurídica universal ni habilitar otras combinaciones sin evaluar su expediente.

RightsDefenseAssessmentV1 es de base ordinaria y acepta forum_type organo_publico.
La excepción concreta se delimitará a tribunal_justicia/organo_administrativo;
no equiparar cualquier órgano público a administrativo ni inferirlo desde nombre.
Puede reaprovecharse estructura conceptual de necesidad/derecho, pero no tratar
su resultado completo como validación automática de las excepciones especiales.

Sin consentimiento explícitamente elegido en condición biométrica y sensible:
authorization_route excepcion_legal, uses_consent_assessment false.
sensitive_condition_id defensa_derechos_art16d solo en condición sensibles_art16;
no reutilizar ese campo en biometría. Identificación de la excepción biométrica
se documentará en su contrato propio/versionado, con remisión concreta a art16bis(d).

Expedientes previstos separados: SensitiveRightsExceptionAssessmentV1 y
BiometricRightsExceptionAssessmentV1, sin cambiar semántica de
SensitiveConsentAssessmentV1 ni BiometricAssessmentV1 de consentimiento.
Contrato/campos/JSONB/asociaciones todavía por fijar en siguiente paso; documento
consentimiento residual o rutas mezcladas requerirán revisión, sin borrado automático.

El expediente debe cubrir derecho/fundamento/titular por metadata, vínculo con
datos/operaciones, necesidad, minimización, foro y etapa/referencia, finalidad y
alcance explícito, identificación biométrica/sistemas, evidencia y principios.
Cobertura conservadora inicial coincidente con RAT y las declaraciones; soporte
granular permanece pendiente. Sin plantillas, grabaciones, huellas ni documentos
procesales íntegros en metadata. Representación, menores, investigación, salud y
otros regímenes concurrentes conservan validadores/límites propios.

El aviso de sistema/finalidad/período/derechos está implementado para la ruta
con consentimiento. Antes de diseñar sus condicionales en excepción se delimitará
expresamente la política de información aplicable; no deducir desde la remisión
que todos los campos son dispensables, ni presentar una decisión conservadora
de producto como requisito textual inequívoco de la excepción.

### 50.2 Barrera EIPD y resultado que puede entregarse

El screening existente incluye datos_protegidos_excepcion_consentimiento.
Declarar una excepción real debe conservar la respuesta correspondiente y los
motivos de EIPD; no marcar no artificialmente para confirmar. Positivo exige EIPD
y permanece bloqueado en el flujo actual. Expediente especial documentalmente
preparado no equivale a screening negativo ni a EIPD aprobada.

Primera implementación podrá preparar y exponer esta excepción, pero no prometer
confirmación cuando EIPD la bloquea. Workflow completo EIPD mantiene diferimiento
original; habilitar confirmación tras resolución EIPD necesita diseño de ese
resultado/flujo y decisión explícita de alcance posterior. No eliminar el bloqueo
para declarar completado el régimen ni confundir preparado con confirmado.

### 50.3 Secuencia de siguiente trabajo

1. Fijar ambos contratos independientes y matriz: completitud, condicionales de
   etapa, foro administrativo, principios, información, residualidad, scopes,
   dependencia sensible y resultado EIPD conservado.
2. Schema/pruebas, persistencia/asociaciones históricas y evaluadores puros.
3. Integración de preparación/detección/EIPD; positivos mantienen bloqueo,
   HTTP demuestra motivos coherentes y conservación íntegra del vigente.
4. Diseñar la resolución de la dependencia EIPD antes de habilitar confirmación
   de excepción; no marcar DONE por preparación documental aislada.

Otras excepciones biométricas permanecen pendientes, no diferidas del alcance
integral. Solo documentación/delimitación: última suite integral anterior
1585 passed (§48), 58 verificaciones focalizadas posteriores (§49). No pruebas
reejecutadas, cambios de código, migración ni commit. M3-T1 EN PROGRESO.
Próximo: contrato/matriz de excepción sensible y biométrica de derechos.


## 51. Contratos y matriz de excepciones de derechos

Diseño documental, 2026-10-06. Continúa §50 dentro del alcance integral.
Fuente oficial: https://www.bcn.cl/leychile/navegar?idNorma=1209272 , arts16(d),
16bis inciso segundo(d), 16ter y 14ter. La excepción se documenta separadamente
de base ordinaria y consentimiento. Las estructuras/pruebas y la política
conservadora de información siguientes son decisiones de producto; no constituyen
una interpretación automática ni atribuyen al texto una obligación adicional.

### 51.1 Contexto común, sin aprobar una base ordinaria

RightsExceptionContextV1: extra forbid; textos/enums/respuestas nullable;
evidence list ContractEvidenceV1 con default_factory. No schema propio dentro del
contexto anidado; el documento raíz tiene schema_version Literal[1] = 1.

| Campo | Tipo | Requisito de preparación |
| --- | --- | --- |
| context_reference | str nullable | Referencia documental del caso, sin identificación personal |
| purpose_description | str nullable | Finalidad RAT por canonización v1 |
| route | Literal formulacion_derecho / ejercicio_derecho / defensa_derecho nullable | Actividad relativa al derecho |
| right_description | str nullable | Derecho concreto |
| right_basis_reference | str nullable | Fundamento del derecho; no exigir que todo derecho nazca de una norma con URL |
| right_holder | Literal responsable / tercero / ambos nullable | Vinculación documental |
| holder_connection_analysis | str nullable | Conexión de titulares/datos con derecho |
| forum_type | Literal tribunal_justicia / organo_administrativo nullable | Foro específico de excepción |
| forum_description | str nullable | Identificación del foro por metadata |
| proceeding_stage | Literal preparacion / en_curso / finalizado nullable | Etapa factual |
| proceeding_reference | str nullable | Referencia documental de actuación/caso, también en preparación |
| preparatory_actions | str nullable | Condicional de etapa preparacion |
| processing_operations | str nullable | Operaciones que la excepción cubre |
| necessity_analysis | str nullable | Necesidad específica para el derecho |
| data_minimization_analysis | str nullable | Datos/operaciones limitados |
| safeguards_analysis | str nullable | Medidas/principios aplicados al alcance |
| related_to_right | ContractResponseV1 nullable | Conexión fundada |
| necessary_for_route | ContractResponseV1 nullable | Necesidad fundada |
| within_forum_scope | ContractResponseV1 nullable | Foro fundado, no deducido de su nombre |
| principles_addressed | ContractResponseV1 nullable | Declaración fundada de medidas/principios, no certificación jurídica |
| post_proceeding_necessity_analysis | str nullable | Condicional de etapa finalizado |
| evidence | list ContractEvidenceV1 | Tipo y referencia por entrada |

No convertir organo_publico de RightsDefenseAssessmentV1 a
organo_administrativo automáticamente. Contexto común no hereda ni modifica el
contrato ordinario; no marca necesaria una base art13e para toda excepción.
En preparacion, referencia es documental, no número de expediente judicial
obligatorio; no inventar plazos procesales ni verificaciones de causas.

### 51.2 Documentos separados

SensitiveRightsExceptionAssessmentV1: extra forbid, schema_version 1; campos:

| Campo | Tipo | Función |
| --- | --- | --- |
| exception_basis | Literal defensa_derechos_art16d nullable | Supuesto sensible explícito |
| context | RightsExceptionContextV1 nullable | Antecedentes de derechos |
| sensitive_data_description | str nullable | Metadata de categorías sensibles |
| scope | SpecialScopeV1 nullable | Alcance coincidente declarado |
| exception_application_analysis | str nullable | Aplicación del supuesto a datos/operaciones |
| exception_conditions_met | ContractResponseV1 nullable | Declaración fundada; preparación de producto |
| evidence | list ContractEvidenceV1 | Referencias propias de excepción |
| notes | str nullable | Observaciones opcionales |

BiometricRightsExceptionAssessmentV1: extra forbid, schema_version 1; campos:

| Campo | Tipo | Función |
| --- | --- | --- |
| exception_basis | Literal defensa_derechos_art16bis_d nullable | Remisión biométrica específica |
| context | RightsExceptionContextV1 nullable | Caso biométrico vinculado al sensible |
| biometric_data_description | str nullable | Metadata de identificación biométrica |
| scope | SpecialScopeV1 nullable | Alcance conservador |
| unique_identification_analysis | str nullable | Relación del tratamiento técnico con identificación única |
| unique_identification_confirmed | ContractResponseV1 nullable | Declaración fundada del régimen |
| exception_application_analysis | str nullable | Necesidad biométrica concreta, no solo necesidad genérica de datos |
| exception_conditions_met | ContractResponseV1 nullable | Declaración fundada del supuesto |
| sensitive_context_connection_analysis | str nullable | Relación entre ambos expedientes y operaciones |
| systems | list BiometricSystemV1 | Sistemas e información documental |
| systems_coverage_analysis | str nullable | Cobertura de sistemas; M2 no verifica inventario |
| all_systems_documented | ContractResponseV1 nullable | Declaración fundada de cobertura |
| evidence | list ContractEvidenceV1 | Referencias propias |
| notes | str nullable | Observaciones opcionales |

Todas las listas default_factory; context/scope/enums/respuestas/textos permiten
null en borrador. Claves approved/result/can_confirm y no_aplica rechazadas.
Referencias de evidencia pueden ser parciales en borrador; fechas son opcionales
factuales. No datos biométricos crudos ni documentos íntegros en metadata.

Política inicial de información: reutilizar BiometricSystemV1 y exigir información
de sistema, finalidad, período y derechos, con sus cuatro respuestas y evidencia,
para declarar completo el expediente de excepción. Es frontera conservadora de
producto; no declarar que el art16ter resuelve inequívocamente todos los supuestos
de información en excepciones. Una dispensa o información diferida necesita
contrato/matriz propios posteriores; no se admite no_aplica ni se omiten campos
para forzar preparación. Art14ter se considera en análisis de transparencia,
pero no se afirma que este expediente audite por sí solo todos sus deberes.

### 51.3 Matriz de completitud y aplicabilidad

| Control | Aplicabilidad | Falta/pendiente | Negativo/contradicción |
| --- | --- | --- | --- |
| Contexto, textos comunes, enums, scope y exception_basis | Siempre | incompleto | Finalidad/rol/ruta/alcance incoherente: revisión |
| Respuestas contextuales y propias | Siempre | Ausente/pendiente/fundamento vacío: incompleto | No fundada: revisión |
| preparatory_actions | Etapa preparacion | Vacío: incompleto | Texto en otra etapa: residual/revisión |
| post_proceeding_necessity_analysis | Etapa finalizado | Vacío: incompleto | Texto en otra etapa: residual/revisión |
| Etapa ausente | Condicionales sin_resolver | Etapa incompleta; no exigir condicional como si fuera aplicable | No inferir desde referencia/fechas |
| Evidencia contextual y propia | Siempre | Lista vacía o tipo/referencia vacío: incompleto | No consulta externa |
| Datos/identificación/sistemas biométricos | Documento biométrico | Campos/respuestas/lista vacíos: incompleto | No/duplicados/discordancia: revisión |
| Información de cada sistema | Cada sistema | Campos/respuestas/evidencia incompletos | No fundada: revisión; dispensa aún no soportada |
| Dependencia sensible preparada | Excepción biométrica | Propagar incompleto | Propagar revisión |
| Datos de consentimiento especial en misma ruta sin consentimiento | Si aportados | No se exigen | Residualidad/mix de rutas: revisión, sin borrar |
| Otros regímenes detectados | Cuando concurren | Mantener motivos propios | Preparación de excepción no los elimina |
| EIPD | Siempre transversal | Sin resolver/obsoleto: bloquea | Excepción real/positivo mantiene requiere_eipd y bloqueo |

Precedencia incompleto > requiere_revision > completo. Aplicabilidad derivada,
motivos ordenados por contrato y por índices numéricos, question_id conservado en
dependencias, entradas inmutables. Respuestas afirmativas no sustituyen textos
de necesidad, fundamentos y evidencia; la prosa no se evalúa como sentencia legal.

### 51.4 Vinculación, coherencia y residualidad

Evaluadores futuros: evaluate_sensitive_rights_exception_v1(document, snapshot,
special) y evaluate_biometric_rights_exception_v1(document, snapshot, special,
sensitive_exception). No dependencia del checklist ni consentimiento sensible de
ruta con consentimiento. Validar contratos aunque falte otra dependencia.

Declaraciones datos_sensibles/biometricos_identificacion_unica afirmativas;
condiciones sensibles_art16 y biometricos_art16ter por excepcion_legal,
uses_consent_assessment false explícito. sensitive_condition_id
 defensa_derechos_art16d solo sensible; biometría no agrega ese campo ni lo acepta.
Condiciones: referencia legal, análisis y evidencia completos; la referencia
textual no se interpreta como autorización. Otros exception_basis no soportados
no se aceptan por compartir texto del derecho.

Contextos sensible/biométrico vinculan context_reference, finalidad, route,
right_holder, forum_type, proceeding_stage y proceeding_reference por comparación
semántica v1 de textos y exacta de enums. Descripciones/análisis pueden reflejar
operaciones biométricas más específicas; vínculo exige análisis documentado y no
igualdad literal de toda prosa/evidencia/notas. Diferencias de vínculo: revisión.

Scopes propios/declaraciones/condiciones coincidentes, no vacíos, válidos en RAT,
semánticamente únicos; categorías sensibles y todos los grupos del alcance.
Cobertura parcial por pares sigue pendiente. No inferir biometría desde flag
sensible ni foro/edad/representación desde nombres. Rol responsable inicial.
Excepción documental sin régimen/ruta correspondiente: revisión residual.

SensitiveConsentAssessmentV1/BiometricAssessmentV1 no se convierten a excepciones.
Su presencia cuando se propone la respectiva excepción produce revisión de
expediente residual; el checklist general puede pertenecer a la base ordinaria y
no se borra automáticamente. La base ordinaria mantiene su evaluador propio.
Cuando se propone consentimiento, documentos de excepción residuales también
producen revisión. No combinar subconjuntos de rutas en este primer soporte.

### 51.5 Persistencia/asociaciones y aceptación prevista

Futuras columnas sensitive_rights_exception_assessment y
biometric_rights_exception_assessment, JSONB nullable/none_as_null/check objeto;
CREATE/PATCH/GET, omisión preserva/null borra solo borrador/reemplazo entero.
Migración append-only desde f39b1d4e7a08. Asociaciones especiales v10/EIPD v11
incorporan ambos documentos finales conservando todos los comparadores previos;
documento no cubierto produce motivos específicos por cada expediente.
No circularidad, no cambio del hash RAT ni reasociación automática durante GET.

Readiness future sensitive_rights_exception/biometric_rights_exception nullable;
completo documental no garantiza confirmación. EIPD distingue propuesta preparada
de excepción no validada, conserva respuesta afirmativa y requiere_eipd; no
inventa resultado aprobada ni aceptación externa. Sin resolución EIPD diseñada
no se confirma la excepción, aunque estén completos los dos expedientes.

Aceptar mediante pruebas: contratos parciales/cerrados y etapa/foro, todos los
campos/respuestas/evidencias faltantes, sin_resolver/residualidad de condicionales,
referencias/vínculos/scopes discordantes, sistemas múltiples/duplicados/índices,
rutas mezcladas y consentimiento ausente sin dependencia artificial. Persistencia
SQL NULL/check objeto, exposición/aislamiento, históricos/obsolescencia/reaporte.
HTTP: completo aún bloqueado por EIPD, no falso negativo para confirmar; conservar
vigente y borrador en rechazo, proteger confirmado. Resolución de EIPD y
confirmación de excepción no se declaran entregadas en esta secuencia.

Solo documentación. M3-T1 EN PROGRESO, alcance integral. Última suite integral
1585 passed (§48) y 58 verificaciones posteriores (§49), no reejecutadas aquí.
Sin cambios de código, migración ni commit. Próximo: schemas de los tres tipos y
pruebas de contrato, antes de persistencia o evaluadores.


## 52. Schemas de excepciones de derechos implementados

Añadidos RightsExceptionContextV1, SensitiveRightsExceptionAssessmentV1 y
BiometricRightsExceptionAssessmentV1 según §51. Contratos extra forbid,
contexto/alcance/textos/enums/respuestas nullable, listas independientes y
schema_version 1 en documentos raíz. Foro especial admite tribunal_justicia y
organo_administrativo; no amplía ni convierte RightsDefenseAssessmentV1 ordinario.
Bases especiales diferenciadas: defensa_derechos_art16d y
defensa_derechos_art16bis_d. Biometría reutiliza BiometricSystemV1.

102 casos nuevos: parciales, listas independientes, enums, respuestas si/no/
pendiente, serialización/roundtrip/fechas, contexto anidado, alcance, evidencia,
campos extra/aprobaciones calculadas/no_aplica, sistemas y separación de rutas.
Condicionales de etapa y duplicados semánticos se conservan en borrador para el
futuro evaluador; schema no declara preparación ni aprobación EIPD.

Validación seleccionada de contratos nuevos y licitud/sensible/salud/biometría:
252 passed. Black/Ruff/whitespace correctos. Última suite integral anterior:
1585 passed (§48), no reejecutada para este cambio aislado de contratos.
No persistencia/API/asociaciones, evaluador ni habilitación de excepciones todavía.
Sin migración nueva ni commit. M3-T1 EN PROGRESO, alcance integral.
Próximo: persistencia/exposición de ambos expedientes y asociaciones especiales
v10/EIPD v11 compatibles; mantener positivo EIPD y rutas pendientes bloqueadas.


## 53. Persistencia y API de excepciones de derechos

Implementados los dos expedientes nullable en LegalAssessment y CREATE/PATCH/GET.
JSONB con SQL NULL y constraints de objeto; migracion append-only a40c2e5f8b19
aplicada desde f39b1d4e7a08. Alembic check sin diferencias nuevas.
PATCH conserva por omision, reemplaza el documento entero y permite null solo
sobre borrador; confirmado permanece protegido. Fechas serializadas en JSON.

Tres casos HTTP (sensible, biometrico, ambos) verifican almacenamiento, omision,
reemplazo, borrado/SQL NULL, contratos invalidos y constraint de objeto,
aislamiento entre organizaciones y proteccion de confirmado. GET/POST comparten
asociacion_excepcion_derechos_no_cubierta: cualquier documento presente bloquea
confirmacion con 409 y preserva integramente borrador y vigente. El caso positivo
tras borrar documentos valida la ruta ordinaria, no una excepcion.

Las asociaciones siguen especiales v9/EIPD v10: los nuevos expedientes todavia
no forman parte de sus hashes. La barrera explicita impide confirmar aunque esas
asociaciones anteriores parezcan vigentes. No hay reasociacion automatica ni
cambio del hash RAT. Proximo paso: especiales v10/EIPD v11 con ambos documentos
y comparadores historicos; despues, evaluadores propios de completitud.
Preparacion documental no habilita excepciones sin resolver la dependencia EIPD.

Black/Ruff/whitespace correctos; tres pruebas focalizadas aprobadas. Regresion
integral: 1712 passed en 169.95 segundos. M3-T1 EN PROGRESO, alcance integral; sin commit.


## 54. Asociaciones de excepciones: especiales v10 y EIPD v11

Los constructores nuevos incorporan sensitive_rights_exception_assessment y
biometric_rights_exception_assessment al material final de hash. CREATE y PATCH
con controles aportados usan especiales v10/EIPD v11, despues de aplicar cambios
al documento; EIPD incluye la asociacion especial final, sin circularidad.
Hash RAT canonico v1 y migraciones sin cambios. Head local a40c2e5f8b19.

Comparadores anteriores se conservan: especiales v1-v9 y EIPD v1-v10 siguen
vigentes si ambos documentos estan ausentes y el resto del contexto coincide.
Un documento presente, incluso {}, produce motivo especifico por expediente
si la version historica no lo cubre: asociacion_excepcion_sensible_no_cubierta o
asociacion_excepcion_biometrica_no_cubierta. Ambos motivos aparecen cuando
corresponde. Las versiones nuevas revalidan los contratos de excepcion.

Alta, edicion y borrado de documentos invalidan asociaciones previas sin
reescribirlas; GET/readiness no mutan ni reasocian. Reaportar solo condiciones
especiales no actualiza EIPD: hace falta aportar cada control. Asociacion actual
no implica completitud ni autorizacion; barrera compartida GET/POST
excepcion_derechos_no_preparada mantiene 409 por cada documento presente
mientras faltan evaluadores propios. Se sustituye el motivo provisional §53 de
falta de cobertura por este motivo de preparacion, sin habilitar excepciones.

96 casos nuevos de servicios: 76 historicos (19 versiones x cuatro presencias),
cuatro de versiones actuales, catorce mutaciones y dos equivalencias/revalidacion
Pydantic/JSON. 22 casos HTTP nuevos: 19 historicos y tres de mutacion/reaporte,
con preservacion integra del borrador y vigente ante rechazo. Tres HTTP de
persistencia existentes ampliados para borrado obsoleto y reaporte ordinario.
Respuesta EIPD afirmativa se conserva; sin condicion especial documentada da
pendiente_revision/excepcion_consentimiento_no_documentada y sigue bloqueada.
No se acredita que una excepcion real pueda confirmarse ni se altera el screening.

Formato/lint/whitespace verificados. Regresion integral: 1830 passed en 184.29 s.
Proximo: evaluador de completitud/aplicabilidad de excepcion sensible de derechos,
seguido del biometrico y sus vinculos. Resolucion EIPD sigue pendiente de diseno.
M3-T1 EN PROGRESO, alcance integral; sin migracion nueva ni commit.


## 55. Evaluador puro de excepcion sensible de derechos

Implementado evaluate_sensitive_rights_exception_v1(document, snapshot, special)
en backend/app/services/sensitive_rights_exception.py. Resultado inmutable:
incompleto/requiere_revision/completo, motivos con field/code/category/question_id
y aplicabilidad aplicable/no_aplicable/sin_resolver. can_confirm significa solo
preparacion documental, no autorizacion ni superacion de EIPD. No dependencia
artificial del checklist de consentimiento ni de la base ordinaria art13e.
Referencia oficial reconsultada: https://www.bcn.cl/leychile/navegar?idNorma=1209272,
art16(d); controles de producto segun matriz §51, sin certificacion juridica.

Contexto exige textos de derecho/operaciones/necesidad/minimizacion/salvaguardas,
fundamento del derecho sin URL normativa obligatoria, enums, respuestas fundadas
y evidencia. preparatory_actions solo en preparacion, analisis posterior solo en
finalizado; prosa residual en otra etapa requiere revision. Etapa ausente deja
ambos condicionales sin_resolver, sin inferir desde prosa ni exigirlos como
aplicables. Declaraciones afirmativas no sustituyen analisis ni evidencia.

Rol responsable inicial, finalidad por canonizacion v1, coherencia sensible del
RAT. Declaracion datos_sensibles afirmativa/fundada, condicion sensibles_art16 por
excepcion_legal, ID defensa_derechos_art16d y uses_consent_assessment false
explicito. Campos ausentes incompletos; rutas/negativos incoherentes revision.
Referencia/analisis/evidencia de condicion obligatorios, sin consulta externa.
Scopes propios/declaracion/condicion semanticamente unicos, coincidentes y
cubriendo todas las categorias sensibles y grupos del RAT. No autoriza cobertura
parcial por pares ni convierte organo_publico en organo_administrativo.

172 pruebas nuevas aprobadas: rutas/foros/etapas/titulares, textos/enums/respuestas,
condicionales/residualidad, evidencia, alcance parcial/duplicados/invalido,
canonizacion/Unicode, ausencias/contradicciones, revalidacion de modelos mutados
incluso con otra dependencia ausente, equivalencia JSON/fechas, orden numerico,
prioridad incompleto e inmutabilidad. Dos verificaciones transversales demuestran
que completo puro conserva bloqueo de excepcion y EIPD con respuesta no o si;
positivo se conserva y excepcion_especial_no_validada mantiene pendiente_revision.
Formato/lint/whitespace correctos. Ultima suite integral anterior: 1830 passed
(§54), no reejecutada para este evaluador aislado todavia no conectado a la API.

No modifica asociaciones/migracion ni habilita confirmacion. Falta exponer su
readiness e integrar el evaluador en detector/gates compartidos, incluyendo
residualidad del expediente de consentimiento sensible; despues evaluador
biometrico y vinculos. Resolucion EIPD sigue pendiente de diseno. M3-T1 EN
PROGRESO, alcance integral; sin commit.


## 56. Integracion de excepcion sensible en readiness y barreras

API readiness expone sensitive_rights_exception nullable: se evalua si hay
documento o condicion sensible que propone excepcion_legal/defensa_derechos_art16d.
Una propuesta sin documento produce expediente_ausente; un contexto sensible sin
propuesta de excepcion no crea un expediente por inferencia. Resultado de lectura
orientativo, inmutable; no reasocia ni modifica documentos/estado.

Detector especial integra el evaluador para sensibles_art16/excepcion_legal/
defensa_derechos_art16d y propaga field/code/category/question_id, conservando
rutas restantes como no implementadas. Completo documental puede dar
regimenes_preparados, sin aprobar la excepcion juridica ni habilitar confirmacion.
La barrera compartida GET/POST usa excepcion_derechos_no_preparada para faltas
sensibles: 400 incompleto, 409 revision. Otros controles pueden elevar el rechazo
a 409; EIPD real sigue en pendiente_revision por excepcion_especial_no_validada.
El expediente biometrico conserva la barrera provisional hasta su evaluador.

Consentimiento sensible presente con ruta excepcion_legal produce
expediente_consentimiento_sensible_residual. Expediente de excepcion sensible
sin regimen o ruta correspondiente produce expediente_excepcion_sensible_residual,
incluida propuesta por consentimiento. No se borran ni convierten documentos;
checklist general puede pertenecer a la base ordinaria y conserva evaluador propio.
Asociaciones especiales v10/EIPD v11 y hash RAT sin cambios.

Doce pruebas nuevas: seis de barrera/propagacion en servicios y seis HTTP sobre
las bases ordinarias con RAT real. HTTP verifica complete/incomplete/ausente,
lectura nullable, aislamiento, motivos compartidos, documento obsoleto/reaporte,
residualidad en ambos sentidos, positivo EIPD conservado, falso negativo
excepcion_consentimiento_discordante, revalidacion del RAT y preservacion integra
de borrador/vigente ante rechazo. No confirma una excepcion ni extrapola
concurrencia a esta nueva ruta. 209 verificaciones focalizadas aprobadas, mas
seis HTTP reejecutadas con escenarios de residualidad inversa/EIPD discordante.

Formato/lint/whitespace correctos. Regresion integral: 2014 passed en 199.23 s.
Proximo: evaluador puro biometrico de derechos y vinculos con el sensible,
seguido de integracion propia. Resolucion EIPD permanece pendiente de diseno;
no alterar screening para eludirla. Head local a40c2e5f8b19, sin migracion nueva
ni commit. M3-T1 EN PROGRESO, alcance integral.


## 57. Evaluador puro biometrico de derechos y vinculos sensibles

Implementado evaluate_biometric_rights_exception_v1(document, snapshot, special,
sensitive_exception) en backend/app/services/biometric_rights_exception.py.
Resultado inmutable incompleto/requiere_revision/completo, motivos ordenados por
contrato/indices numericos y aplicabilidad derivada. can_confirm significa solo
preparacion documental; no habilita tratamiento ni supera controles EIPD.
Sin dependencia artificial de consentimiento ni de una base ordinaria art13e.

Propaga preparacion sensible con field/code/category/question_id y aplicabilidad,
con prefijo sensible donde corresponde. Valida contratos aun cuando otra
dependencia falte. Contexto biometrico exige derecho/operaciones/necesidad,
minimizacion/salvaguardas, foro y etapa, evidencia y respuestas fundadas; mismos
condicionales de preparacion/finalizado, etapa ausente sin_resolver y textos
residuales en otra etapa requieren revision. Vincula context_reference,
purpose_description y proceeding_reference por canonizacion v1; route,
right_holder, forum_type y proceeding_stage por igualdad de enums. No compara
toda prosa ni evidencia literalmente: analisis biometrico puede ser especifico.
Analisis de conexion entre ambos expedientes obligatorio.

Declaracion biometricos_identificacion_unica afirmativa/fundada; condicion
biometricos_art16ter por excepcion_legal y uses_consent_assessment false explicito.
Documento exception_basis defensa_derechos_art16bis_d; no agrega ID sensible a
condicion biometrica. Referencia/analisis/evidencia de condicion requeridos.
Scope completo de categorias sensibles y grupos del RAT, coincidente con
expediente/declaracion/condicion y sensible; cobertura parcial por pares pendiente.

Exige identificacion unica documentada, descripcion biometrica, aplicacion de la
excepcion, lista de sistemas, declaracion/analisis de cobertura y evidencia.
Cada sistema requiere diez textos, cuatro respuestas fundadas y evidencia;
referencias de sistema duplicadas semanticamente producen revision. Inventario
M2 no se verifica automaticamente. Politica conservadora de informacion de §51:
no implica afirmar una obligacion universal ni soporta dispensa/no_aplica.

208 pruebas nuevas aprobadas: campos/respuestas/enums/etapas, siete vinculos,
canonizacion/Unicode/prosa especifica, dependencia sensible/motivos/aplicabilidad,
evidencia, scopes completos/invalidos/duplicados/discordantes, condicion/declaracion,
sistemas multiples y numeracion, revalidacion de modelos mutados incluso con
otra dependencia ausente, equivalencia JSON/fechas e inmutabilidad/preferencia
incompleto. Dos verificaciones transversales acreditan que completo puro sigue
bloqueado por detector/gates actuales y EIPD; positivo permanece afirmativo.

Formato/lint/whitespace correctos. Ultima suite integral anterior: 2014 passed
(§56), no reejecutada para este evaluador aislado todavia no conectado a la API.
Sin cambios de contratos/asociaciones/migraciones ni habilitacion de confirmacion.
Proximo: readiness nullable e integracion biometrica en detector/gates con
residualidad de consentimiento/excepcion, manteniendo evaluador de cada ruta y
barrera EIPD. M3-T1 EN PROGRESO, alcance integral; sin commit.


## 58. Integracion biometrica de derechos en readiness y barreras

API readiness expone biometric_rights_exception nullable: evalua documento
presente o propuesta biometricos_art16ter/excepcion_legal, incluso sin documento.
Detector integra el evaluador biometrico y propaga motivos propios y dependencia
sensible con field/code/category/question_id. Campos faltantes producen barrera
compartida excepcion_derechos_no_preparada (400 incompleto, 409 revision).
GET y POST usan las mismas reglas; lectura no escribe, confirma ni reasocia.

Seleccion explicita de rutas: biometric_assessment por consentimiento se evalua
cuando se aporta o cuando el regimen detectado no propone excepcion_legal;
la excepcion sin documento de consentimiento no adquiere dependencia artificial.
Un documento de consentimiento aportado en ruta excepcion genera
expediente_biometria_residual; documento de excepcion en otra ruta/sin regimen
genera expediente_excepcion_biometrica_residual. No se convierten ni borran datos.
Rutas restantes y otros regimenes conservan evaluadores/barreras propios.

Ambas excepciones documentalmente completas pueden dar regimenes_preparados.
EIPD conserva pendiente_revision/excepcion_especial_no_validada: asociaciones
actuales y documentos completos no autorizan la excepcion ni habilitan
confirmacion. Positivo no se cambia, negativo discordante tampoco elimina bloqueo.
Especiales v10/EIPD v11, hash RAT y head local a40c2e5f8b19 sin cambios.

Doce casos nuevos: seis de categorias/propagacion en servicios y seis HTTP sobre
bases ordinarias con RAT real. HTTP verifica readiness nullable, preparacion
completa sin consentimiento especial, documento ausente/pendiente/obsoleto,
reaporte, dependencia sensible null/parcial, discordancia de caso, segundo
sistema incompleto, residualidad en ambos sentidos, EIPD positivo/negativo
discordante, cambio de RAT y aislamiento. Todos los rechazos conservan integro
borrador y vigente; ninguna excepcion confirmada. No extrapolar concurrencia.
251 verificaciones focalizadas aprobadas, incluidos escenarios anteriores de
excepciones/asociaciones. Formato/lint/whitespace correctos.

Regresion integral: 2234 passed en 218.12 s. Proximo: definir diseno/alcance de
resolucion EIPD para estas excepciones, con evidencia y decision trazable antes
de habilitar confirmacion; workflow completo sigue diferido segun diseno previo,
sin bypass ni aprobacion implicita. Mantener los demas pendientes funcionales del
alcance integral. Sin migracion nueva ni commit; M3-T1 EN PROGRESO.


## 59. Resolucion EIPD acotada: evaluacion externa y revision trazable

Paso documental, 2026-10-06. Continua §58 dentro del alcance integral, sin
habilitar confirmaciones. Fuente primaria reconsultada:
https://www.bcn.cl/leychile/navegar?idNorma=1209272, art15ter: EIPD previa al
tratamiento en supuestos obligatorios, incluida excepcion de consentimiento en
datos sensibles/especialmente protegidos. Sus criterios incluyen operaciones,
finalidad, necesidad/proporcionalidad, riesgos y mitigacion. La consulta a la
Agencia para obtener recomendaciones es una posibilidad prevista en ese articulo.
La revision interna de producto descrita aqui no es una aprobacion regulatoria.

### 59.1 Frontera del primer soporte

Registrar metadata de una EIPD realizada y conservada por la organizacion fuera
de CumpleIA, su analisis estructurado y una revision humana autenticada. No basta
una referencia generica ni una casilla approved. Workflow completo de autoria,
custodia de anexos, inventario exhaustivo e intercambio con la Agencia permanece
diferido; esta secuencia implementara solo registro/revision y decision de gate.
No enviar comunicaciones externas ni usar LLM para aprobar contenido juridico.

Primera continuacion soportada: sensible art16(d), sola o junto con biometria por
art16ter/art16bis(d), con ambos evaluadores pertinentes completos, asociaciones
actuales, rol responsable, alcance integral del contexto y sin rutas mezcladas.
El screening exige datos_protegidos_excepcion_consentimiento=si fundada y las
otras cuatro respuestas no fundadas, completas y coherentes con RAT/LIA.
Otro positivo, pendiente, regimen no soportado o contradiccion conserva bloqueo;
ampliar despues con contrato/aceptacion propios, sin recortar pendientes integrales.

### 59.2 Contenido y contrato a concretar antes de codigo

EipdResolutionAssessmentV1: documento cerrado/partial en borrador, schema_version
1; null/textos/enums/respuestas opcionales hasta evaluacion, listas independientes.
Metadata, referencias y analisis solamente; sin datos personales/biometricos crudos.

| Seccion | Preparacion requerida |
| --- | --- |
| Referencia de EIPD | Identificador documental, version, fecha de finalizacion, referencia a informe y responsable de su elaboracion |
| Alcance y operaciones | Finalidad coincidente con RAT, categorias/grupos completos de la evaluacion, operaciones/contexto/tecnologia y analisis de cobertura de ambas excepciones |
| Necesidad/proporcionalidad | Analisis propios de finalidad, minimizacion y medidas; respuestas fundadas y evidencia |
| Evaluacion previa | Declaracion documentada de realizacion antes del tratamiento, con fundamento/evidencia; no inferirla de fecha de subida o confirmacion |
| Riesgos | Lista de riesgos referenciados, descripcion/impacto, valoracion inicial/residual fundada y evidencia; IDs semanticamente unicos |
| Medidas | Referencia de medida y riesgos que cubre, descripcion/eficacia/implantacion y evidencia; referencias coherentes; plan pendiente no equivale a medida implantada |
| Conclusion | Sintesis de riesgo residual, declaracion no_alto/alto/sin_resolver fundada, limites y seguimiento; no calcular umbral legal ni puntaje propio |
| Fuentes oficiales | Revision de listas/orientaciones, fuentes consultadas, fecha, referencias y analisis de aplicabilidad; estado identificado/no_identificado/pendiente documentado |
| Consulta a Agencia | Estado no_solicitada/en_curso/concluida, analisis y referencias condicionales; recomendaciones son antecedentes de revision |
| Evidencia general | Tipo y referencia completos; fechas opcionales factuales aparte de las fechas de revision/finalizacion requeridas |

Fechas/enums/condicionales exactos se fijaran en el siguiente contrato/matriz.
Sin_resolver/faltas son incompleto; negacion/discordancia son revision. Etapas y
condicionales no se deducen desde nombres o prosa. Scope EIPD cubre todas las
categorias/grupos del RAT de esta evaluacion, incluidos los no sensibles; las
excepciones mantienen sus scopes sensibles, contenidos en ese alcance, sin
forzar igualdad entre scopes de diferente funcion.

Riesgo residual alto mantiene bloqueo como frontera conservadora de producto;
no se atribuye al articulo una prohibicion general ni consulta obligatoria.
Consulta en_curso mantiene revision; concluida exige analizar antecedentes y
actualizar evaluacion/medidas cuando corresponda, sin convertir recomendaciones
en autorizacion automatica. No_solicitada no omite evaluacion ni riesgo residual.
No declarar completo solo por aportar informe o marcar todos los controles si.

### 59.3 Revision humana separada del payload

Eventos append-only EipdResolutionReview: tenant y assessment, decision
continuar/requiere_cambios/no_continuar, fundamento/referencia de revision,
hash del documento revisado y hash de contexto, actor y fecha de servidor.
Actor/fecha/tenant/hashes/estado de revision no son campos editables por el cliente.
Permiso edit_content y suscripcion vigente, coherentes con M3; permiso de app no
certifica titulacion ni juicio juridico. La revision expresa una decision humana
interna documentada y no se genera desde una conclusion LIA ni desde el LLM.

Registro de continuar exige documento completo, contexto vigente, riesgo residual
no_alto fundado y todos los controles de esta frontera superados. Requiere_cambios
/no_continuar mantienen bloqueo. Eventos historicos no se sobrescriben: editar
la EIPD o su contexto invalida la revision anterior aunque quede visible en el
historial. Confirmado/reemplazado siguen inmutables; revision nueva solo en borrador.

### 59.4 Asociaciones y transaccion

Sin cambiar hash RAT v1 ni constructores/comparadores especiales v1-v10 y EIPD
v1-v11. Context binding de resolucion v1 incluye snapshot completo, legal_basis,
consentimiento y todos los expedientes ordinarios/especiales finales, condiciones
especiales y screening finales. No incluye el propio documento de resolucion ni
sus eventos. Hash documental separado de la resolucion normalizada incluye su
context_binding y contenido, excluyendo estados/actor/historial de revision.
Revision vincula ambos hashes. No circularidad ni actualizacion automatica en GET.

Orden de escritura: aplicar borrador/documentos; asociar condiciones especiales;
asociar screening; asociar resolucion al contexto final; revision humana sobre
version/hashes concretos. Cambios en cualquiera de esas entradas vuelven obsoleto
el evento previo; reaporte documental no reproduce la decision humana.

Propuesta fisica a concretar: columna JSONB nullable/check objeto para resolucion
y tabla de eventos con organization_id, FK compuesta y RLS desde su migracion
append-only inicial. CREATE/PATCH/GET de metadata; accion separada para registrar
revision con campos de servidor. PATCH omite/preserva, null borra solo borrador,
reemplazo entero; historial permanece. Accion de revision y confirmacion bloquean
la misma serie, releen populate_existing y recomponen RAT/contexto antes de
cualquier cambio. Rechazo/rollback conserva vigente, borrador y eventos previos.

### 59.5 Screening y gate sin borrar el positivo

Mantener cuestionario/contratos/hash actuales. Evaluacion versionada v2 prevista:
solo cuando todas las excepciones declaradas pertenezcan a esta frontera y esten
preparadas, distinguir propuesta documental preparada de ruta no soportada.
La deteccion conserva requiere_eipd y sus motivos; no depende del resultado de
la revision ni se convierte en sin_supuestos_declarados. La version v1 permanece
como comparador/evaluador historico; no borrar sus motivos de snapshots anteriores.

Gate separado combina screening vigente, resolucion completa, revision humana
continuar actual y controles ordinarios/especiales. Permite continuar solo dentro
de esta frontera, con EIPD aun requerida pero documentada y revisada; nunca filtra
arbitrariamente blockers por codigo. Sin documento/revision/contexto vigente,
misma barrera actual. Residualidad: resolucion sin necesidad/propuesta soportada
requiere revision y no aprueba otras rutas. GET ofrece ambos resultados y motivos,
POST revalida iguales reglas despues del lock, antes de reemplazar confirmado.

### 59.6 Fuentes pendientes y aceptacion previa al desbloqueo

Busqueda acotada de listas/orientaciones en fuentes oficiales, 2026-10-06: se
verifico el texto legal; no se verifico una publicacion especifica de orientaciones
aplicables. Esto no acredita inexistencia. Registro de fuentes/estado queda
pendiente; antes de habilitar confirmacion deben verificarse las fuentes vigentes
y registrar su aplicabilidad/version, segun §18.21. No inventar listado ni plazo.
El contrato permite conservar esta tarea pendiente sin forzar un no negativo.

Aceptar mediante pruebas de contratos cerrados/parciales, todos los faltantes,
IDs/medidas/riesgos discordantes, etapas/fuentes/consulta sin_resolver y residualidad,
preparacion y decision separadas, campos de servidor no falsificables, hashes y
revisiones obsoletos por cada documento/RAT, aislamiento/RLS, historial inmutable,
GET sin escritura, seis bases ordinarias, positivo EIPD persistente, unsupported
positivo bloqueado, dos sesiones con RAT real y rollback sin reemplazo parcial.
Solo despues de esa evidencia y revision de fuentes habilitar la frontera concreta.

Este paso solo fija diseno; no codigo/schema/API/migracion ni habilitacion de gates.
Ultima suite integral 2234 passed (§58), no reejecutada para documentacion.
Proximo: contrato fisico/matriz de resolucion y eventos, antes de schemas.
M3-T1 EN PROGRESO, alcance integral; sin commit.


## Contratos/matriz de resolucion EIPD — 2026-10-06

Diseño §60 concreta campos/tipos, condicionales de fuentes/consulta, cobertura de
riesgos/medidas, respuestas fundadas y scopes RAT. Entrada editable separada de
binding de servidor; revision humana recibe decision/fundamento/referencia y
servidor registra hashes/actor/fecha. Historial append-only y ultimo evento sin
recuperar aprobacion anterior; preparacion, vigencia y decision independientes.
Implementacion y pruebas pendientes, incluida inmutabilidad SQL/RLS. Fuentes
oficiales pendientes antes de desbloqueo; no_identificado no prueba inexistencia.
Paso solo documental; gates conservados. Ultima suite 2234 passed (§58), sin
reejecucion. Proximo: schemas y pruebas de contrato. EN PROGRESO; sin commit.


## 61. Schemas de resolucion EIPD y revision humana

2026-10-06. Implementados contratos de §60 en schemas/licitud.py: riesgos,
medidas, fuentes oficiales, consulta y EipdResolutionAssessmentV1 editable parcial.
EipdResolutionAssessmentStoredV1 separado agrega context_binding nullable;
binding v1 cerrado/hash SHA-256 hexadecimal. No incorporar esta forma interna
como entrada CREATE/PATCH en la futura integracion.

EipdResolutionReviewIn exige decision explicita, fundamento y referencia no
blancos; rechaza metadata del servidor. ReviewOut agrega UUIDs, hashes y fecha
UTC con zona; ReviewStateOut expone estado/ultimo evento como contrato de lectura.
Schemas no autentican al actor ni producen hashes/fechas: eso corresponde al
servicio futuro bajo lock. Tampoco calculan vigencia/decision ni persistencia.

Borradores aceptan parciales/negativos/pendientes y condicionales residuales;
completitud, IDs semanticos, cobertura y contradicciones pertenecen al evaluador
pendiente, sin rechazar borrador ni asumir aprobacion. Contratos cerrados anidados,
listas independientes, fechas factuales y enums explicitos; no_aplica rechazado.

111 pruebas nuevas: metadata no falsificable, enums/fechas/hash, cierre anidado,
listas/borradores, respuestas parciales, condicionales diferidos y JSON roundtrip.
231 focalizadas aprobadas; todos los schemas: 419 passed. Black/Ruff y diff
whitespace correctos. Ultima suite integral 2234 passed (§58), no reejecutada
para contratos aislados; no sumar parciales como evidencia de suite completa.

Sin integracion API/DB, migracion, evaluador ni habilitacion de gates. Fuentes
oficiales siguen pendientes; EN PROGRESO integral, sin commit. Proximo: asociacion
/hash de resolucion v1, preservando comparadores especiales v1-v10/EIPD v1-v11;
despues persistencia/eventos/RLS/API, matriz y gate segun §60.4.


## 62. Asociacion y hash de resolucion EIPD v1

2026-10-06. Nuevo servicio puro eipd_resolution.py, sin dependencias DB/API.
EipdResolutionContextV1 interno cerrado exige explicitamente snapshot RAT completo,
legal_basis y todos los documentos ordinarios/especiales, consentimiento incluido,
condiciones especiales y screening finales. Entradas nullable deben aportarse
explicitamente; no usar defaults que permitan omitir accidentalmente un expediente.
Contexto excluye resolucion/eventos y rechaza campos extra, evitando circularidad.

build_eipd_resolution_context_hash_v1 revalida material y genera SHA-256 de JSON
normalizado (claves ordenadas, UTF-8, nulls/defaults explicitos, listas preservadas)
con binding_version=1. Incluye tambien campos del snapshot fuera del hash RAT
canonico: ese hash RAT y comparadores especiales v1-v10/EIPD v1-v11 no cambian.

bind_eipd_resolution_v1 acepta solo documento editable y devuelve forma interna
con binding de servidor. Reaporte exige entrada editable explicita; documento
almacenado/binding aportado como entrada se rechaza. No reutiliza decision humana.
build_eipd_resolution_document_hash_v1 incluye documento completo y su binding,
rechaza metadata de revision; eipd_resolution_context_is_current_v1 compara sin
mutar/asociar. Sin binding devuelve false. Schemas invalidos lanzan ValidationError;
la futura integracion debera tratarlos sin convertirlos en aprobacion.

89 pruebas nuevas: alta/baja/modificacion de cada expediente, base ordinaria,
snapshot completo, todos los inputs obligatorios, modelos/JSON/defaults/orden de
claves, contenido propio separado de contexto, lectura sin escritura, metadata
ajena/circular rechazada y revalidacion de instancias/nested modificadas.
296 focalizadas aprobadas, incluyendo 96 asociaciones historicas de excepciones
y 111 schemas EIPD. Black/Ruff y whitespace correctos. Ultima suite integral
2234 passed (§58), no reejecutada para funciones puras aisladas; no sumar este
checkpoint como nueva suite integral ni extrapolar a concurrencia/API.

Pendiente consumir estos hashes desde persistencia/revision bajo lock con RAT
real. Ninguna revision/gate habilitada; fuentes oficiales pendientes.
Proximo: persistencia JSONB y eventos append-only con RLS desde migracion inicial;
despues exposicion documental/API, evaluador y revision segun §60.4.
M3-T1 EN PROGRESO integral, sin migracion nueva ni commit en este paso.


## 63. Persistencia de resolucion EIPD e historial protegido

2026-10-06. Migracion append-only b51d3f6a9c20 posterior a a40c2e5f8b19,
aplicada en PostgreSQL local. Alembic check sin operaciones nuevas.
LegalAssessment.eipd_resolution_assessment JSONB nullable/none_as_null=True,
CHECK objeto: null SQL admitido, null JSON/listas/escalares rechazados.
UQ adicional (id, organization_id) soporta FK compuesta del historial.

EipdResolutionReview persiste UUID, tenant/assessment, decision, fundamento,
referencia, hashes SHA-256, actor FK profiles y fecha timezone con clock_timestamp.
CHECKs para decision, textos no blancos (incluidos tab/newline) y hashes; indices
por tenant y orden historico assessment/created_at/id. No relaciones ORM que
eliminen eventos por cascade. FK a assessment/tenant y organization sin ON DELETE
CASCADE: no borrar el padre para eliminar indirectamente el historial.

RLS desde creacion: SELECT solo organizaciones autenticadas; INSERT ademas exige
actor del auth.uid() y assessment propio borrador con documento presente.
No politicas UPDATE/DELETE. Revocados UPDATE/DELETE/TRUNCATE de app_user y permisos
PUBLIC; solo SELECT/INSERT de runtime. Privilegios administrativos siguen disponibles
para mantenimiento autorizado, sin presentarlos como capacidad de usuario.
Limpieza de fixtures usa propietario exclusivamente para eventos de tenants de test,
antes de borrar organizaciones; sesiones runtime se revierten antes de limpiar.

36 pruebas PostgreSQL/app_user sin BYPASSRLS: aislamiento/lectura sin auth, insercion
valida, identidad suplantada/tenant/parent rechazados, documento/borrador requerido,
permisos reales, UPDATE/DELETE/TRUNCATE denegados, padre protegido, FK cross-tenant
incluso propietario, CHECKs/JSONB y fecha generada. Vaciar documento preserva evento.
No verifica contenido juridico, hashes contra RAT ni permisos/suscripcion de API;
estos controles corresponden a servicios futuros bajo lock, no al CHECK de tabla.

Regresion integral 2470 passed en 221.64 s (3:41), incluidas pruebas anteriores de
schemas/asociaciones. Black/Ruff/Alembic check/whitespace correctos. La suite completa
reemplaza el total anterior como evidencia de regresion, no acredita cierre integral.
No ampliar esta evidencia de persistencia a concurrencia/revision funcional futura.

Sin exposicion API/documental ni accion de revision: sigue pendiente binding final
con RAT actual, evaluador, estados derivados, permisos y relectura transaccional.
Gates/positivo EIPD se conservan; no confirmacion excepcional habilitada. Fuentes
oficiales pendientes. Proximo: CREATE/PATCH/GET documental de resolucion y binding,
con semantica omitir/preservar, null/vaciar, reemplazo entero, inmutabilidad de
confirmados/reemplazados y conservacion del historial; despues revision/evaluador.
M3-T1 EN PROGRESO integral; sin commit.


## 64. API documental de resolucion EIPD y asociacion final

2026-10-06. CREATE/PATCH reciben eipd_resolution_assessment nullable con contrato
editable EipdResolutionAssessmentV1; GET/salida devuelve forma interna con binding.
Hash/actor/decision/estado aportados dentro del documento se rechazan (422).
Sin endpoint de revision humana ni estados derivados de historial en este paso.

Servicio construye contexto con todos los expedientes y snapshot finales. Orden:
aplicar documentos/cambios y RAT; asociar especiales v10; asociar screening v11;
asociar resolucion v1. PATCH mantiene lock de serie y relectura populate_existing;
solo borrador editable. Omitir preserva documento/binding; null vacia JSONB como
NULL SQL; objeto sustituye entero y asocia explicitamente. Cambios en contexto
sin reaporte no actualizan binding. GET/readiness no asocian ni escriben.
No cambiar hashes RAT ni comparadores historicos. No generar/sobrescribir eventos.

Presencia de resolucion agrega barrera provisional compartida
resolucion_eipd_no_validada (409) en readiness/confirmacion, hasta evaluador/revision
funcionales. No altera motivos/positivo de screening ni habilita excepciones.
Retirar documento no elimina historial; ruta ordinaria preparada y sin EIPD requerida
conserva flujo previo. Confirmados/reemplazados rechazan cualquier PATCH.

25 escenarios HTTP nuevos con RAT real/PostgreSQL/app_user: documento parcial,
omision/null/reemplazo, historial previo intacto, lectura sin escritura, invalidacion
por alta/cambio/baja de todos los documentos, orden simultaneo y cambio RAT real,
reaporte explicito, metadata/enums/fechas cerrados, aislamiento por cabecera,
viewer y suscripcion suspendida. Seis bases ordinarias verifican igualdad de barrera
GET/POST y rechazo conservando borrador/vigente; retirar documento restaura ruta
ordinaria y reemplazo/inmutabilidad. No confirmar excepcion ni extrapolar concurrencia.

225 focalizadas aprobadas; regresion integral 2495 passed en 233.70 s (3:53).
Ajuste posterior exclusivamente de redaccion de mensaje al usuario: los 25 HTTP
revalidados (11.07 s). Black/Ruff/whitespace correctos; head local b51d3f6a9c20
sin migracion nueva. Este total no certifica cierre funcional integral.

Proximo: evaluador puro de completitud/aplicabilidad de resolucion segun §60;
despues readiness/vigencia, accion humana autenticada, concurrencia/relectura y
screening versionado/gate separado con fuentes verificadas antes de desbloqueo.
Fuentes y demas pendientes integrales permanecen abiertos. EN PROGRESO; sin commit.


## Checkpoint local autorizado — 2026-10-06

Usuario solicita ejecutar commit del avance acumulado. Revisados los 68 archivos
modificados/nuevos de M3-T1, incluyendo migraciones, servicios, contratos, pruebas
y documentacion. Formato/lint completos aprobados, diff sin errores de espacios,
sin hallazgos de patrones sensibles. Evidencia funcional §64: 2495 pruebas en
suite integral y 25 HTTP posteriores al ajuste de mensaje. El commit registra
avance y pendientes; no declara DONE ni habilita confirmaciones excepcionales.


## 65. Evaluador puro de preparacion documental EIPD

2026-10-06. Continua checkpoint local 6d9bb76. Implementado
evaluate_eipd_resolution_document_v1 en eipd_resolution.py para los bloques
documentales de §60.2: referencias/analisis, respuestas fundadas, evaluacion previa,
fechas, scope completo RAT, riesgos/medidas/evidencia, conclusion, fuentes/consulta
condicionales y binding. Fecha evaluated_on date explicita: sin reloj interno, DB,
LLM, comunicacion externa ni escritura. Revalida modelos/dicts y no reasocia.

Resultado inmutable con issues/applicability ordenados y deduplicados, context_current
y is_document_prepared. No can_confirm: completo expresa preparacion documental,
no revision humana ni autorizacion de tratamiento. Requiere_revision prevalece
sobre incompleto segun §60, preservando todos los motivos de ambas categorias.
Esto no cambia precedencia de otros evaluadores historicos ni sus comparadores.

Riesgos/medidas con IDs canonicos unicos, referencias no vacias/conocidas/unicas,
cobertura de todos los riesgos e implemented si fundada/evidencia propia.
Planes pendientes no son implementacion. Sin puntaje ni umbral juridico calculado;
alto conserva revision como frontera conservadora del producto. No inferir EIPD
previa por fecha de informe/evidencia. Fechas requeridas de informe y consulta de
fuentes no futuras; obtained_on sigue metadata factual opcional, sin regla nueva.

Scope coincide con categorias/grupos completos del snapshot, incluso no sensibles;
scopes de excepciones presentes deben estar contenidos, sin exigir igualdad de
alcances de distinta funcion. Completitud juridica propia de excepciones, rol/rutas,
controles ordinarios/especiales y frontera §59.1 son comprobaciones separadas,
aun pendientes de componer antes de gate/revision. No presentarlas como ejecutadas
por este evaluador documental; presencia de documento preparado no las supera.

Fuentes identificado exige publicacion/version documentada y aplicabilidad resuelta;
no_identificado permite busqueda documentada sin version ficticia de publicacion,
pero contradiccion con fuente declarada aplicable requiere revision. Ninguno de
estos estados acredita verificacion oficial global ni inexistencia de orientaciones.
Consulta no_solicitada exige analisis; referencias/respuestas residuales requieren
revision. En_curso mantiene revision y exige referencia/evidencia, con conclusion
residual marcada. Concluida exige referencias, recomendaciones/reassessment,
respuesta fundada y evidencia; no convierte recomendaciones en aprobacion.

159 pruebas nuevas: faltantes individuales, respuestas/evidencia por elemento,
riesgos/medidas/refs/duplicados semanticos, cobertura, prior assessment no inferido,
fechas explicitas, estados/condicionales de fuentes/consulta, scope RAT/subconjunto
de excepciones, binding ausente/obsoleto, todos los motivos/precedencia, orden
numerico, inmutabilidad, JSON/modelos y revalidacion. 455 focalizadas aprobadas,
incluidos contratos y asociaciones previas; Black/Ruff/whitespace correctos.
Ultima suite integral 2495 passed (§64), no reejecutada para evaluador puro aislado;
no sumar focalizadas como evidencia de una suite integral nueva.

Sin conexion API/readiness ni cambio de gates: resolucion_eipd_no_validada sigue
bloqueando, EIPD positivo y resto de controles se conservan. Fuentes pendientes.
Proximo: exposicion de preparacion documental en readiness y vigencia de revision
como resultados separados, usando contexto RAT actual; despues accion humana,
frontera versionada y concurrencia/aceptacion antes de habilitacion.
M3-T1 EN PROGRESO integral; sin migracion ni nuevo commit en este paso.


## 66. Readiness documental y vigencia de revision EIPD

2026-10-06. Readiness expone eipd_resolution (preparacion documental y
context_current) y eipd_resolution_review (sin_revision/vigente/obsoleta y ultimo
evento). Resultados separados de screening, decision humana y confirmacion.
Documento ausente se evalua cuando hay supuesto EIPD positivo; ruta ordinaria
sin documento conserva preparacion null y estado sin_revision.

El contexto se reconstruye desde RAT actual y documentos finales, sin modificar
snapshot, asociaciones ni historial. Contexto no disponible impide acreditar
vigencia. Ultimo evento tenant-aware por created_at descendente e id descendente:
no seleccionar una decision continuar anterior cuando existe otra posterior.
Vigencia requiere binding actual y coincidencia de hashes documental/contextual;
las tres decisiones conservan su contenido sin convertir vigencia en aprobacion.
Cambiar documento/contexto vuelve obsoleta la revision; reaportar al contexto
cambiado actualiza el documento, pero no renueva los hashes del evento anterior.

18 pruebas nuevas: diez puras y ocho HTTP con RAT/PostgreSQL real. Cubren las
tres decisiones, ausencia de documento/contexto/binding, hashes distintos,
cambios de consentimiento/especiales/screening/RAT, contexto no reconstruible,
reaporte, orden determinista con fecha empatada, aislamiento y GET sin escritura.
La confirmacion conserva resolucion_eipd_no_validada y el screening positivo;
no existe accion API para emitir revisiones ni nueva habilitacion de excepciones.

Validacion: suite completa 2672 passed en 237.06 s; Black/Ruff correctos.
Incluye las 159 pruebas del evaluador §65 y las 18 nuevas de este paso.

Proximo: frontera de revision y accion humana autenticada con controles vigentes,
fuentes oficiales y concurrencia, antes de habilitar confirmaciones. La preparacion
documental no acredita verificacion oficial global ni reemplaza controles propios.
M3-T1 EN PROGRESO, alcance integral; sin migracion ni nuevo commit.


## 67. Prerequisitos puros para registrar revision humana EIPD

2026-10-06. Implementado evaluate_eipd_resolution_review_prerequisites_v1,
con entrada ReviewIn cerrada/revalidada, estado, documento, contexto y fecha
explicita. Resultado inmutable conserva decision y todos los motivos; propiedad
prerequisites_met describe solo estos requisitos documentales, sin autorizacion,
confirmacion ni escritura. No sustituye permisos/suscripcion, tenant, bloqueo de
serie, relectura ni actor/fecha/hashes de servidor que debe resolver la accion API.

Cualquier decision exige borrador, documento presente y binding vigente frente
al contexto RAT actual disponible. Requiere_cambios/no_continuar permiten documento
parcial actual, incluso riesgo alto, para registrar una decision negativa concreta.
Esto no habilita tratamiento. Confirmado/reemplazado, documento ausente, binding
ausente/obsoleto o contexto no disponible conservan motivos de rechazo.

Continuar incorpora todos los motivos del evaluador documental y mantiene barreras
explicitas frontera_revision_no_validada y fuentes_oficiales_no_verificadas.
No hay bandera aportable por cliente para superar controles aun no implementados;
ni documento completo ni fuentes declaradas en su payload acreditan la verificacion
global de §59.6. Esta version no permite continuar. Componer/verificar controles
de frontera en una version posterior antes de habilitar esa decision.

38 pruebas nuevas cubren tres decisiones, parcialidad, riesgo alto, inmutabilidad,
ausencia/obsolescencia, estados no editables, metadatos falsificados y banderas de
aprobacion rechazadas, modelos revalidados, fecha explicita y estado desconocido.
215 focalizadas aprobadas, incluyendo evaluador documental y readiness HTTP previos;
Black/Ruff correctos. Ultima suite integral 2672 passed (§66); no reejecutada para
este servicio aislado y no sumar focalizadas como nueva evidencia integral.

Sin nueva ruta API, migracion, gate ni commit. Proximo: accion autenticada de revision
con edit_content/suscripcion, relectura bajo bloqueo de serie, hashes/actor/fecha de
servidor e historial append-only; conservar barreras de continuar de esta version.
Luego frontera verificada, fuentes y concurrencia antes de abrir confirmaciones.
M3-T1 EN PROGRESO, alcance integral.

Validacion de checkpoint previa al commit autorizado: 2710 passed en 238.18 s;
Black/Ruff sobre seis archivos Python y diff --check correctos. Sin cierre integral.


## 68. Accion autenticada de revision humana EIPD

2026-10-06. POST /licitud/treatments/{treatment_id}/assessments/{assessment_id}/
eipd-resolution/reviews, respuesta 201 EipdResolutionReviewOut. Usa ReviewIn
cerrado, edit_content, suscripcion vigente y tenant validado en servidor.
Servicio record_eipd_resolution_review_v1 obtiene borrador/serie del tenant,
bloquea la misma serie que PATCH/confirmacion y relee populate_existing antes
de reconstruir RAT/contexto actual y aplicar prerequisitos §67. Versiones de
assessment/snapshot distintas de v1 y estados no borrador rechazan.

Actor/tenant/assessment/hashes resueltos en servidor; UUID y fecha de evento
asignados por PostgreSQL. Flush dentro de transaccion del caller; get_db confirma
al terminar o revierte ante error. Evento append-only sin modificar assessment,
serie, documento/binding ni eventos anteriores. Requiere_cambios/no_continuar
admiten parcial presente vigente; continuar sigue bloqueado por frontera/fuentes.
Revision no confirma ni reemplaza un confirmado. Sin nuevo GET de historial:
readiness existente muestra ultimo evento y vigencia, preservando historia en DB.

15 pruebas nuevas: dos decisiones negativas, hashes/identidad/fecha de servidor,
historial conservado, GET sin cambios, obsolescencia/revision nueva, confirmacion
bloqueada; ausencia/asociacion obsoleta/continuar rechazan sin evento; siete campos
falsificados 422; tenant equivocado 403, lookup 404, viewer 403 y suscripcion
suspendida 402; confirmado/reemplazado inmutables. Dos sesiones app_user con RAT
real prueban espera/relectura: borrar documento bajo lock y commit rechaza sin
escritura; rollback permite revisar documento original con sus hashes.

Validacion: 15 pruebas nuevas aprobadas; suite completa 2725 passed en 242.75 s.
Black/Ruff sobre los tres archivos Python modificados y diff --check correctos.

Proximo: frontera versionada de controles de primera ruta soportada y verificacion
oficial de fuentes, conservando screening positivo y barreras hasta aceptacion.
Concurrencia ampliada/cambios RAT y seis bases para gates siguen pendientes antes
de desbloquear. M3-T1 EN PROGRESO integral; sin migracion, nuevo commit ni push.


## 69. Registro de fuentes EIPD y pendiente temporal

2026-10-06. Creado m3-t1-eipd-fuentes.md con enlaces, versiones consultadas,
metodo/limites y resultados separados. Texto legal comprobado; publicacion concreta
de listas/orientaciones no verificada. Busqueda acotada no demuestra inexistencia.
Apertura de consolidado diferido incompleta se registra como tal, sin exagerar evidencia.
Anuncio ministerial de postergacion se conserva como propuesta: no cambia fecha
legal de producto sin ley publicada/comprobada ni certifica tramitacion exhaustiva.

Fuentes globales siguen pendientes; campos documentales del tenant no sustituyen
su verificacion. Barreras fuentes_oficiales_no_verificadas/frontera_revision_no_validada
y confirmacion conservadas. Proximo: matriz/contrato versionado de primera frontera,
que puede implementarse sin abrir continuar mientras las fuentes siguen pendientes.

Paso documental, diff --check correcto; ultima suite integral 2725 passed (§68),
no reejecutada por esta documentacion. Sin nuevo commit/push ni migracion.
M3-T1 EN PROGRESO integral.


## 70. Base normativa fija y contrato de primera frontera EIPD

### 70.1 Decision del proyecto

2026-10-06. Instruccion explicita del usuario: la ley de privacidad/proteccion de
datos es base normativa irrefutable del proyecto, independientemente de su entrada
en vigor en diciembre o eventual postergacion. Para M3 se mantiene el marco de
Ley 21.719/19.628 reformada ya adoptado. No agregar fecha de activacion, excepcion
transitoria ni desactivar controles por anuncio o postergacion. §69/F3 queda como
antecedente informativo, sin condicionar alcance o implementacion. No equivale a
certificar externamente el estado legislativo; es la decision normativa de producto.

Orientaciones/listas complementarias mantienen su pendiente de verificacion
separado. No cambian la certeza del marco adoptado ni impiden implementar controles
basados en el contrato aprobado; no marcar fuentes verificadas sin evidencia.

### 70.2 Contrato propuesto de preparacion de frontera

Servicio puro versionado separado de documento/revision/gate. Entrada interna:
contexto final EipdResolutionContextV1, revalidado incluyendo modelos modificados.
No aceptar de cliente resultados, flags de preparacion, verificacion o aprobacion.
Salida inmutable: result incompleto/requiere_revision/preparado, motivos por campo,
aplicabilidad y ruta sensible_derechos/sensible_biometrica_derechos/sin_resolver.
Sin can_confirm. Requiere_revision prevalece sobre incompleto, conservando todos
los motivos; orden estable y deduplicacion sin borrar preguntas positivas.

| Control | Exigencia de primera frontera | Si falta | Si contradice/sale del soporte |
| --- | --- | --- | --- |
| Contexto | RAT completo actual, rol responsable y alcance completo de su evaluacion | incompleto | otro rol requiere_revision |
| Deteccion especial | Regimen sensible; biometrico opcional, con sensible obligatorio; solo estos en primera ruta | regimen/condicion faltante incompleto | otros regimenes/coexistencias requieren_revision, sin declararlos ilicitos |
| Condicion sensible | sensibles_art16, excepcion_legal, defensa_derechos_art16d | incompleto | consentimiento/otra excepcion requiere_revision |
| Excepcion sensible | Evaluador propio completo y asociaciones especiales actuales | preservar todos los faltantes | preservar todos sus motivos de revision |
| Biometria presente | Excepcion legal de derechos art16ter/art16bis(d), expediente propio y dependencia sensible completos | incompleto | ruta distinta, inconsistencia o residualidad requiere_revision |
| Asociaciones | Comparadores especiales/EIPD vigentes admitidos segun versiones historicas; sin reasociar al leer | ausente incompleto | obsoleta requiere_revision |
| Screening | Cinco respuestas con fundamento; datos_protegidos_excepcion_consentimiento si, otras cuatro no | ausente/pendiente/fundamento faltante incompleto | otro positivo o contradiccion requiere_revision |
| Residuos | Ningun expediente especial fuera de ruta detectada; conservar comprobaciones transversales actuales | no inferir ausencia desde prosa | residuo requiere_revision |

La primera frontera no restringe por nombre de base ordinaria: las seis conservan
su evaluador independiente. Preparado describe ruta especial/screening solamente;
no reemplaza evaluador ordinario, resolucion preparada/no_alto, fuentes o revision.
Una condicion declarada no sustituye hechos RAT; no detectar ni comparar por prosa.
Sensibilidad/biometria y poblaciones se derivan con detectores existentes.

### 70.3 Deteccion versionada y futura composicion

Mantener evaluate_eipd_screening_v1 y sus motivos historicos. Nueva evaluacion v2
prevista reconoce excepcion preparada dentro de esta frontera sin borrar positivos:
requiere_eipd sigue explicitamente presente con motivos. No convertir en
sin_supuestos_declarados ni eliminar blockers de v1 por lista de codigos.
Compartir validaciones historicas mediante refactor probado o implementacion v2
explicita; revalidar contradicciones y bindings, con pruebas de equivalencia v1.

Orden futuro bajo lock: RAT actual, base ordinaria, especiales/frontera,
screening versionado, resolucion, fuentes verificadas, ultimo evento continuar con
ambos hashes actuales. GET y POST usaran reglas compartidas, sin GET mutador.
Revisiones negativas §68 siguen admitiendo parcial vigente; la frontera no se
convierte en requisito para registrar rechazo. Continuar aun no habilitado.

### 70.4 Aceptacion y siguiente paso

Proximo: implementar evaluador puro de frontera y pruebas propias antes de conexion
API/gates. Cubrir sensible sola y sensible+biometria; cada faltante/respuesta;
otros cuatro positivos; pendientes y fundamentos; rol; rutas mezcladas y residuos;
asociaciones obsoletas; dependencia sensible; precedencia/orden/inmutabilidad y
entradas cerradas. Fechas de vigencia legal no figuran como condicion del evaluador.
Despues screening v2 y composicion, fuentes y aceptacion seis bases/concurrencia
antes de habilitar continuar. Este paso cierra contrato, no implementacion funcional.

Ultima suite integral 2725 passed (§68), no reejecutada para documentacion.
Diff --check correcto. M3-T1 EN PROGRESO integral; sin commit/push ni migracion.


## 71. Evaluador puro de primera frontera EIPD

2026-10-06. Implementado evaluate_eipd_frontier_v1 en eipd_frontier.py sobre
EipdResolutionContextV1 interno cerrado/revalidado. Sin DB/reloj/LLM, fecha de
activacion legal ni flags de aprobacion. Resultado inmutable incompleto/
requiere_revision/preparado, ruta candidata, motivos/aplicabilidad y diagnosticos
especial/screening separados. is_frontier_prepared no implica can_confirm.

Reutiliza deteccion, validacion de expedientes especiales, dependencias sensibles/
biometricas y comparadores historicos. Conserva todos sus motivos, roles responsables,
ruta sensible defensa_derechos_art16d/excepcion_legal y biometria dependiente.
Otro regimen, ruta de consentimiento/otra regla, expediente fuera de frontera o
asociacion no vigente requiere revision. Ambas rutas admitidas segun §70.
Las seis bases ordinarias se asocian independientemente: su preparacion propia
se exige despues en composicion/gate; este evaluador no la certifica.

Exige cinco respuestas fundadas: excepcion protegida si y otras cuatro no.
Omitida/pendiente/fundamento ausente incompleto; otro positivo o negacion de
excepcion requiere revision. Precedencia de revision conserva todos los faltantes;
orden estable, deduplicacion e inmutabilidad. Ninguna reasociacion automatica.

Devuelve el screening v1 entero como diagnostico historico, incluidos positivo,
excepcion_especial_no_validada y pendiente_revision: no filtra blockers por codigo
ni cambia ese resultado. Preparado describe la nueva frontera acotada solamente.
Deteccion v2/composicion aun pendientes, sin sustituir v1 en API o confirmacion.
Fuentes/revision humana/documento EIPD y controles ordinarios son etapas separadas.

106 pruebas nuevas: ambas rutas, respuestas/fundamentos de cada pregunta,
faltantes, rol, dependencias, residuales, rutas mezcladas, seis bases ordinarias,
bindings obsoletos/historicos, precedencia/motivos, igualdad modelo/dict,
revalidacion de modelo mutado y rechazo de campos de aprobacion/fecha.
695 focalizadas aprobadas con excepciones sensible/biometrica, resolucion y
prerequisitos de revision; Black/Ruff/diff --check correctos. Ultima suite integral
2725 passed (§68), no reejecutada para nuevo servicio puro sin integracion;
no sumar focalizadas como evidencia de suite completa.

Proximo: deteccion EIPD v2 explicita para esta frontera, conservando motivos
positivos y compatibilidad historica; luego exposicion/composicion compartida y
fuentes/aceptacion antes de habilitar continuar. Base legal fija segun §70.
M3-T1 EN PROGRESO integral; sin cambio de gates, migracion, commit o push.


## 72. Deteccion EIPD v2 y nucleo historico compartido

2026-10-06. Implementado evaluate_eipd_screening_v2(context) puro en
eipd_screening_v2.py; contexto interno cerrado/revalidado. Calcula frontera §71,
no acepta flag de preparacion/approved/version desde cliente. Salida inmutable
EipdReadinessV2: resultados/motivos/observaciones/context_current de deteccion,
frontier y evaluation_version=2 separado de versiones documentales/bindings.

Refactor de evaluate_eipd_screening_v1 a wrapper con misma firma y nucleo privado
compartido. V1 siempre llama sin excepciones preparadas: comportamiento historico
conservado. Nucleo decide motivo durante evaluacion, sin filtrado posterior de
blockers. Comparadores v1-v11, contrato del cuestionario y hash RAT sin cambios.

Solo si frontera completa vigente: excepciones concretas pasan a motivo
excepcion_especial_preparada, categoria supuesto_declarado; la respuesta protegida
si y su motivo original permanecen, resultado requiere_eipd. No equivale a
sin_supuestos_declarados ni permite can_continue. Diagnostico v1 entero permanece
en frontier.screening, incluidos pendiente_revision/excepcion_especial_no_validada.

Fuera de frontera completa, v2 mantiene integro screening v1 con sus motivos,
observaciones y resultado: faltantes, otros positivos, rol, mezclas, residuos y
asociaciones obsoletas no obtienen preparacion. Ruta ordinaria negativa conserva
sin_supuestos_declarados; can_continue heredado expresa solo deteccion y nunca
confirmacion o aprobacion de la frontera. Preparacion de frontera no sustituye
controles ordinarios, resolucion, fuentes ni revision humana.

56 pruebas nuevas: ambas rutas preparadas, positivos historicos conservados,
modelo/dict e inmutabilidad, cada pregunta pendiente/opuesta/sin fundamento,
contextos invalidos, rol, bindings/residuos/coexistencia, campos falsificados,
contexto ausente y screening ordinario negativo. 161 focalizadas iniciales aprobadas
antes de agregar caso ordinario (55 v2 + 106 frontera); nueva suite integral incluye
ese caso adicional y toda regresion v1. Suite integral: 2887 passed en 243.26 s. Black/Ruff/diff --check correctos.

API/readiness/confirmacion siguen usando v1: en este paso no hay conexion de v2
ni habilitacion de continuar. Proximo: exponer frontera y deteccion v2 separadas
en readiness, con resultados/motivos versionados y positivos persistentes;
luego composicion compartida/fuentes/aceptacion antes de desbloqueo.
Ley como base fija, sin reloj normativo. M3-T1 EN PROGRESO integral;
sin migracion, nuevo commit ni push.


## 73. Readiness de deteccion EIPD v2 y frontera

2026-10-06. LegalAssessmentReadinessOut agrega eipd_v2 con contratos cerrados
EipdReadinessV2Out/EipdFrontierReadinessOut: evaluation_version=2, resultado,
context_current, motivos/observaciones y frontier (ruta/result/issues/applicability,
special y screening v1 como diagnosticos). Evaluacion versionada distinta de
schema/binding documental. Campo nullable con default para compatibilidad de
construccion del modelo; servicio readiness siempre calcula y aporta v2.

Usa el mismo contexto final de resolucion reconstruido desde RAT actual disponible,
no snapshot viejo si la finalidad/alcance no se puede recomponer. Contexto no
disponible mantiene deteccion pendiente, frontera incompleta y motivo explicito.
Preparacion v2 no depende de revision humana ni transforma EIPD positiva en negativa.
Resultado v1 root eipd y confirmation_blockers/pending_controls conservados; lectura
GET sin escritura, reasociacion, nuevo evento ni cambio de estado/confirmacion.

14 pruebas nuevas: diez de contrato (ambas rutas, version/extra/route/approval),
dos HTTP preparados sensible y sensible+biometrico con RAT/PostgreSQL real,
positivo/EIPD requerida, v1 entero visible y bloqueo/GET sin cambios. Actualizacion
incompleta de dependencia sensible invalida preparacion; otro HTTP prueba ruta
ordinaria negativa, tenant equivocado y cambio RAT sin reescribir snapshot.
Caso RAT no reconstruible por finalidad cambiada conserva pendiente/contexto falso
y motivo sin usar contexto almacenado como actual. Suite completa: 2901 passed en 247.30 s; Black/Ruff/diff --check correctos.

Siguiente: contrato/matriz de composicion compartida para decision humana y gate,
con ordinarios, especiales/frontera, deteccion v2, resolucion, fuentes y ultima
revision vigentes; avanzar sin habilitar continuar mientras faltan verificaciones.
Fuente normativa fija segun §70; fuentes complementarias siguen separadas.
M3-T1 EN PROGRESO integral; sin migracion, nuevo commit ni push.


## 74. Contrato de composicion compartida de controles EIPD

2026-10-06. Diseno del siguiente servicio puro, separado de permisos, transaccion,
documento editable y evento humano. Ley adoptada como base fija (§70), sin fecha
de activacion/postergacion en entrada ni logica. Alcance: primera frontera §70;
no ampliar otras rutas ni alterar confirmacion ordinaria sin excepcion EIPD.

### 74.1 Entrada interna cerrada

EipdControlCompositionInputV1 propuesto, revalidar modelos/dicts: organization_id y
assessment_id UUID; assessment_status LegalAssessmentStatus; assessment_schema_version
y rat_context_schema_version int (distintos de 1 generan motivo de revision);
justification str nullable; rat_context_current bool nullable obtenido por comparacion
de hash RAT actual/almacenado; context EipdResolutionContextV1 nullable reconstruido;
resolution EipdResolutionAssessmentStoredV1 nullable; latest_review
EipdResolutionReviewOut nullable seleccionado por fecha/id en el mismo tenant.
Fecha evaluated_on date explicita, separada de la fecha de vigencia legal.
No cliente puede aportar este contrato ni ready/approved/fuentes verificadas.

Contexto no reconstruible no se reemplaza por snapshot viejo. Bool RAT true no
suple contexto ausente ni asociaciones/documentos obsoletos. organization_id/
assessment_id del ultimo evento deben coincidir con entrada; discrepancia requiere
revision y no acredita revision actual aunque hashes coincidan. Autorizacion y
lookup tenant siguen siendo responsabilidad del servicio/DB, no de este contrato.

### 74.2 Matriz comun y composicion por finalidad

| Etapa | Exigencia | Resultado insuficiente |
| --- | --- | --- |
| Estado/version | Borrador; versiones assessment/RAT 1 | Estado inmutable/version no soportada: revision |
| Contexto RAT | Actual disponible, hash vigente, categorias/titulares no vacios; rol responsable para esta frontera | Ausente/desconocido: incompleto; obsoleto/otro rol: revision |
| Base/justificacion | Una de seis bases implementadas y justificacion no blanca | Ausente/faltante: incompleto |
| Preparacion ordinaria | Ejecutar evaluador propio de base con RAT actual: consentimiento, LIA, contrato, obligacion legal, derechos o economica | Preservar todos los motivos/aplicabilidad y precedencia propia; no aprobar base por nombre ni por excepcion especial |
| Especiales/frontera | Evaluador §71 preparado, comparadores y dependencias vigentes | Preservar todos sus motivos; otra ruta/residuo no se declara ilicito |
| Deteccion | §72 requiere_eipd, contexto vigente y primera frontera preparada; positivos visibles | Otros positivos/pendientes/contradicciones no superan frontera |
| Resolucion | Evaluador §65 preparado y binding actual, no_alto fundado, fuentes/consulta documentales completas | Preservar todos los motivos; completo no acredita verificacion global |
| Fuentes complementarias | Verificacion global trazable separada del documento tenant | En esta version: fuentes_oficiales_no_verificadas siempre pendiente |
| Revision para confirmar | Ultimo evento del expediente/tenant, vigente en ambos hashes, decision continuar | Ausente: incompleto; obsoleta/decision negativa/discrepancia: revision |

Preparacion ordinaria usa los evaluadores deterministas vigentes sin redefinir sus
comparadores/conclusiones; LIA mantiene condiciones propias de can_confirm.
No filtrar blockers de evaluate_transversal_readiness_v1 para simular aprobacion:
componer etapas explicitas, conservando v1 como diagnostico historico.

### 74.3 Salida y ausencia de circularidad

Resultado inmutable EipdControlCompositionV1 propuesto: preparation_result
incompleto/requiere_revision/preparado, ordinary (base/evaluador/motivos), frontier,
detection_v2, resolution, review_state y colecciones de motivos por etapa.
Precedencia comun requiere_revision sobre incompleto, sin cambiar resultados
individuales; ordenar por etapa/campo/codigo y conservar question_id.

Separar review_blockers de confirmation_blockers. review_blockers para registrar
continuar incluyen estado/contexto, ordinario, frontera/deteccion, resolucion y
fuentes; no requieren evento continuar previo. confirmation_blockers incluyen
esos mismos controles mas ultimo evento continuar vigente. Esto evita que crear
la primera revision positiva exija tener otra positiva anterior.
preparation_result excluye verificacion global y decision humana: preparado solo
expresa que los controles documentales comunes pasan. Ningun can_confirm ni
bandera de autorizacion; en esta version ambas colecciones mantienen fuente
complementaria pendiente y habilitacion no validada hasta aceptacion de gates.

Revision negativa conserva §67/§68: puede registrar rechazo sobre documento parcial
presente vigente en borrador, sin exigir preparacion ordinaria/composicion completa.
No convertir estos blockers comunes en requisito de rechazo. Inmutabilidad/hash/
actor/fecha de servidor y relectura bajo lock siguen exigidos para cualquier evento.

### 74.4 Integracion y aceptacion

Primer paso: implementar composicion pura y pruebas, sin conectar nuevos gates.
Despues exponer resultado orientativo en readiness, preservando historial y motivos
v1/v2. Accion de revision/confirmacion reconstruye misma entrada bajo lock de serie,
relee populate_existing y evalua antes de flush/reemplazo; caller maneja rollback.
GET sin escritura. Fuentes/aceptacion resueltas con evidencia antes de habilitar.

Pruebas previstas: seis bases y ambos alcances; cada etapa/faltante; estado/version;
RAT ausente/obsoleto; ordinario incompleto/revision; residuos/especiales; deteccion
positiva persistente; resolucion parcial/alto/fuentes/consulta; revision ausente,
negativa/obsoleta/otro tenant-expediente; hashes/ultima decision; no circularidad;
orden/todos los motivos/inmutabilidad/modelos revalidados. Luego HTTP/concurrencia
real, rollback, seis bases y conservacion del confirmado antes de gates habilitados.

Paso documental: ultima suite completa 2901 passed (§73), no reejecutada.
Diff --check correcto. M3-T1 EN PROGRESO integral; sin commit/push ni migracion.


## 75. Composicion pura de controles EIPD implementada

2026-10-06. compose_eipd_controls_v1 en eipd_controls.py implementa §74.
Entrada interna cerrada con tenant/assessment, estado/versiones, justificacion,
vigencia RAT/contexto actual, resolucion y ultimo evento; fecha date explicita.
StrictBool/StrictInt y revalidacion en modo python antes de JSON: evita que una
instancia mutada serialice True como version 1. Campos/fechas de aprobacion y
activacion normativa ajenos rechazados. Sin DB/reloj/LLM ni escrituras.

Composicion por estado/RAT, evaluador ordinario propio de seis bases, frontera,
deteccion v2 y resolucion. Resultados propios conservan motivos/aplicabilidad y
limites: no asumir base preparada por nombre. preparation_result documental
preparado/incompleto/requiere_revision con todos los motivos por etapa y
precedencia comun, sin cambiar precedencia interna de evaluadores existentes.

review_blockers comunes no exigen revision positiva anterior. confirmation_blockers
agregan ultimo evento humano, decision continuar y hashes vigentes. Evento de
otro tenant/assessment conserva motivo revision_otro_expediente y estado obsoleto,
aunque hashes coincidan. Estados/historia se copian a snapshots dataclass congelados
para salida inmutable, sin alterar evento persistido o input. Negativas no habilitan
confirmacion; su registro parcial sigue en servicio §67/§68, sin nuevos requisitos.

Fuentes/aceptacion pendientes permanecen como fuentes_oficiales_no_verificadas y
gate_eipd_no_habilitado en ambas colecciones. Preparado no es permiso ni can_confirm;
no cambia gates actuales ni conecta composicion a API. Frontera/deteccion mantienen
positivo EIPD y diagnostico v1 entero. Ley fija, sin fecha de activacion legal.

80 pruebas nuevas: ambas rutas, preparacion sin revision/no circularidad, tres
decisiones vigentes, hashes distintos/cambio documental, identidad de evento,
estado/version/justificacion/RAT/expediente ausentes, seis evaluadores ordinarios,
fallos de etapas/riesgo residual, entrada cerrada/tipos estrictos/modelo mutado,
fecha explicita, inmutabilidad de salida/revision, orden y todos los motivos.
468 focalizadas aprobadas incluyendo frontera/v2/resolucion/prerequisitos y HTTP
readiness/revision previos; Black/Ruff/diff --check correctos. Ultima suite integral
2901 passed (§73), no reejecutada para nuevo servicio puro sin integracion;
no sumar focalizadas como evidencia de una suite completa nueva.

Proximo: exponer composicion orientativa en readiness con campos de servidor,
ultimo evento del tenant y misma fecha/contexto de evaluacion. Despues integracion
bajo lock/fuentes/aceptacion antes de habilitar revision continuar o confirmacion.
M3-T1 EN PROGRESO integral; sin migracion, nuevo commit ni push.


## 76. Composicion de controles EIPD expuesta en readiness

2026-10-06. eipd_controls publica la composicion §75 con contrato cerrado y
version 1; detection_v2 conserva version 2. Separa preparation_issues,
review_blockers y confirmation_blockers, sin convertir preparado en permiso.
Se muestra ante expediente EIPD, deteccion positiva, excepcion propuesta o
historial existente; el flujo ordinario sin estos antecedentes devuelve null.

Usa identidad del servidor, contexto RAT actual, ultimo evento del mismo tenant
ya consultado y una unica fecha de evaluacion compartida con el diagnostico
documental. No agrega consultas de historial ni escrituras en GET. Documento
retirado conserva evento obsoleto; contexto RAT no reconstruible conserva los
motivos de falta de contexto. Diagnosticos existentes y bloqueos permanecen.

17 pruebas nuevas de contratos/HTTP: versiones y campos cerrados, resultados
consistentes, negativas sucesivas, retiro documental, contexto perdido, aislamiento
entre organizaciones, consultas repetidas sin cambios e historial conservado.
Suite completa: 2998 passed en 248.05 s, incluyendo las 80 pruebas puras de
§75 y las 17 nuevas de este paso. Black/Ruff y diff --check correctos.

Proximo: integrar composicion compartida bajo lock en revision positiva y
confirmacion, conservando barreras de fuentes complementarias/aceptacion.
Ley fija sin dependencia temporal. M3-T1 EN PROGRESO integral; continuar y
confirmacion excepcional bloqueados. Sin migracion, nuevo commit ni push.


## 77. Composicion compartida integrada bajo lock

2026-10-06. Readiness y operaciones mutadoras reutilizan el mismo constructor
interno de composicion y lector del ultimo evento, filtrado por tenant/assessment.
La salida cerrada se valida y serializa en modo JSON para los errores HTTP.
No recibe indicadores de habilitacion del cliente ni modifica hashes/documentos.

Revision continuar reconstruye RAT/contexto despues del lock de serie y relectura
populate_existing; calcula vigencia RAT real y comparte fecha con prerequisitos.
Rechaza antes de insertar cuando faltan prerequisitos o review_blockers, incluyendo
fuentes/aceptacion. Conserva codigo/issues previos y agrega eipd_controls. Negativas
mantienen prerequisitos parciales §67/§68 sin exigir composicion documental completa
ni evento positivo previo. Ultimo evento negativo no habilita confirmacion.

Confirmacion conserva orden de validadores ordinarios, vigencia RAT y motivos
transversales. Ante documento EIPD/deteccion positiva o pendiente/excepcion de
derechos, compone bajo el lock existente antes de consultar/reemplazar confirmado
o hacer flush. confirmation_blockers impiden escritura; error transversal conserva
codigo/diagnosticos previos y agrega eipd_controls. No elimina motivos v1 ni cambia
resultados ordinarios. Los rechazos previos de base/estado/RAT conservan precedencia.

Seis casos nuevos: cuatro HTTP comparan composicion del rechazo con readiness,
con/sin ultimo evento negativo, sin cambios en borrador/historial; dos amplian
concurrencia real app_user de revision positiva con retirada documental confirmada
o revertida. Al esperar se usa documento refrescado y la barrera permanece; no se
inserta evento. Casos negativos previos siguen probando insercion tras rollback.
Doble unitario de confirmacion declara ausencia de historial para la nueva lectura.
227 pruebas focalizadas aprobadas. Suite completa: 3004 passed en 253.18 s. Black/Ruff/diff --check correctos.

Proximo: ampliar concurrencia real de confirmacion y cobertura HTTP de seis bases
para esta composicion antes de resolver fuentes complementarias/aceptacion y
habilitar cualquier frontera. Ley como base fija sin dependencia temporal.
M3-T1 EN PROGRESO integral; continuar/confirmacion excepcional bloqueados.
Sin migracion, nuevo commit ni push.


## 78. HTTP seis bases y concurrencia real de confirmacion

2026-10-06. Ampliada matriz HTTP de resolucion EIPD: seis bases ordinarias con
expediente ordinario completo, con/sin ultimo evento negativo. Revision continuar
y confirmacion rechazan conservando composicion identica a readiness, motivos
previos, borrador, historial y confirmado anterior. review_blockers no exige evento
positivo previo. Tras retirar documento EIPD en flujo ordinario sin supuesto
positivo, se conserva confirmacion ordinaria y proteccion del confirmado.
Esta evidencia no certifica seis bases con excepciones protegidas: el escenario
es ordinario y algunas bases excluyen datos sensibles por sus propios controles.

Dos casos nuevos de concurrencia PostgreSQL/app_user, RAT real y lock de serie:
transaccion titular cambia referencia documental y registra decision no_continuar;
confirmacion en otra conexion tiene borrador precargado y espera lock real,
verificado mediante pg_blocking_pids. Tras commit relee documento/ultimo evento
vigente negativo; tras rollback usa documento original sin evento. Rechazos 409
antes de reemplazar confirmado, sin insertar eventos adicionales ni confirmar
borrador; diagnostico final coincide con GET y confirmado anterior intacto.

Ocho casos adicionales (seis combinaciones con evento previo y dos concurrencias),
mas verificaciones ampliadas en los seis casos existentes. 54 focalizadas aprobadas.
Suite completa: 3012 passed en 295.88 s. Black/Ruff/diff --check correctos.
Sin cambios de logica productiva en este paso, migracion, nuevo commit ni push.
M3-T1 EN PROGRESO integral; continuar/confirmacion excepcional bloqueados.
Ley como base normativa fija, sin condicion por fecha de entrada en vigor.

Proximo: revisar matriz de aceptacion de primera frontera EIPD y verificar fuentes
complementarias oficiales con registro de evidencia. No habilitar gates por el
numero de pruebas ni interpretar una busqueda sin resultados como inexistencia.


## 79. Revision de aceptacion de primera frontera y fuentes

2026-10-06. Revision documental/codigo en HEAD 792c935; no cambia gates.
Base normativa fija §70; fuentes complementarias revalidadas en registro §79/F4.
BCN art15ter y PDF Diario Oficial comprobados, sin instrumento complementario
especifico verificado. Busqueda acotada no demuestra inexistencia ni certifica
inventario de actos de Agencia. Riesgo no_alto y bloqueos globales son limites de
producto, no atribucion de aprobacion obligatoria de Agencia o prohibicion legal
general de riesgo alto. No usar campos editables del tenant como verificacion.

### Matriz de aceptacion acotada

| Criterio | Evidencia comprobada | Conclusion actual |
| --- | --- | --- |
| Sensible de derechos y sensible+biometrica, dependencias/rol/residuos | test_services_eipd_frontier.py, §71; test_api_eipd_v2_readiness.py, §73 | Preparacion especial probada; no autorizacion |
| Deteccion v2 positiva y diagnostico v1 integro | test_services_eipd_screening_v2.py y HTTP v2 | requiere_eipd preservado; gate v1 sigue bloqueando |
| Composicion documental preparada en ambas rutas | test_services_eipd_controls.py, prepared_controls, §75 | Evidencia pura; separacion documental/fuentes/revision |
| Resolucion y ultima decision vigente/obsoleta/negativa | servicios/pruebas §65-68 y composicion §75 | Evaluadores e historial probados; ninguna positiva aceptada actualmente |
| HTTP seis bases ordinarias y confirmado anterior | test_resolution_keeps_confirmation_blocked_six_bases, §78 | No acredita EIPD completa de rutas protegidas; economica conserva exclusion propia |
| Concurrencia revision/confirmacion app_user y RAT real | test_rereads_document_after_series_lock y test_confirmation_rereads_document_and_latest_review_under_real_lock, §77-78 | Documento parcial ordinario; commit/rollback y ultima negativa probados |
| HTTP de ambas rutas protegidas con ordinario/resolucion completos | Aun falta escenario combinado de preparation_result preparado y solo barreras globales | PENDIENTE; ampliar antes de aceptar frontera |
| Concurrencia de expediente protegido preparado/cambio de dependencia | No acreditada por las pruebas ordinarias anteriores | PENDIENTE; no extrapolar cobertura |
| Instrumento complementario de Agencia versionado/aplicable | Registro de fuentes §79: no verificado | PENDIENTE; conservar barrera |
| Habilitacion de revision positiva/confirmacion | §67 agrega frontera_revision_no_validada/fuentes; §75 agrega gate_eipd_no_habilitado; confirmacion conserva v1 | NO HABILITADA; retiro futuro requiere contrato/evidencia, sin filtrar codigos v1 |

Conclusion: primera frontera NO aceptada para habilitacion. Esto no deshace
implementacion/readiness probados; identifica pendientes diferentes del total de
pruebas. M3-T1 EN PROGRESO integral; no cierre DONE ni aprobacion juridica externa.

Proximo paso implementable independiente de publicaciones: HTTP de ambas rutas
protegidas con expediente ordinario/resolucion completos, usando RAT real y
confirmando preparation_result preparado sin habilitar continuar; luego cambio de
dependencia y concurrencia protegida. Conservar positivos, todos los motivos,
borrador/historial/confirmado y controles de base propia. No forzar seis bases
compatibles con sensibles si su evaluador propio lo excluye.

Paso documental: ultima suite integral 3012 passed en 295.88 s (§78), no
reejecutada. Diff --check correcto. Sin codigo, migracion, nuevo commit o push.


## 80. HTTP de ambas rutas protegidas con composicion preparada

2026-10-07. test_api_eipd_prepared_frontier.py agrega cuatro casos HTTP con RAT
real/PostgreSQL: sensible de derechos y sensible+biometrica de derechos, con/sin
ultima revision no_continuar. Base ordinaria contrato con expediente propio completo;
no extrapola a seis bases ni elimina restricciones economicas sobre sensibles.
Resolucion completa usa finalidad y alcance integral del snapshot real de M2,
se aporta por PATCH y recibe binding del servidor. Referencias de fuentes son
sinteticas de test y editables del tenant; no acreditan verificacion global.

Readiness acredita preparation_result preparado, cero preparation_issues,
ordinario/resolucion completos y contexto vigente. Deteccion v2 requiere_eipd;
diagnostico v1 pendiente_revision permanece integro. review_blockers contiene
exclusivamente fuentes_oficiales_no_verificadas y gate_eipd_no_habilitado: no exige
revision positiva previa. confirmation_blockers agrega revision ausente o ultima
decision negativa. POST continuar y confirmar rechazan 409 con la misma composicion,
sin modificar borrador/historial; GET repetido identico y tenant ajeno 403.

Retirar dependencia sensible invalida frontera/composicion, vuelve obsoleta
resolucion y, cuando existe, ultima revision humana; ambas acciones siguen
rechazadas y no crean eventos ni cambian borrador tras rechazo. No reescribe
asociaciones al consultar ni borra los antecedentes historicos.

Cuatro pruebas nuevas aprobadas. 89 pruebas HTTP focalizadas aprobadas en 34.89 s, incluyendo readiness v2,
composicion, documentos y revision previos. Black/Ruff/diff --check correctos.
Paso de pruebas/documentacion; sin cambios de logica productiva o migracion.
Ultima suite completa 3012 passed (§78), no reejecutada; no sumar pruebas focalizadas
como nueva evidencia integral. M3-T1 EN PROGRESO integral, primera frontera aun
no aceptada para habilitacion; fuentes complementarias pendientes §79.
Ley como base fija sin dependencia temporal. Sin nuevo commit ni push.

Proximo: concurrencia real de ambas rutas protegidas preparadas, cambiando
dependencia/documento bajo lock con commit/rollback; conservar relectura actual,
historial y rechazo antes de escritura. Luego completar aceptacion/fuentes.


## 81. Concurrencia real de ambas rutas protegidas preparadas

2026-10-07. Ocho casos nuevos en test_api_eipd_prepared_frontier.py:
sensible/sensible+biometrica x revision continuar/confirmacion x commit/rollback.
Fixture asincrona compartida construye via HTTP expediente ordinario contrato,
frontera y resolucion completos con RAT real; prepara ultima revision negativa
vigente por accion autenticada. No usa mocks del RAT ni del evaluador.

Dos conexiones runtime app_user con identidad autenticada y lock de serie real.
Transaccion titular retira dependencia sensible usando update_legal_assessment_draft_v1,
con contrato normalizado y flush real. Otra conexion precarga borrador y solicita
revision positiva/confirmacion; pg_blocking_pids acredita espera antes de liberar.
Tras commit se relee dependencia incompleta: preparacion/frontera no preparadas,
resolucion y revision obsoletas. Tras rollback se recupera composicion preparada
identica a readiness anterior, incluida ultima decision negativa vigente.

Ambas operaciones rechazan 409 en los ocho escenarios, conservan barreras globales
y mismo evento historico; no insertan nuevos eventos ni confirman borrador. GET
final coincide con diagnostico calculado tras lock. Resolucion almacenada permanece
intacta; rollback conserva borrador original completo y commit solo cambios de la
actualizacion autorizada. Expectativa documental usa normalizacion del schema,
no supone que input vacio persista literalmente como objeto vacio.

97 HTTP focalizadas aprobadas en 36.68 s incluyendo §§80, v2, composicion,
documentos y revision previos. Black/Ruff/diff --check correctos. Ultima suite
completa 3012 passed (§78), no reejecutada para este paso de pruebas; no sumar
focalizadas como nuevo total integral. No cambia logica productiva ni migraciones.

Pendiente tecnico de concurrencia preparada identificado en §79 cubierto para
ambas rutas con contrato ordinario y negativa previa. No extrapola a otras bases,
regimenes o confirmacion excepcional exitosa. No modifica fronteras ni retira
controles v1/§67/globales. M3-T1 EN PROGRESO integral; fuentes complementarias y
aceptacion final de habilitacion pendientes. Ley fija sin dependencia temporal.
Sin nuevo commit ni push.

Proximo: actualizar aceptacion con evidencia §§80-81 y delimitar contrato de
habilitacion del servidor, incluyendo transicion de diagnostico historico v1 sin
filtrado de codigos y verificacion complementaria auditable. Mantener bloqueos
mientras faltan fuentes/aceptacion; el alcance integral restante sigue pendiente.


## 82. Aceptacion actualizada y contrato de habilitacion del servidor

2026-10-07. HEAD revisado 91a71cd26ca3ab9e2960d0c4f1ffb3f28de973fc, limpio.
Paso de diseno/documentacion; no autoriza habilitacion ni afirma verificacion de
fuentes distinta de §79. Ley como base fija §70, sin fecha de activacion normativa.

### 82.1 Aceptacion de evidencia y pendientes

| Criterio §79 | Actualizacion comprobada | Alcance y pendiente |
| --- | --- | --- |
| HTTP protegido completo | §80: cuatro casos, dos rutas con/sin negativa; preparation_result preparado y solo barreras globales en review_blockers | Cubierto con contrato ordinario; no seis bases protegidas ni habilitacion |
| Concurrencia protegida preparada | §81: ocho casos, dos rutas x revision/confirmacion x commit/rollback, dos app_user y RAT real | Cubierto para retiro de dependencia sensible y ultima negativa; no cambio concurrente de politica ni confirmacion exitosa |
| Bases ordinarias y confirmado anterior | §78: seis bases ordinarias, rechazo conserva confirmado | No extrapolar a bases que excluyen sensibles |
| Instrumento complementario aplicable/versionado | §79 no verificado | PENDIENTE; busqueda acotada no acredita inexistencia |
| Decision versionada de habilitacion/compatibilidad | Controles actuales §67/§75 y transversal v1 incondicionales | PENDIENTE implementacion/pruebas; no retirar codigos por lista |
| Revision positiva y confirmacion exitosa | Ninguna autorizada por producto actual | PENDIENTE evidencia tecnica, fuentes y aceptacion explicita de frontera |

Se cierra el pendiente de evidencia HTTP/concurrencia preparada del escenario
acotado, no la aceptacion final de habilitacion. Ultima suite integral 3012 passed
§78; §§80-81: 97 HTTP focalizadas, no nuevo total integral. M3-T1 EN PROGRESO.

### 82.2 Contrato interno propuesto EipdGatePolicyV1

Entrada exclusivamente del servidor, cerrada/revalidada e inmutable tras evaluar.
No forma parte de Create/PATCH/ReviewIn; rechazar campos approved/can_confirm,
policy, flags de fuentes/aceptacion y fechas de activacion enviados por cliente.
Resolver inicialmente devuelve politica deshabilitada; ninguna variable de entorno
booleana, texto del tenant, fecha legal o busqueda sin resultados la habilita.

Campos requeridos (nullable explicitos donde corresponda):

- policy_version: StrictInt literal 1; policy_reference: identificador de revision
  controlada del servidor, no referencia libre de usuario.
- routes: conjunto cerrado de sensible_derechos/sensible_biometrica_derechos,
  sin rutas repetidas; no habilitacion global de excepciones por comodin.
- sources_status: pendiente/verificadas; source_records: instrumentos con emisor,
  referencia/URL primaria, version/fecha y analisis de aplicabilidad a cada ruta,
  junto a evidencia de verificacion y responsable del registro del servidor.
- acceptance_status: pendiente/aceptada; acceptance_reference y validation_commit:
  evidencia de revision tecnica de esta frontera/version, no total de pruebas solo.
- activation: deshabilitada/habilitada; cambios versionados/auditables de politica.

Combinaciones contradictorias o incompletas son errores de contrato, nunca permiso.
Fuentes verificadas exige instrumentos y trazabilidad comprobados del servidor;
aceptada exige referencia/commit/evidencia para las rutas seleccionadas. Habilitada
exige ambas condiciones y al menos una ruta. Pendiente/deshabilitada es valido y
conserva barreras. No inventar instrumento ni declarar verificadas por ausencia
inferida de busqueda. No incorporar en este contrato una obligacion legal general
de aprobacion de Agencia: consulta y limites de riesgo mantienen contrato §59/§65.

Hash canonico policy_hash cubre version/referencia, rutas, fuentes/aplicabilidad,
aceptacion y activation; calcular del objeto validado en servidor. Cualquier cambio
relevante produce otra identidad de politica. La evidencia real se registra/revisa
antes de aceptar fuentes, no se acredita porque un objeto interno diga verificadas.

### 82.3 Composicion y decision versionadas, sin circularidad

Nueva composicion v2 prevista recibe contexto §74 y politica interna explicita;
v1 y todos los bindings documentales/RAT conservan contratos actuales. Diagnostico
v1 entero permanece visible. Version de politica (1), composicion/gate (2), deteccion
(2) y bindings actuales son conceptos distintos; no aceptar version desde cliente.

Motivos documentales/frontier/ordinarios se calculan aun con politica deshabilitada.
Etapa sources depende de evidencia de politica; activation exige ruta incluida y
aceptacion/habilitacion. Resultado documental preparado sigue sin otorgar permiso.
review_blockers nunca exige ultima revision positiva; negativas siguen contrato
parcial §67/§68. confirmation_blockers agrega ultima continuar vigente, misma
organizacion/assessment y hashes documento/contexto/politica actuales.

Prerrequisitos de revision positivos v2 componen controles en vez de sumar barreras
fijas §67 despues de composicion habilitada. V1 conserva su comportamiento entero.
Sin politica resuelta/valida, ruta fuera de alcance, fuentes o aceptacion pendientes:
continuar y confirmacion excepcional siguen rechazados. Faltantes/revision se
reportan por etapa, sin ocultar positivos ni convertir requiere_eipd en negativo.

### 82.4 Transicion de controles transversales

Confirmacion v2 futura debe construir decision semantica propia compartiendo los
validadores actuales: base ordinaria, rol/RAT/vigencia, especiales, dependencias,
residuos, deteccion v2, resolucion, politica y revision. No llamar v1 y sustraer
screening_eipd_no_preparado/resolucion_eipd_no_validada u otros codigos. No reutilizar
un can_continue de deteccion como permiso de confirmacion. Motivos historicos v1
quedan como diagnostico con version explicita, separados de decision activa v2.

Fuera de primera frontera/politica habilitada, conservar el rechazo ordinario y
transversal correspondiente, incluidas rutas mixtas, otros positivos, contextos
incompletos y bases incompatibles. Antes de conectar decision activa: pruebas de
equivalencia del flujo ordinario y de cada rechazo historico, no solo caso feliz.
GET consulta sin escribir/reescribir bindings, mismas entradas que operaciones.

### 82.5 Vigencia humana y atomicidad de politica

Revision positiva futura registra tambien policy_reference/version/hash actuales
como metadatos de servidor. Requiere contrato/persistencia append-only nuevo y
migracion propia antes de conexion: no reescribir eventos ni migraciones antiguas.
Eventos negativos existentes permanecen legibles. Evento positivo sin identidad
de politica no acredita gate v2 aunque documento/contexto coincidan; una nueva
politica requiere nueva revision humana, no promover evento viejo automaticamente.

Bajo lock de serie: releer borrador/RAT/ultimo evento y resolver politica actual
antes de insertar/reemplazar/flush. Politica debe permanecer estable hasta commit:
si es artefacto inmutable del proceso, impedir cambio durante transaccion; si se
persiste, adoptar revision/lock compatible con actualizacion de politica y probar
concurrencia/revocacion. No basta comparar un hash antes de esperar lock. Caller
maneja rollback. No introducir segundo orden de locks sin diseño de no-deadlock.

### 82.6 Implementacion secuenciada y validacion

Siguiente paso: schema/evaluador puro de politica y composicion v2, sin resolver
habilitada en produccion ni migracion/API/gates nuevos. Pruebas: cierres/StrictInt,
modelos mutados, rutas/dependencias, estados contradictorios, trazabilidad ausente,
hash estable/sensible a cambios, fuentes pendientes, habilitacion limitada a ruta,
revision ausente/negativa/politica vieja y cero circularidad. Mantener v1 sin cambios.

Luego persistencia de metadatos de politica en eventos y resolver/auditoria;
prerrequisitos/decision transversal v2 compartidos; HTTP/concurrencia real de cambio
de politica y dependencias, confirmado previo, tenant/roles/suscripcion y hashes.
Resolver real queda deshabilitado mientras fuentes/aceptacion faltan. Cubrir exitos
con politica sintetica de test no autoriza habilitar politica real. Ultima suite
completa y revision tecnica requeridas antes de cualquier habilitacion efectiva.

Paso documental, diff --check correcto; no reejecutar pruebas por diseno sin codigo.
Sin migracion, nuevo commit ni push; frontera no habilitada y M3-T1 EN PROGRESO integral.


## 83. Politica pura y composicion v2 implementadas

2026-10-07. eipd_policy.py implementa EipdGatePolicyV1, SourceRecordV1 y
EipdReviewPolicyIdentityV1 exclusivos del servidor; no se agregan a API/input del
tenant ni se implementa resolver real. Schema cerrado, StrictInt version 1 y
revalidate_instances always en politica/fuentes/identidad; normaliza textos y exige
referencias, URL HTTP(S), fecha/version, cobertura de rutas, responsables y evidencia.
URL valida no acredita emisor/autenticidad: verificacion real pendiente en resolver.

Rechaza rutas/instrumentos duplicados, rutas desconocidas, habilitacion sin rutas,
fuentes verificadas sin instrumentos/cobertura y aceptacion sin referencia, commit
Git completo, evidencia/responsable. Fuentes pendientes/aceptacion pendiente y
activacion deshabilitada siguen estados validos. No introduce fecha de vigencia
legal; fecha explicita date permite detectar publicaciones futuras, sin reloj interno.

build_eipd_policy_hash_v1 SHA256 canonico de todos los datos validados, ordenando
rutas/instrumentos y rutas de aplicabilidad; cambios de evidencia/aceptacion/emisor
responsable/activacion producen otra identidad. evaluate_eipd_policy_v1 devuelve
snapshot congelado y motivos sources/activation ordenados/deduplicados. Politica
None conserva fuentes/gate pendientes y politica_no_disponible; ruta fuera de
politica no queda habilitada. Politicas sinteticas de test no autorizan el producto.

EipdControlCompositionInputV2 agrega assessment v1, politica nullable explicita y
ultima identidad humana nullable; identidad sin evento rechazada. Salida congelada
EipdControlCompositionV2 version 2 agrega politica y review_policy_status, separado
de review_state documental. Mismo nucleo privado compone documentacion y etapas
para v1/v2; v1 mantiene barreras constantes sin cambio de firma/resultados.
V2 calcula etapas de politica durante evaluacion, sin filtrar motivos de v1.

review_blockers no exige evento humano previo. confirmation_blockers agrega
identidad de politica de ultimo evento: id de evento, version, referencia y hash
actuales; sin identidad/otra revision/hash previo bloquean. Vigencia documental
se conserva separada: politica coincidente no elimina obsolescencia del documento,
contexto, otro tenant/assessment ni decision negativa. Deteccion requiere_eipd y
screening v1 entero permanecen. Sin can_confirm ni permiso externo de evaluadores.

104 pruebas nuevas: estados/campos/tipos/cobertura/tipos URL, hashes canonicos y
cambios relevantes, rutas limitadas, politica ausente/deshabilitada/futura, fecha
explicita, entradas/ReviewIn cerrados, ambas rutas preparadas sin circularidad,
tres decisiones, politica anterior/otro evento/documento/tenant, faltantes comunes,
inmutabilidad y modelos anidados modificados revalidados. Se corrigio durante
pruebas la aceptacion por defecto de instancia anidada ya validada pero mutada;
revalidacion always evita confiar en ese estado. No se altera modelo cliente v1.
184 pruebas puras aprobadas (104 nuevas + 80 composicion v1). Suite completa: 3128 passed en 276.34 s, incluyendo §§80-81 y nuevas pruebas
de politica; Black/Ruff/diff --check correctos.

API/readiness/acciones/confirmacion siguen en v1 y barreras actuales. Sin persistir
metadatos ni activar resolver/gate v2. Fuentes complementarias/aceptacion pendientes;
M3-T1 EN PROGRESO integral y ley fija. Sin migracion, nuevo commit ni push.
Proximo: contrato/persistencia append-only de identidad de politica en eventos,
compatibilidad con historicos y RLS antes de resolver/auditoria/accion v2. Politica
real permanece deshabilitada mientras faltan fuentes/aceptacion y evidencia final.


## 84. Identidad de politica persistible en eventos EIPD

2026-10-07. Nueva migracion append-only c62e407bad31 sobre b51d3f6a9c20;
EipdResolutionReview incorpora policy_version Integer, policy_reference Text y
policy_hash Text, todos nullable y sin defaults/backfill. Restriccion CHECK exige
los tres NULL para historia sin identidad, o todos NOT NULL con version 1,
referencia no vacia y hash hexadecimal minusculo de 64 caracteres. NOT NULL
explicitos en rama completa impiden aceptar identidad parcial por logica SQL NULL.
Convencion de nombres del repo se conserva, incluido nombre generado/truncado;
pruebas identifican el constraint real desde catalogo PostgreSQL.

No modifica RLS SELECT/INSERT, FK compuesta tenant/assessment, actor autenticado,
requisito de borrador/documento, ni prohibicion UPDATE/DELETE/TRUNCATE app_user.
Eventos antiguos no se reescriben ni reciben una politica supuesta. Continuar
historico sin identidad sigue legible y no acredita composicion v2. No se exige
identidad a negativas antiguas ni se inventa autorizacion para nuevos positivos.

EipdResolutionReviewWithPolicyOut agrega lectura cerrada/nullable con version
estricta y coherencia de los tres campos, heredando UTC y metadatos de servidor.
No sustituye respuesta API v1 en este paso. ReviewIn sigue rechazando los tres
campos; caller no puede aportar hashes/version/referencia de politica.

build_eipd_review_policy_metadata_v1 calcula campos desde politica interna validada;
no autoriza insercion positiva ni verifica fuente externa. derive_eipd_review_policy_identity_v1
mapea id del evento persistido junto a identidad validada; historicos todos NULL
producen None. Metadatos parciales, version/hash invalidos o identidad sin id se rechazan, sin
promover revisiones viejas a politica actual. No resolver habilitado ni conexion de
acciones v2; POST actual conserva barreras y eventos sin identidad.

35 pruebas nuevas: insercion/lectura runtime con identidad, legacy intacto y mapper,
12 parciales/formatos invalidos rechazados por CHECK real, spoof tenant/actor/parent/
sin auth rechazado por RLS, UPDATE de identidad prohibido, tres decisiones legacy
sin promocion, salida cerrada/tipos estrictos, ReviewIn rechaza metadatos y mapper
rechaza identidad incompleta. 71 pruebas de persistencia/contratos aprobadas,
incluyendo 36 anteriores. Alembic check: No new upgrade operations detected.
Migracion aplicada localmente; comparacion de contenido anterior a/post upgrade
sobre 0 eventos existentes (no constituye prueba de conversion de historial poblado).
Fixtures de eventos sin politica verifican compatibilidad nullable y lectura.
Suite completa: 3163 passed en 277.43 s; Black/Ruff/diff --check correctos.

Proximo: resolver de servidor deshabilitado y lectura de composicion/identidad v2,
antes de auditoria/politica real y acciones v2. Habilitacion efectiva aun requiere
fuentes complementarias/aceptacion, decision transversal v2 sin filtrar v1 y
concurrencia de politica. Ley fija; M3-T1 EN PROGRESO integral; gates bloqueados.
Sin nuevo commit ni push; ninguna migracion historica reescrita o downgrade ejecutado.


## 85. Resolver deshabilitado y lectura de composicion v2

2026-10-07. resolve_eipd_gate_policy_v1 devuelve instancia nueva/revalidada de
artefacto fijo m3-t1-eipd-deshabilitada-v1, version 1, ambas rutas delimitadas,
fuentes/aceptacion pendientes, sin instrumentos/evidencia supuestos y activacion
deshabilitada. Sin parametro de cliente, flags/env, reloj normativo, red o DB;
no acredita auditoria de politicas habilitadas ni permite cambios de politica en
produccion. Una instancia mutada no altera la siguiente resolucion.

LegalAssessmentReadinessOut agrega eipd_controls_v2 nullable junto a v1 conservado.
Salida cerrada/version 2 incluye policy, review_policy_status y latest_review_policy
nullable (id del evento + version/referencia/hash). Policy snapshot valida identidad
completa, estados de activacion coherentes y rutas sin duplicados; tipos/versiones
estrictos, campos extra rechazados. Deteccion anidada version 2 y politica version 1
permanecen conceptos separados. No incluye can_confirm ni permiso de tratamiento.

Readiness construye ambas composiciones con mismo contexto RAT actual, vigencia,
fecha explicita y ultimo evento. Constructor de entrada comun evita drift. Consulta
unica de historial obtiene payload legacy e identidad desde la misma fila filtrada
por tenant/assessment y ordenada created_at/id; acciones v1 reutilizan wrapper legacy.
No busca evento anterior si ultimo carece de politica o es negativo. Ambito de
exposicion igual a §76: EIPD/documento/excepcion/historia; flujo ordinario sin estos
antecedentes mantiene ambas composiciones null.

GET no escribe ni reasocia; retirar documento conserva historial y separa vigencia
documental obsoleta de identidad de politica coincidente/anterior. Politica vigente
no elimina negativa ni bloqueos globales. Metadatos guardados no verifican fuentes
reales; datos editables del tenant tampoco. Root v1/confirmation_blockers permanecen
intactos y POST continuar/confirmar siguen rechazados por reglas v1. No conecta
composicion v2 a autorizacion o accion mutadora, ni activa gates por politica de test.

26 pruebas nuevas: resolver fijo/instancias independientes/env ignorada, contratos
cerrados y versiones/coherencia (ambas rutas), HTTP preparado con una sola consulta
real de historial, GET repetido/parametros ignorados, aislamiento tenant, acciones
bloqueadas y borrador/historial intactos. Historia positiva se crea solo como fixture:
sin identidad/current/anterior; politica actual deshabilitada impide usarla para
confirmar. Retiro documental conserva identidad/evento; ultima negativa legacy
prevalece sobre positiva anterior con identidad. Flujo ordinario null verificado.
26 pruebas aprobadas; 29 HTTP previas aprobadas en validacion inicial.
Suite completa: 3189 passed en 279.29 s; Black/Ruff/diff --check correctos.

Proximo: prerequisitos puros versionados v2 de revision, separando negativos
parciales de positivos con composicion/politica actual; luego accion y decision
transversal v2 sin filtrar codigos v1, auditoria/politica real y concurrencia de
politica antes de habilitar. Fuentes complementarias/aceptacion siguen pendientes.
Ley fija; M3-T1 EN PROGRESO integral. Sin nueva migracion, commit ni push.


## §86 — Prerrequisitos puros de revision EIPD v2

2026-10-07. eipd_review_v2 implementa evaluador puro versionado con entrada
interna cerrada y revalidacion de modelos anidados mutados. Resultado inmutable:
decision, motivos ordenados/deduplicados y composicion opcional. Sin DB, permisos,
accion, resolver activo ni can_confirm.

Nucleo parcial compartido con v1 valida fecha explicita, request cerrado, borrador,
documento/contexto presentes y asociacion vigente. V1 conserva motivos, orden y
bloqueos fijos de positivos. requiere_cambios/no_continuar usan estos requisitos
parciales y no ejecutan composicion completa: faltantes ordinarios/documentales,
alto riesgo o politica deshabilitada no impiden registrar una negativa valida.

continuar compone v2 y conserva todos sus review_blockers, incluida politica,
fuentes, aceptacion, ruta, versiones y preparacion documental. No usa
confirmation_blockers ni exige revision positiva anterior: evita circularidad;
una negativa anterior o identidad de politica obsoleta no sustituye ni impide
por si sola la nueva revision. Confirmacion conserva sus controles propios.

110 pruebas nuevas cubren ambas rutas, negativos parciales, condiciones comunes,
positivos incompletos/deshabilitados, politica sintetica preparada, ausencia de
revision previa, historia negativa/obsoleta, contratos cerrados/modelos mutados,
fecha explicita e inmutabilidad. 148 pruebas focalizadas aprobadas, incluidas 38
v1; suite completa 3299 passed en 281.10 s. Black/Ruff/diff --check correctos.
Politica sintetica preparada solo prueba el evaluador; no activa producto real.

Proximo: integrar revision autenticada v2 con relectura bajo lock y politica
exclusiva de servidor deshabilitada, preservando negativos y metadatos; despues
decision transversal v2, auditoria/politica real y concurrencia de politica.
Fuentes complementarias/aceptacion pendientes; acciones/gates reales siguen v1
bloqueados en este paso. Ley fija; M3-T1 EN PROGRESO integral.
Sin nueva migracion, commit ni push.


## §87 — Revision autenticada con prerrequisitos v2 y politica de servidor

2026-10-07. La accion existente record_eipd_resolution_review_v1 conserva endpoint,
autenticacion/permiso edit_content, suscripcion, tenant y transaccion; usa ahora
prerrequisitos v2 para decidir. Bajo FOR UPDATE de serie relee borrador/versiones,
contexto actual desde M2 y documento antes de resolver politica fija deshabilitada.
Una consulta obtiene ultimo evento e identidad; fecha explicita comun. Los controles
v1 permanecen diagnosticos sin filtrar sus codigos; no determinan la nueva decision.

Negativas conservan requisitos parciales y pueden registrarse aun con documentos
incompletos o politica deshabilitada. Eventos nuevos guardan version/referencia/hash
de politica desde el servidor, junto a actor y hashes documentales existentes.
Identidad vigente no convierte una negativa en aprobacion ni habilita confirmacion.
Eventos historicos sin politica permanecen sin identidad; no backfill ni fallback.
Salida publica de evento conserva contrato previo; readiness expone su identidad v2.

continuar exige review_blockers v2 y sigue rechazado por fuentes/aceptacion pendientes
y activacion deshabilitada. Error 409 conserva issues/eipd_controls legacy y agrega
evaluation_version 2, issues_v2 y eipd_controls_v2. No exige positiva previa y no
escribe evento/documento al rechazar. Confirmacion y decision transversal siguen v1.
Cliente no aporta politica ni activa servidor mediante query o payload.

Diez pruebas HTTP nuevas: negativas parciales con identidad/actor de servidor,
ambas rutas preparadas con/sin negativa previa, composicion identica a readiness,
una consulta de historial, preservacion y cuatro rechazos de politica de cliente.
Prueba historica legacy conserva evento negativo sin identidad mediante fixture;
concurrencia real preparada ampliada con contexto/ultimo evento/identidad v2 tras
commit o rollback. 71 focalizadas aprobadas antes de ampliar aserciones concurrentes.
Suite completa: 3309 passed en 290.08 s, incluidas las aserciones concurrentes
ampliadas. Black/Ruff/diff --check correctos.

Proximo: decision transversal/confirmacion v2 bajo lock sin filtrar reglas v1;
auditoria/politica real, exitos y concurrencia de politica antes de habilitar.
Fuentes complementarias/aceptacion siguen pendientes. Ley fija; M3-T1 EN PROGRESO
integral. Sin nueva migracion, commit ni push.


## §88 — Decision transversal de confirmacion v2 bajo lock

2026-10-07. confirm_legal_assessment_v1 conserva endpoint/permisos/suscripcion,
FOR UPDATE de serie, relectura del borrador/versiones, justificacion, alcance,
vigencia RAT y validadores propios de las seis bases ordinarias. Antes de consultar
o reemplazar confirmado previo obtiene ultimo evento/identidad en una consulta y
construye composiciones v1/v2 con mismo contexto actual y fecha explicita.

Dentro del ambito EIPD (resolucion actual, detector positivo/revision o excepciones
de derechos), confirmation_blockers de v2 determinan la
decision. La composicion valida la frontera delimitada y rechaza las restantes;
no borra ni filtra codigos v1. Fuera de ese ambito las barreras transversales v1
siguen decidiendo. Validadores ordinarios y contexto RAT se ejecutan antes del gate.
Diagnosticos legacy special/eipd/confirmation_blockers/eipd_controls permanecen;
error agrega evaluation_version 2 y eipd_controls_v2. Politica exclusivamente del
resolver fijo deshabilitado; query del cliente no activa gates.

Identidad vigente por si sola no acredita decision positiva ni documentacion actual.
Eventos positivos historicos con identidad actual/anterior o sin identidad no
superan fuentes/aceptacion/activacion pendientes. Negativas conservan decision;
retirar documento mantiene historial y readiness v2 obsoleta/incompleta. El historial
por si solo no amplia el gate ordinario cuando no hay supuestos EIPD actuales.
Rechazo ocurre antes de escrituras/reemplazo del confirmado previo; sin migracion.

Once pruebas HTTP nuevas cubren ambas rutas y cinco historias (ausente, positiva
legacy, positiva con politica actual/anterior y negativa), coincidencia con readiness,
una consulta, query ignorada y preservacion de borrador/historial; caso ordinario
con historial y sin documento confirma sin ampliar el gate. La suite inicial
detecto seis regresiones de ese alcance y se corrigieron conservando el flujo previo. Concurrencia real preparada amplia aserciones v2 tambien
para confirmar tras commit/rollback, manteniendo confirmado previo y negativa.
61 pruebas previas aprobadas; 23 focalizadas posteriores aprobadas, once nuevas.
Tras corregir alcance/fixture: 54 focalizadas aprobadas. Suite completa final:
3320 passed en 287.70 s; Black/Ruff/diff --check correctos.

Proximo: contrato/auditoria de politica real y atomicidad de cambios de politica,
con evidencia de fuentes complementarias y aceptacion antes de habilitar. Resolver
continua deshabilitado; exitos de frontera habilitada y concurrencia de politica
siguen pendientes. Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §89 — Contrato de auditoria y seleccion transaccional de politica real

2026-10-07. Contrato detallado en m3-t1-eipd-politica-auditoria.md (DISENO).
Publicaciones inmutables con referencia unica/hash de servidor; selector global
revisionado y eventos append-only atomicos. Schema version 1 distinto de revision
del selector; publicar no selecciona. Reseleccion/revocacion requieren nueva
publicacion/referencia, sin promover revisiones historicas ni seleccionar vieja
politica habilitada. Canal administrativo separado del runtime/tenant.

Orden futuro selector FOR SHARE -> serie FOR UPDATE -> relecturas; seleccion usa
FOR UPDATE del selector sin locks de serie. Politica permanece estable hasta
commit/rollback. Requiere modificar uniformemente el orden actual antes de conectar
resolver real; §87/88 todavia usan artefacto fijo y lock de serie solamente.
Readiness orientativo coherente; integridad desconocida falla cerrado en ambito EIPD.
Historia sola no amplia gate ordinario. Negativas parciales admitidas con politica
valida deshabilitada, sin inventar identidad ante corrupcion del resolver.

Evidencia append-only de confirmacion excepcional futura asocia tenant/assessment,
evento humano, publicacion/revision/seleccion y hashes, atomicamente con reemplazo;
requiere contrato/migracion y RLS propios antes de habilitar exitos. Revocacion
conserva evidencia historica y bloquea acciones nuevas, sin mutar confirmados previos.
Matriz incluye privilegios, conflictos de revision, commit/rollback, cambios y
revocacion concurrentes, ambos sentidos de espera, tenants y ambas rutas.

Proximo: contratos/evaluadores puros de publicacion/seleccion/evidencia; despues
persistencia, privilegios/RLS, resolver/orden de locks y concurrencia/exitos antes
de fuentes/aceptacion y habilitacion real. Paso documental; diff --check correcto.
No se reejecuta suite por diseno sin codigo; ultima completa §88: 3320 passed.
Resolver deshabilitado. Ley fija; M3-T1 EN PROGRESO integral.
Sin nueva migracion, commit ni push.


## §90 — Contratos y evaluadores puros de auditoria de politica

2026-10-07. eipd_policy_audit.py implementa contratos internos cerrados/revalidados:
publicacion, evento de seleccion, selector, snapshot de auditoria, solicitud/plan
y evidencia de confirmacion. Modelos frozen, revisiones StrictInt y fechas con zona
normalizadas a UTC; constructores reciben id/actor/fecha explicitos de servidor.
Politica anidada conserva contrato §83; hash canonico calculado/comprobado, referencias
de publicacion unicas. Revalidacion desde python detecta modelos anidados mutados.

Snapshot valida publicaciones/eventos sin duplicados, cadena completa ordenada desde
bootstrap revision 1, hashes/identidad anterior, tiempos y selector igual al ultimo
evento. Sin eventos admite selector null solo como estado previo a bootstrap; no
es politica disponible para confirmar. Constructor de seleccion compara revision
esperada, exige publicacion registrada y no seleccionada previamente, genera evento
con revision consecutiva/identidad previa y selector coherente sin mutar entradas.
Publicar no selecciona; plan no escribe ni acredita permiso administrativo.

Evidencia pura exige selector coherente y recompone controles v2 con politica de la
publicacion actual, assessment/revision humana e identidad revalidados. Sin motivos
de confirmacion y sin tiempos invertidos, construye evidencia con tenant/assessment,
evento humano, publicacion/revision/seleccion, politica, hashes, actor y fecha.
Identidad sola o documento preparado no eluden negativos, obsolescencia, faltantes
ordinarios, politica deshabilitada ni otro tenant/assessment. Exito sintetico prueba
contrato; no confirma assessment real ni persiste evidencia.

65 pruebas nuevas: bootstrap/revocacion puros, contratos cerrados/hash/versiones,
StrictInt, falta de zona, duplicados/modelos mutados, revision esperada obsoleta,
publicacion desconocida/reseleccion, cadenas multiples/corrupcion/tiempos/plan,
evidencia de ambas rutas y rechazo de controles incompletos/historia impropia.
169 focalizadas aprobadas junto a 104 de politica/composicion §83.
Suite completa: 3385 passed en 293.55 s; Black/Ruff/diff --check correctos.

Pendiente persistencia/privilegios/RLS, autenticacion administrativa, historia completa
obtenida de DB, locks/atomicidad y resolver real. Modelos frozen no convierten objetos
anidados en almacenamiento inmutable; revalidacion protege fronteras puras, DB debera
impedir UPDATE/DELETE. Next: migracion append-only de control global y evidencia tenant
con pruebas PostgreSQL/RLS antes de servicios/resolver y cambio de orden de locks.
Fuentes/aceptacion pendientes, resolver fijo deshabilitado. Ley fija;
M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.


## §91 — Persistencia y privilegios de auditoria global EIPD

2026-10-07. Migracion append-only d73f518cbe42 sobre c62e407bad31 aplicada localmente:
eipd_policy_publications, eipd_policy_selections y eipd_policy_selector. Modelos ORM
alineados. Son controles globales, no datos de organizacion: sin tenant ficticio;
eventos humanos conservan sus tablas/RLS. Sin bootstrap ni politica activa insertada.

Publicacion almacena payload JSONB, version/referencia/hash, actor/fecha y evidencia.
Referencia unica; CHECK identidad/version/formato/textos y objeto JSONB con identidad
explicita. DB no recompone hash canonico ni verifica fuentes: futuro canal servidor
debe usar contratos puros §90 para validar payload completo/hash/fechas/autoridad.
FK de seleccion exige publicacion/hash registrados; revision unica/consecutiva,
identidad anterior completa y FK propia a revision/publicacion/hash anteriores.
Publicacion solo puede seleccionarse una vez. Selector singleton exige triple
revision/publicacion/evento coherente. Triggers de constraint diferidos comparan
selector con ultimo evento al finalizar transaccion: evento sin selector actualizado
falla al commit y rollback conserva estado anterior.

Rol eipd_policy_admin NOLOGIN/NOSUPERUSER/NOBYPASSRLS/NOCREATEROLE/NOCREATEDB,
separado y no asumible por app_user; sin concesion de membresia runtime. Migracion
rechaza rol preexistente incompatible o membresia runtime. Admin SELECT/INSERT en
control y UPDATE solo selector; sin UPDATE/DELETE/TRUNCATE de publicaciones/eventos.
RLS explicito de administracion y lectura autenticada global; app_user SELECT solo,
sin escritura/TRUNCATE. PUBLIC sin privilegios. Owner de migracion sigue privilegiado
para mantenimiento; append-only se exige a runtime/canal administrativo, no al owner.
Downgrade de esta migracion elimina tablas/triggers/funcion, conserva rol NOLOGIN
porque puede pertenecer a gestion de despliegue externa. No se reescriben migraciones
historicas ni eventos tenant. Rol no se expone como canal/API administrativa.

44 pruebas nuevas PostgreSQL: privilegios/flags/RLS, lectura sin/con autenticacion
y otro tenant, escrituras runtime y SET ROLE denegados, admin append-only y seleccion
atomica con rollback, trece corrupciones de publicacion/cadena/selector, fallo real
al commit por selector pendiente e inexistencia de publicacion tras rollback.
Fixtures solo datos sinteticos; limpieza owner elimina esos ids, no datos ajenos.
44 aprobadas en 2.98 s; Alembic check sin operaciones nuevas.
Suite completa: 3429 passed en 297.19 s; Black/Ruff/diff --check correctos.

Paso acotado al control global. Evidencia por tenant requiere siguiente migracion,
FK compuestas al assessment/evento humano/publicacion/seleccion y RLS/append-only;
no habilitar confirmacion excepcional antes de esa evidencia atomica. Resolver,
servicio administrativo, relectura/orden de locks y concurrencia de politica quedan
pendientes. Actualmente solo artefacto fijo deshabilitado, sin fuentes/aceptacion
verificadas. Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §92 — Persistencia append-only de evidencia de confirmacion tenant

2026-10-07. Migracion e84a629dcf53 sobre d73f518cbe42 aplicada localmente, sin editar
migraciones anteriores ni rellenar historicos. EipdConfirmationEvidence almacena
identidades tenant/assessment/review/publication/selection, revision del selector,
politica, hashes documento/contexto, actor y fecha. Una evidencia por assessment.
review_decision interno constante continuar permite FK a decision humana positiva;
no es input publico ni modifica el contrato puro §90.

Nuevas UNIQUE de soporte en publicaciones/eventos humanos y FK compuestas exigen:
assessment del tenant, review del mismo tenant/assessment con politica/hashes exactos
y decision continuar, publicacion con version/referencia/hash coincidentes y triple
revision/publicacion/evento de seleccion auditado. Metadatos legacy null o revision
negativa no pueden acreditar evidencia; claves no reescriben eventos existentes.
CHECK version/revision/referencia/hashes; FK sin cascadas conservan procedencia.

RLS SELECT tenant via auth_org_ids. app_user SELECT/INSERT, sin UPDATE/DELETE/TRUNCATE;
PUBLIC y eipd_policy_admin sin privilegios sobre evidencia. INSERT exige actor JWT,
tenant accesible, assessment borrador con documento, ultima revision humana y
selector actual con publicacion declarada habilitada. Actor de publicacion no recibe
por ello acceso a evidencia tenant. Lectura historica no depende del selector actual:
revocacion conserva evidencia original. Owner de mantenimiento permanece privilegiado.

Estas barreras de DB no recomponen controles documentales/hash ni verifican fuentes,
roles de API o atomicidad de la seleccion durante espera. Servicio futuro debe usar
constructor puro §90, permisos, relecturas y orden de locks §89; no existe endpoint
para insertar evidencia ni conexion de confirmacion real en este paso. Fixtures
siembran politica/positivas sinteticas mediante owner, no mediante accion continuar.
Sin evidencia atomica integrada y fuentes/aceptacion, resolver fijo deshabilitado.

29 PostgreSQL nuevas: lectura/escritura runtime y tenant cruzado, UTC, append-only,
actor suplantado, borrador/documento/revision posterior/anonimo, trece enlaces falsos,
unicidad, rollback conjunto de evidencia/estado y revocacion con historia intacta.
Negativas/legacy fallan FK incluso usando owner sin RLS. Ajuste de limpieza de
fixtures elimina evidencia antes de reviews y controles sinteticos TEST de actores
de prueba antes de perfiles; scope asíncrono y campos lifecycle alineados.
105 focalizadas aprobadas antes de los tres casos finales; 29 nuevas finales
aprobadas en 3.70 s. Alembic check sin operaciones nuevas.
Suite completa: 3458 passed en 302.51 s; Black/Ruff/diff --check correctos.

Proximo: servicio administrativo de publicacion/seleccion y resolver de lectura
validada, aun sin politica real habilitada; despues locks compartidos/orden uniforme
y evidencia atomica en confirmacion, concurrencia/exitos y fuentes/aceptacion.
Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §93 — Servicios internos de publicacion/seleccion y lectura auditada

2026-10-07. eipd_policy_store.py implementa publish_eipd_policy_v1,
select_eipd_policy_v1, read_eipd_policy_audit_snapshot_v1 y
read_selected_eipd_policy_v1. Sin endpoint administrativo, migracion nueva ni
conexion al resolver de acciones/readiness actuales. Solo canal DB current_user
exacto eipd_policy_admin escribe mediante estos servicios; app_user y owner normal
rechazados en la frontera del servicio. Ese rol acredita canal, no identidad personal:
caller administrativo futuro debe autenticar actor de plataforma y gestionar
commit/rollback. Actor explicito validado por contrato/FK, no tomado del tenant.

Publicar genera UUID/fecha de servidor (clock_timestamp), hash canonico y payload
cerrado via §90; referencia repetida rechazada antes de escritura. No selecciona.
Seleccionar valida solicitud cerrada/revision esperada, adquiere advisory lock
transaccional 719093 y luego FOR UPDATE del selector, relee auditoria, genera plan,
inserta evento y cambia selector en la misma transaccion. No commit interno ni locks
de serie. Advisory serializa tambien bootstrap cuando fila de selector no existe;
siempre precede selector en este canal. Error/rollback no deja evento parcial.

Lectura usa una sola sentencia SQL con aggregates del catalogo completo, cadena
ordenada y selector, bajo snapshot MVCC comun; mapea columnas explicitas a contratos
§90 y comprueba identidad/payload/hash/cadena/tiempos. Datos corruptos, selector
faltante o lectura runtime sin autenticacion no generan fallback habilitado.
Publicacion sin selector es estado de bootstrap, no politica disponible. Leer no
escribe/cachea ni garantiza estabilidad posterior hasta commit. No usar esta lectura
orientativa como resolver transaccional de confirmacion sin locks compatibles.

El canal de publicacion/seleccion admite exclusivamente activacion deshabilitada;
objetos sinteticos habilitados rechazados aun si cumplen schema/evidencia declarada.
No comprueba fuentes reales ni interpreta fechas como activacion. Artefacto fijo
resolve_eipd_gate_policy_v1 permanece intacto/deshabilitado en acciones actuales.

24 PostgreSQL nuevas: publicacion/bootstrap y campos servidor, permisos de canal,
una consulta y autenticacion, extra/StrictInt/target desconocido/revision obsoleta/
reseleccion/referencia repetida/activacion, corrupcion catalogo/hash/payload/tiempos/
selector, rollback y cuatro concurrencias reales con pg_blocking_pids: bootstrap y
seleccion existentes, commit y rollback. Segundo escritor relee revision despues de
espera; commit hace solicitud obsoleta, rollback permite plan sucesor. Fixtures
limpian controles TEST del actor sintetico por prueba, ademas de limpieza de sesion.
24 aprobadas en 2.37 s; Black/Ruff correctos.
Suite completa: 3482 passed en 315.74 s; Black/Ruff/diff --check correctos.

Proximo: resolver transaccional de lectura con bloqueo compartido seguro y orden
selector -> serie en acciones, manteniendo politica deshabilitada; integrar evidencia
atomica despues y validar concurrencia/exitos antes de fuentes/aceptacion/activacion.
Privilegios runtime solo SELECT se conservan: resolver con lock requiere mecanismo
limitado compatible con esos privilegios, no conceder UPDATE global al runtime.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.


## §94 — Resolver transaccional con bloqueo compartido limitado

2026-10-07. Migracion append-only f95b73aed064 sobre e84a629dcf53 aplicada localmente.
Funcion public.lock_eipd_policy_selector_v1() sin argumentos, SECURITY DEFINER,
search_path fijo pg_catalog y objetos de dominio calificados. Comprueba JWT auth.uid
con perfil registrado antes de bloquear; advisory xact lock compartido 719093 y
selector singleton FOR SHARE. Devuelve solo existencia; no escribe/publica/selecciona
ni revela datos tenant. EXECUTE solo app_user, retirado de PUBLIC/admin; runtime
conserva SELECT y no recibe UPDATE, INSERT de control ni BYPASSRLS.

Helper lock_eipd_policy_selector_v1 exige READ COMMITTED, invoca funcion y rechaza
selector ausente sin fallback/bootstrap. resolve_eipd_policy_snapshot_for_transaction_v1
lee y revalida auditoria despues de esperar, manteniendo locks hasta commit/rollback
del caller. Sin cache ni commits internos. READINESS orientativo §93 sigue separado.
Advisory compartido serializa tambien frente al bootstrap administrativo exclusivo;
lectores de distintos tenants pueden coexistir. Orden previsto de acciones pasa a
advisory compartido -> selector compartido -> serie exclusiva. Canal administrativo
§93 advisory exclusivo -> selector exclusivo, sin series; PATCH solo serie.

Garantia frente al canal administrativo que respeta ese protocolo y publicaciones
append-only; owner de mantenimiento permanece privilegiado. Actor registrado solo
acredita acceso a bloqueo global, no permisos de accion/tenant ni revision humana.
Resolver transaccional aun no conectado a acciones; estas siguen con artefacto fijo
deshabilitado y lock de serie actual. No introducir lock de selector despues de serie:
conexion siguiente debera cambiar orden uniformemente y releer controles/contexto.

15 PostgreSQL nuevas: atributos/permisos de funcion, anonimo/UUID sin perfil, selector
ausente, aislamiento no admitido, lectores compartidos entre tenants, dos variantes
admin esperando a lector y cuatro lector esperando a admin (bootstrap/seleccion,
commit/rollback), corrupción de hash/payload sin fallback. pg_blocking_pids demuestra
espera real; commit/rollback libera locks y relectura coincide con seleccion nueva/
anterior o ausencia. 39 focalizadas aprobadas con 24 del servicio §93 en 3.66 s.
Alembic check sin operaciones nuevas; Black/Ruff correctos.
Suite completa: 3497 passed en 309.60 s; Black/Ruff/diff --check correctos.

Proximo: integrar orden de locks y snapshot auditado en revision/confirmacion,
con selector deshabilitado explicitamente registrado y errores cerrados si falta;
evidencia atomica, concurrencia de acciones, autoridad administrativa personal y
fuentes/aceptacion antes de habilitar. No bootstrap supuesto ni promocion de historia.
Ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §95 — Revision humana conectada al selector auditado deshabilitado

2026-10-07. POST eipd-resolution/reviews adquiere advisory compartido y selector
FOR SHARE mediante §94 antes del lock FOR UPDATE de serie. Despues de ambos locks
relee borrador, contexto M2 y auditoria completa, y evalua v2 con la publicacion
seleccionada. Historial y diagnostico v1 conservados. Evento negativo guarda version,
referencia y hash de esa publicacion; nunca politica del cliente ni identidad fija
como fallback. Permisos/tenant/suscripcion siguen en dependencias autenticadas.
Locks permanecen hasta commit/rollback del caller; no commits internos.

Selector ausente o auditoria/hash/payload incoherentes devuelve 409 con codigo
politica_eipd_no_disponible, sin evento ni cambio de borrador. Publicacion habilitada
rechazada explicitamente (politica_eipd_habilitada_no_admitida): este paso no habilita
positivas ni excepciones. Runtime no publica/selecciona ni hace bootstrap. Para usar
revision se requiere selector deshabilitado registrado por canal autorizado; ninguna
migracion o accion tenant crea ese selector automaticamente.

Nueve pruebas nuevas con PostgreSQL/app_user: dos decisiones negativas/identidad real,
orden SQL selector antes de serie y lectura posterior, tres fallos cerrados, cuatro
concurrencias reales observadas por pg_blocking_pids: revision espera seleccion
administrativa commit/rollback y registra nueva/anterior identidad; administrador
espera fin de transaccion de revision commit/rollback, con evento persistido/revertido.
Fixtures HTTP existentes registran explicitamente artefacto deshabilitado conocido
por canal interno de test y limpian solo su publicacion/selector; no simulan fallback
ni credenciales administrativas de produccion. 33 HTTP anteriores y nueve nuevas
aprobadas focalmente. Suite completa: 3506 passed en 313.64 s; Black/Ruff/Alembic check/diff correctos.

Alcance de este checkpoint: revision humana exclusivamente. Confirmacion y readiness
v2 aun usan artefacto fijo deshabilitado; cuando selector tiene identidad diferente,
readiness puede mostrar revision obsoleta respecto de su politica fija. Esa consulta
es orientativa y no acredita vigencia contra selector real hasta siguiente integracion.
No cierre del control global ni activacion. Proximo: conectar readiness y confirmacion
al mismo selector con orden compatible, preservando ordinario sin EIPD/historia sola;
luego evidencia atomica, autoridad personal, matriz de exitos y fuentes/aceptacion.
Ley fija; M3-T1 EN PROGRESO integral. Sin migracion, commit ni push.


## §96 — Preparacion y confirmacion con el mismo selector auditado

2026-10-07. Readiness v2 lee publicacion seleccionada mediante snapshot SQL completo
validado y sin locks/escrituras. Ya no compone con artefacto fijo: politica, hash y
estado de identidad humana corresponden al selector real. Es consulta orientativa,
no garantiza estabilidad hasta una accion. Selector ausente/corrupto en su ambito
EIPD devuelve 409 politica_eipd_no_disponible, sin fallback ni bootstrap.

Confirmacion adquiere advisory compartido -> selector FOR SHARE si existe -> serie
FOR UPDATE, antes de releer borrador/contexto M2/controles. Helper exige READ COMMITTED;
require_selector=False solo permite adquirir advisory aun sin fila para conservar
ordinarios sin EIPD. Ambito de gate revalidado bajo serie conserva §88: documento,
deteccion requiere EIPD/revision o expedientes de excepcion; historia sola no amplía
ambito de confirmacion. Si entra al ambito, exige snapshot seleccionado validado
tras ambos locks; ausencia/incoherencia bloquea antes de reemplazar confirmado.
Bootstrap/seleccion administrativos esperan advisory; PATCH solo serie, sin inversion.

Revisiones, readiness y confirmacion usan helper compartido que admite unicamente
activacion deshabilitada. Politica habilitada aun rechazada con codigo
politica_eipd_habilitada_no_admitida, aunque una fixture privilegiada la insertase.
Sin politica client-side, nueva migracion, seed productivo ni commits internos.
Todavia no se conecta escritura de evidencia de confirmacion EIPD: ninguna ruta
excepcional se habilita en este checkpoint. No promociona revisiones historicas.

Trece PostgreSQL/app_user nuevas: ambas rutas coinciden entre revision/consulta/error
de confirmacion; reseleccion cambia hash y vuelve obsoleta revision; seis casos de
selector ausente/hash/extra en preparacion/confirmacion conservan borrador/eventos;
ordinario sin selector confirma y no crea selector/evidencia; cuatro concurrencias
reales observadas con pg_blocking_pids, confirmacion esperando admin commit/rollback
y admin esperando fin de transaccion de confirmacion bloqueada commit/rollback.
13 aprobadas en 5.68 s; 221 focalizadas de confirmacion/preparacion aprobadas en
20.40 s. Dobles unitarios de confirmacion declaran politica/lock simulados, mientras
HTTP y PostgreSQL verifican comportamiento real. API Licitud historica tambien
registra selector explicito; 53 regresiones verificadas en 76.42 s. Suite completa: 3519 passed en 329.62 s; Black/Ruff/Alembic check/diff correctos.

Proximo: conectar evidencia de confirmacion atomica y validar fallos/reemplazo y
exitos sinteticos antes de habilitar; autoridad administrativa personal, fuentes
complementarias y aceptacion tecnica trazable pendientes. Ley fija; EN PROGRESO
integral. Sin commit ni push. §95 tambien sigue pendiente de commit.


## §97 — Evidencia de confirmacion conectada a la transaccion

2026-10-07. Servicio interno eipd_confirmation.record_eipd_confirmation_evidence_v1
relee snapshot auditado, recompone controles con constructor puro §90 y genera UUID
y fecha UTC de servidor (clock_timestamp). Inserta EipdConfirmationEvidence y flush,
sin commit, endpoint ni parametros de evidencia del cliente. Caller conserva locks
selector -> serie y arma contexto actual; DB §92 verifica tenant/JWT/borrador/ultima
revision positiva y FK exactas de politica/documento/contexto/seleccion.

Confirmacion llama servicio solo tras aprobar controles v2 en ambito EIPD y antes
de leer/modificar confirmado anterior. Borrador debe seguir borrador al insertar
por RLS; evidencia, reemplazo y confirmacion quedan en misma transaccion del caller.
ValueError/contrato no preparado devuelve 409 evidencia_eipd_no_preparada; errores
DB/flush propagan para rollback. Si cualquier paso falla, no conserva evidencia ni
reemplazo parcial. Ordinario fuera de EIPD no inserta evidencia. No commits internos.

Guardia §96 se conserva: politica habilitada rechazada en la aplicacion. Exitos
excepcionales solo se ejercitan en pytest con politica/positiva sinteticas insertadas
por owner de fixtures y override local de _selected_disabled_eipd_policy_v1. No flag,
variable de entorno, endpoint o bypass de produccion. Constructor/relectura/gates,
RLS y persistencia real no se simulan; ninguna fuente de fixture acredita verificacion
real ni aceptacion tecnica de politica productiva.

Doce pruebas PostgreSQL/app_user nuevas: dos guardias reales rechazan habilitada sin
evidencia; cuatro exitos sinteticos (ambas rutas, con/sin confirmado previo) conservan
identidad exacta/actor/fecha y evidencia unica, segundo intento no duplica; cuatro
fallos con anterior confirmado revierten evidencia/borrador/anterior (FK real de
insercion, fallo tras evidencia, tras reemplazo y tras flush final); dos controles
fallidos (negativa/identidad obsoleta) prueban que no se intenta insertar evidencia.
12 aprobadas en 4.59 s. Fixtures limpian evidencia antes de revision/politica y RAT.
Suite completa: 3531 passed en 334.47 s; Black/Ruff/Alembic check/diff correctos.

Proximo: concurrencia de confirmaciones exitosas y revocacion tras exito con evidencia
historica preservada, dos series/tenants, y autoridad administrativa personal antes
de fuentes complementarias/aceptacion/activacion. M3-T1 EN PROGRESO integral, ley fija.
Sin migracion, commit ni push; §§95–97 pendientes de commit.


## §98 — Concurrencia exitosa y revocacion con evidencia preservada

2026-10-07. Se amplía matriz PostgreSQL/app_user; sin cambio de comportamiento ni
activacion productiva. Reutiliza politica/positiva owner sinteticas y override local
de guardia de pytest de §97. Servicios de confirmacion, constructor, RLS/FK, locks,
seleccion administrativa deshabilitada y commits/rollbacks son reales.

Doce pruebas nuevas, ambas rutas sensible/sensible-biometrica, con pg_blocking_pids
para demostrar espera efectiva y timeout acotado, no inferir bloqueo por sleep:

- Dos confirmaciones de misma evaluacion/serie con anterior confirmado: primer commit
  deja segunda en 409 al releer status; primer rollback permite exito de segunda.
  En ambos casos queda una evidencia exacta y un reemplazo, sin duplicacion. Evidencia
  no es visible desde otra transaccion antes de commit.
- Administrador intenta seleccionar nueva politica deshabilitada mientras confirmacion
  exitosa conserva locks: espera hasta commit/rollback. Tras commit evidencia original
  se conserva campo por campo y confirmado mantiene status; tras rollback no queda
  evidencia. Seleccion deshabilitada posterior bloquea accion siguiente con identidad
  humana obsoleta y gate_eipd_no_habilitado. Sucesor/positiva historica de test no se
  promocionan ni reemplazan confirmado tras revocacion.
- Confirmacion comienza mientras revocacion tiene lock exclusivo: tras commit revalida
  politica deshabilitada y rechaza sin evidencia/status; tras rollback usa seleccion
  original habilitada sintetica y confirma con evidencia de revision 1.

12 aprobadas en 5.78 s. Fixtures restauran selector previo solo mediante owner para
limpieza tras aserciones, borran publicacion/evento sucesor de test y luego limpian
estado original. Esa restauracion no es canal de rollback/reseleccion productivo:
contrato real sigue exigiendo publicacion nueva. Sin flags/env/endpoints nuevos.
Suite completa: 3543 passed en 343.50 s; Black/Ruff/Alembic check/diff correctos.

Proximo: ampliar exitos concurrentes a series independientes/tenants y PATCH, despues
resolver autoridad personal administrativa; fuentes complementarias y aceptacion
tecnica trazable pendientes antes de habilitar. M3-T1 EN PROGRESO integral; ley fija.
Sin migracion ni cambio de servicios, commit o push; §§95–98 pendientes de commit.


## §99 — Exitos de series/tenants independientes y PATCH concurrente

2026-10-07. Ampliacion de pruebas PostgreSQL/app_user, sin cambios de servicios,
privilegios, migraciones ni activacion. Politica/positivas sinteticas y override
pytest local de guardia §97 conservados. Fixture owner prepara segundo RAT real
(tratamiento/finalidad/categorias/titulares), serie y borrador documental equivalentes
en misma organizacion o en organizacion B; contexto se valida con constructor M2 real,
no sustitucion de builder/gates/RLS. IDs/actores/revisiones diferentes por serie.

Doce nuevas, ambas rutas sensible/sensible-biometrica:

- Cuatro exitos de series independientes (misma org/dos orgs): segunda confirma antes
  de terminar transaccion de primera, ambas conservan locks compartidos de selector.
  Evidencia de cada una invisible antes de commit; despues existe una por evaluacion,
  con actor correspondiente. RLS muestra ambas al mismo tenant o solo propia entre
  tenants, y servicio cruzado devuelve 404 sin acceso.
- Ocho PATCH/confirmacion (misma org/dos orgs, commit/rollback): PATCH parcial toma
  serie A; confirmacion A espera realmente (pg_blocking_pids) manteniendo selector
  compartido. Confirmacion B avanza y hace commit mientras A sigue esperando. Commit
  de PATCH invalida controles revalidados de A y bloquea sin evidencia; rollback
  permite exito de A con evidencia. No se revierte ni sobrescribe evidencia de B.

12 aprobadas en 6.64 s; timeout acotado para detectar espera indebida. Fixtures limpian
primero evidencia/revision y despues borrador/serie/RAT B antes de limpiar politica A.
Clonado owner es preparacion sintetica de pruebas, no via nueva de producto ni
promocion de positivos historicos. Guardia de habilitadas en aplicacion conservada.
Suite completa: 3555 passed en 345.51 s; Black/Ruff/Alembic check/diff correctos.

Proximo: definir/implementar autoridad personal del canal administrativo de politica,
con permisos separados de roles tenant; fuentes complementarias y aceptacion tecnica
trazable antes de habilitar. No cierre integral ni validacion juridica por total de
pruebas. M3-T1 EN PROGRESO integral; ley fija. Sin commit ni push.


## §100 — Contrato de autoridad personal administrativa

2026-10-07. Paso documental previo a implementar autorizacion personal. ADR 0001
establece profiles.is_superadmin como autoridad global, independiente de membresias.
get_current_profile valida JWT mediante extract_auth_identity, establece sub local y
aprovisiona perfil sin promoverlo; require_superadmin comprueba bandera. Canal EIPD
actual _require_admin solo verifica current_user=eipd_policy_admin; actor_id recibido
por servicios internos no acredita por si mismo identidad personal autenticada.

Contrato elegido: exigir simultaneamente identidad JWT verificada por servidor,
perfil global superadmin vigente y conexion administrativa separada. Actor de auditoria
se deriva del perfil autorizado; nunca de actor_id/client payload, accepted_by,
verified_by, X-Organization-Id ni roles owner/admin/editor de organizacion. app_user
no recibe membresia del rol administrativo ni credenciales owner. JIT no promueve;
sin identidad, perfil, permiso o canal adecuado, rechazar antes de publicar/seleccionar.
No crear API administrativa operativa hasta completar barreras y pruebas.

Precondicion descubierta en codigo: migracion 0001 otorga CRUD de todas las tablas
public a app_user y no incluye profiles en lista RLS; 0002 agrega is_superadmin.
Las migraciones revisadas no acreditan proteccion suficiente de columnas de identidad/
autoridad. Esto es hallazgo de codigo, no prueba de explotacion ni comprobacion de
privilegios efectivos en despliegues. Proximo paso debe auditar privilegios reales y
proteger auth_user_id/id/is_superadmin frente a insercion/actualizacion suplantada,
promocion y borrado runtime. Mantener JIT legitimo y cambios de datos de perfil
permitidos; no conceder promocion por rol tenant. Migracion nueva append-only.

Orden administrativo previsto: autoridad personal estabilizada (lectura protegida de
perfil) -> advisory exclusivo -> selector exclusivo; nunca serie. Revocacion personal
concurrente debe tener resultado definido: aplicada antes de autorizar rechaza, o
espera fin de operacion ya autorizada bajo lock. No confiar solo en objeto ORM/cache
anterior a espera. Funcion DB limitada, si se utiliza, exige canal administrativo,
search_path seguro y permisos minimos; no autentica criptograficamente JWT por si sola.
Caller debe propagar sub verificado a conexion administrativa en transaccion local,
sin fuga de identidad entre conexiones de pool. Actor/fecha/hash siempre servidor.

Matriz obligatoria: anonimo/JWT invalido/perfil ausente; tenant owner/admin sin bandera;
actor suplantado; superadmin autenticado por canal incorrecto; canal correcto sin
identidad; JIT sin autopromocion; SQL runtime no altera autoridad/identidad; revocacion
personal commit/rollback antes/durante espera; aislamiento del contexto local del pool;
auditoria exacta del actor; rollback sin publicacion/seleccion parcial. Superadmin
legitimo sin membresia tenant puede administrar solo por canal separado autorizado.

Sin cambio de servicios, permisos, migraciones, pruebas ejecutables ni activacion en
este checkpoint. Ultima suite ejecutada: 3555 passed §99; no se presenta como prueba
del contrato nuevo. Autoridad personal todavia NO implementada. Fuentes/aceptacion
pendientes; ley fija; M3-T1 EN PROGRESO integral. Sin commit ni push.


## §101 — Proteccion de identidad y autoridad de perfiles

2026-10-07. Auditoria local efectiva antes del cambio con conexion app_user confirma
INSERT/UPDATE/DELETE de profiles y UPDATE de is_superadmin permitidos. Hallazgo §100
confirmado para base local; no se extrapola a despliegues externos. Migracion nueva
append-only a06c84bf175e sobre f95b73aed064 aplicada localmente.

Revoca INSERT/UPDATE/DELETE/TRUNCATE de tabla profiles para app_user; conserva SELECT
existente y concede INSERT solo auth_user_id/email/full_name, UPDATE solo email/
full_name/updated_at. ID por default DB y is_superadmin=false por default; no INSERT
explicito de ID/autoridad ni UPDATE identidad/autoridad. Sin concesiones al canal EIPD.
Trigger SECURITY INVOKER/search_path pg_catalog exige auth.uid() no nulo y matching
NEW.auth_user_id para runtime; UPDATE ademas acredita identidad OLD y rechaza cambio
de ID/auth_user_id/is_superadmin. Cambios basicos de perfil ajeno rechazados. Funcion
no obtiene privilegios elevados; EXECUTE retirado de PUBLIC/app_user/eipd_policy_admin,
trigger realiza validacion. Owner de mantenimiento conserva atribuciones explicitas.

JIT get_current_profile conserva INSERT de columnas permitidas/ON CONFLICT DO NOTHING,
perfil nuevo sin promocion y RETURNING/SELECT. No cambia API/autenticacion/JWT ni
activa canal administrativo. Proteccion no representa RLS completo de perfiles:
SELECT anterior se conserva y administracion personal EIPD aun pendiente. Downgrade
restaura grants anteriores de CRUD y retira trigger/permisos de columna nuevos;
es reversion de seguridad, no necesaria para operar upgrade.

Doce PostgreSQL/app_user nuevas: privilegios efectivos, JIT idempotente y update basico
propio, cuatro INSERT forjados (anonimo/otra identidad/promocion/ID explicito), seis
mutaciones denegadas (promocion/auth_user_id/ID/borrado/truncate/datos ajenos).
22 focalizadas con autenticacion aprobadas en 0.51 s. No datos reales alterados por
pruebas; insercion/actualizacion propia de test revertida por rollback.
Suite completa: 3567 passed en 431.30 s; Black/Ruff/Alembic check/diff correctos.

Proximo: implementar autorizacion personal transaccional del canal EIPD (JWT verificado,
perfil superadmin vigente, actor derivado y rol separado), locks/revocacion/pool y
pruebas; fuentes/aceptacion antes de activar. Ley fija; EN PROGRESO integral.
Sin commit ni push; §100 documental tambien pendiente de commit.


## §102 — Barrera personal transaccional limitada

2026-10-08. Migracion append-only b17d95c0286f sobre a06c84bf175e aplicada localmente.
public.lock_eipd_personal_authority_v1() sin argumentos retorna UUID de perfil derivado
de auth.uid(); exige perfil existente con is_superadmin=true. SELECT perfil FOR SHARE
antes de evaluar autoridad; retiene lock hasta commit/rollback. Funcion SECURITY
DEFINER con search_path pg_catalog y referencias calificadas, EXECUTE solo rol
administrativo EIPD (owner mantenimiento privilegiado); app_user sin EXECUTE, canal
administrativo sin UPDATE de perfiles ni elevacion nueva. No publica ni selecciona.

Helper authorize_eipd_personal_actor_v1 exige current_user=eipd_policy_admin y
READ COMMITTED; invoca funcion, sin actor del cliente/cache/commit. Sub debe provenir
de JWT verificado por caller y propagarse localmente a conexion separada. Funcion SQL
no verifica criptografia del JWT. Orden previsto perfil -> advisory -> selector,
sin series. No endpoints, configuracion de pool/credenciales ni bootstrap nuevos.

Nueve PostgreSQL nuevas: anonimo/perfil desconocido/owner tenant rechazados; superadmin
por canal runtime rechazado incluso al invocar funcion directamente; atributos,
privilegios y actor exacto derivados; sub local desaparece tras rollback. Cuatro
concurrencias con pg_blocking_pids: revocacion previa commit rechaza tras esperar,
rollback permite autorizacion; revocacion posterior espera fin de transaccion personal
(commit/rollback). Actor global dedicado sintetico sin membresia tenant, limpiado
por owner; no se promueven perfiles de usuarios reales. 45 focalizadas con proteccion
de perfiles/servicios de politica aprobadas en 3.37 s; Black/Ruff/Alembic check correctos.
Ultima suite completa sigue 3567 §101; no se registra total nuevo sin ejecutarla.

Limite: barrera todavia NO conectada a publish/select ni a API/canal autenticado.
Servicios internos conservan contrato confiable anterior actor_id; rol DB solo aun
no acredita persona para escritores. Proximo: integrar barrera antes de locks/global
writes, actor derivado y rechazo de suplantacion, ajustar fixtures y suite completa;
despues transporte autenticado/pool y fuentes/aceptacion antes de habilitar.
Ley fija; EN PROGRESO integral. Sin commit ni push.


## §103 — Escritores con entrada personal y actor derivado

2026-10-08. publish_eipd_policy_v1/select_eipd_policy_v1 ya no aceptan actor_id.
Invocan authorize_eipd_personal_actor_v1 antes de escribir/adquirir locks globales;
actor auditable se deriva de perfil superadmin bloqueado. Seleccion: perfil FOR SHARE
-> advisory exclusivo -> selector FOR UPDATE, sin serie ni commit interno. Solicitud
sin identidad/canal/autoridad falla antes de mutaciones; actor forjado no es argumento
admitido. Politicas habilitadas siguen rechazadas por el canal de publicacion/seleccion.

Primitivas anteriores se renombran _publish_eipd_policy_v1/_select_eipd_policy_v1,
privadas de persistencia para caller confiable. No endpoints ni entrada personal;
DB rol sigue canal privilegiado y no valida criptograficamente sub por si solo.
Fixtures antiguas usan explicitamente primitivas privadas para preparar politica/
metadatos sinteticos, sin promover perfiles tenant ni simular nuevas barreras. Las
pruebas nuevas ejercitan entradas personales reales y actor global dedicado sin
membresia tenant. Transporte futuro debe usar exclusivamente entradas personales y
propagar sub de JWT verificado, con conexion separada y contexto local del pool.

Once PostgreSQL nuevas: publicacion/seleccion exactas con actor derivado, seis rechazos
(anonimo/desconocido/tenant para ambos escritores) conservan catalogo, superadmin por
runtime rechazado, dos argumentos actor_id forjados rechazados sin escritura, rollback
conjunto de publicacion/evento/selector. 44 focalizadas con autoridad personal y
servicios de persistencia aprobadas en 4.41 s.
Suite completa: 3587 passed en 348.04 s; Black/Ruff/Alembic check/diff correctos.

Sin nueva migracion sobre b17d95c0286f. No API administrativa operativa, pool/config/
credenciales nuevas ni activacion real. Proximo: transporte administrativo autenticado
con canal DB separado/contexto transaccional local y pruebas de permiso/revocacion/
pool; despues fuentes complementarias y aceptacion tecnica trazable. Ley fija;
EN PROGRESO integral. Sin commit ni push; §102 tambien pendiente de commit.

## §104 — Pool separado y dependencia autenticada EIPD (2026-10-08)

Se incorpora `EIPD_ADMIN_DATABASE_URL` opcional y secreta, sin valor por defecto ni
fallback a DATABASE_URL/APP_DATABASE_URL. El pool se crea de forma diferida,
READ COMMITTED, sin echo y con parametros ocultos. No se cambia .env ni se
provisionan credenciales reales: el login debe provisionarse por mantenimiento.

`get_eipd_admin_db` valida el bearer con extract_auth_user_id (JWT existente)
antes de obtener el pool. Requiere login dedicado LOGIN/NOINHERIT, sin superuser,
BYPASSRLS, CREATEDB, CREATEROLE, REPLICATION, propiedad de relaciones ni membresias
directas adicionales; miembro de eipd_policy_admin. Rechaza owner y app_user.
SET LOCAL ROLE eipd_policy_admin y sub parametrizado/local preceden la barrera
personal FOR SHARE. No usa JIT, organizacion del header ni actor del payload.
La dependencia gestiona commit/rollback; el lock personal dura la transaccion.

17 pruebas nuevas, con login/password sinteticos efimeros y pool real de una
conexion: JWT ausente/invalido antes de pool, configuracion ausente/invalida,
identidad derivada, reutilizacion del mismo backend tras commit/rollback sin
sub/rol residual, tenant/desconocido/revocado rechazados, owner/app_user rechazados,
y privilegios excesivos bloqueados. Las pruebas de JWT del modulo existente y
las barreras/escritores anteriores se ejecutan juntas: 47 passed en 3.18 s.
Suite completa: 3604 passed en 352.09 s; Black/Ruff/Alembic check/diff correctos.

No nueva migracion, rutas administrativas ni activacion operativa. La validacion
criptografica se reutiliza; los tests de pool inyectan la identidad extraida y
no acreditan una ruta HTTP integrada. Pendiente conectar endpoints publicacion/
seleccion a esta dependencia, validar HTTP/JWT real y concurrencia de revocacion
por transporte; luego fuentes/aceptacion y despliegue/provision controlados.
Ley 21.719/19.628 reformada sigue base fija; M3-T1 EN PROGRESO integral y
activacion excepcional bloqueada. Sin commit/push en este paso.

## §105 — Rutas administrativas EIPD con JWT/pool real (2026-10-08)

Se registran POST /admin/eipd/publications y POST /admin/eipd/selections en la API.
PublicationRequest exige policy/rationale/evidence_reference; SelectionRequest exige
publication_id/expected_revision/rationale/evidence_reference. Esquemas cerrados,
revision StrictInt; actor/UUID/reloj/hash/evento se generan o derivan en servidor.
Se reutilizan entradas personales §103 y dependencia §104, nunca primitivas privadas
ni require_superadmin/JIT/DB tenant. Organizacion del header no concede autoridad.

201 devuelve publicacion o plan evento/selector; cada request tiene su propia
transaccion. Publicar no selecciona automaticamente. 401 token ausente/invalido;
403 identidad verificada sin perfil superadmin vigente; 503 JWKS/pool ausente o
canal inapropiado. 422 cuerpo/campos adicionales; 409 rechazo de dominio/revision
obsoleta/referencia repetida. Unique violation de publicacion tambien se traduce
a 409 para la carrera potencial, sin exponer mensajes SQL. Esa carrera concurrente
queda pendiente de matriz HTTP del siguiente paso; no acreditada por test secuencial.

38 pruebas HTTP nuevas usan app registrada, JWT ES256 real con par de claves y
JWKS sintetico, y pool PostgreSQL/login limitado reales. Cubren publicacion seguida
de seleccion y visibilidad de commit con actor derivado, pool limpio, seis formas
de token invalido por ambas rutas antes de pool, tenant/desconocido/revocado,
campos auditables de cliente rechazados, duplicado/revision obsoleta/desconocido,
publicacion habilitada bloqueada, fallo de commit con rollback sin respuesta exitosa,
JWKS caido, configuracion ausente y owner/app_user rechazados. Sin reemplazar
extract_auth_user_id ni dependencias de autoridad/escritores en pruebas HTTP.
85 focalizadas con pool/autoridad/escritores/autenticacion anteriores: 9.03 s.
Suite completa: 3642 passed en 355.96 s; Black/Ruff/Alembic check/diff correctos.

No migracion nueva ni provision/despliegue con credenciales reales. Ambas operaciones
conservan guardias de habilitadas; sin activacion excepcional. Pendiente concurrencia
HTTP de revocacion/seleccion/publicacion y fallos transaccionales adicionales,
fuentes oficiales/aceptacion y provision operativa controlada. Ley 21.719/19.628
reformada base fija; M3-T1 EN PROGRESO integral. Sin commit/push en este paso.

## §106 — Concurrencia administrativa por HTTP (2026-10-08)

Doce pruebas nuevas, sin cambios en rutas/servicios/migraciones. App registrada,
JWT ES256 firmado con JWKS sintetico, login/pools PostgreSQL restringidos reales.
Las pausas de test controlan flush/commit; no reemplazan SQL, barrera personal,
validacion JWT, escritores ni rollback. Se observan bloqueos efectivos mediante
pg_blocking_pids; pg_stat_clear_snapshot evita cache de pg_stat_activity en el
observador transaccional. Timeouts acotados y limpieza de tasks/pools/roles/perfiles.

Cuatro casos (publicacion/seleccion x commit/rollback de revocacion previa):
peticion HTTP espera UPDATE del perfil; revocacion confirmada -> 403 sin escrituras;
revocacion revertida -> 201. Se relee autoridad despues de esperar.
Seis casos (ambas rutas x commit/rollback/cancelacion de la peticion autorizada):
UPDATE de revocacion espera FOR SHARE hasta cierre. Commit -> 201/cambio persistido;
fallo de commit -> 500/rollback sin cambio; cancelacion -> rollback sin cambio.
Despues de confirmar revocacion, siguiente peticion -> 403; pool sin sub/rol residual.

Seleccion concurrente: dos conexiones esperando advisory, publicaciones diferentes
con expected_revision=0 -> un 201 y un 409; exactamente un evento/selector revision 1.
Publicacion duplicada concurrente: ambas pasan precheck y se encuentran en flush;
se observa espera real por unicidad mientras ganador retiene commit. Un 201 y un
409 (SQLSTATE 23505), una sola publicacion y ningun evento/selector. Esto acredita
la traduccion de conflicto de DB implementada en §105, antes solo secuencial.

Doce nuevas aprobadas en 2.98 s; 97 focalizadas con API/pool/autoridad/escritores/auth
aprobadas en 11.73 s. Suite completa: 3654 passed en 369.30 s; Black/Ruff/Alembic check/diff correctos.
No migracion ni datos/credenciales reales alterados; fixtures usan identidades y
roles temporales propios. Sin habilitacion excepcional ni despliegue operativo.

Proximo: revisar fuentes oficiales y trazabilidad de aceptacion tecnica para el
control EIPD, sin habilitar mientras falten requisitos; registrar/probar provision
operativa por separado. Ley 21.719/19.628 reformada base fija independiente del
calendario; M3-T1 sigue EN PROGRESO integral. Sin commit/push en este paso.

## §107 — Revalidacion de fuentes y trazabilidad tecnica (2026-10-08)

Base Git limpia/sincronizada: 97d4fd29920e98a7b0a94714b04ae43e7cb5d010 (§106).
Registro m3-t1-eipd-fuentes.md actualizado: BCN por portal nuevo, art15ter localizado;
Diario Oficial CVE 2583630 PDF abierto. Busqueda acotada no verifica instrumento
complementario especifico de Agencia; no acredita inexistencia. Ley reformada
base fija independiente del calendario; no reinterpretar consulta facultativa como
aprobacion juridica universal. No version/autoridad/aceptacion inventadas.

| Criterio actual | Evidencia trazable | Estado |
| --- | --- | --- |
| Autoridad y escritores personales | 07bc7dd8ad06a16f5e32efc17ac67efa1036e356, §§102–103 | Implementado/probado |
| Pool separado y JWT/sub local | 01d27b0c44cec33dd2dfa2f160f0e6e3f3dc3257, §104 | Implementado/probado local |
| Rutas HTTP administrativas | 56dba76a0052eccb766f77ac91ba59c62d1f922d, §105 | Implementado/probado local |
| Revocacion/carreras/rollback/cancelacion HTTP | 97d4fd29920e98a7b0a94714b04ae43e7cb5d010, §106 | Doce nuevas; 97 focalizadas, 11.73 s |
| Suite completa del contenido §106 | Checkpoint §106; pruebas antes del commit, contenido luego versionado | 3654 passed, 369.30 s |
| Head local de migraciones | alembic current consultado §107 | b17d95c0286f (head) |
| Fuentes legales base | Registro F1/F4 y revalidacion §107 | Texto consultado, sin certificacion exhaustiva de vigencia |
| Instrumentos complementarios Agencia | Registro §107 | PENDIENTE; sin instrumento/version verificados |
| Decision de aceptacion real con responsable/evidencia | Sin aceptacion trazable registrada | PENDIENTE; pruebas no equivalen a accepted_by |
| Provision/validacion operativa real | Solo roles/credenciales sinteticos de tests | PENDIENTE; sin despliegue acreditado |
| Activacion excepcional real | Guardias productivas conservadas | BLOQUEADA |

La matriz inicial de este documento y checkpoints anteriores son historicos;
para autoridad/pool/transporte/head actual prevalece esta evidencia. No se declara
aceptacion integral ni se genera objeto de politica con fuentes verificadas,
accepted_by, validation_commit o activation habilitada. Este inventario asocia
pruebas a commits; no reemplaza decision de aceptacion ni validacion operativa.

Solo documentacion en §107: diff --check correcto; no nueva suite ni migracion.
Ultima suite completa conserva 3654 §106. Proximo paso independiente: procedimiento
verificable de provision operativa del canal con politica deshabilitada, sin
credenciales reales ni activacion. Completar fuentes/aceptacion antes de habilitar.
M3-T1 EN PROGRESO integral. Sin commit/push en este paso.

## §108 — Procedimiento operativo deshabilitado preparado (2026-10-09)

Base c963e75c2caa0936e04fdeac01ebad4f903ae911. Se agrega
m3-t1-eipd-provision-operativa.md: expediente de entorno/commit/head/login/staff/
secreto por referencia/selector, provision del login separada del grupo NOLOGIN,
comprobaciones de rol local y permisos, pruebas HTTP negativas/positivas con politica
deshabilitada, verificacion de auditoria, revocacion/retirada/rotacion con drenaje.
Reconoce ausencia de GET snapshot; lectura coherente por herramienta de mantenimiento.
Sin retry ciego, borrado de auditoria, downgrade ni aceptacion/fuentes inventadas.

Plantillas no ejecutadas; no se provisionan roles/credenciales/perfiles ni se envia
trafico a un entorno operativo. JSON de publicacion validado contra PublicationRequest;
diff --check correcto. No cambios de codigo ni nueva suite completa: 3654 §106.
Provision real, instrumento complementario y decision de aceptacion permanecen
PENDIENTES. Proximo: preparar preflight verificable de solo lectura del canal,
sin reemplazar JWT/autoridad ni emitir publicacion/seleccion. Activacion bloqueada;
ley reformada base fija; M3-T1 EN PROGRESO integral. Sin commit/push.

## §109 — Preflight administrativo de solo lectura (2026-10-09)

Se agrega backend/scripts/eipd_admin_preflight.py, ejecutable desde backend con
python -m scripts.eipd_admin_preflight. Usa solo EIPD_ADMIN_DATABASE_URL/pool §104;
transaccion READ ONLY, chequeo de login/rol, identidad residual vacia, READ COMMITTED,
EXECUTE de barrera y ausencia de UPDATE de perfiles/is_superadmin. Lee y valida
snapshot completo; rechaza politicas habilitadas incluso no seleccionadas.
Siempre rollback. No setea sub ni llama a barrera FOR SHARE ni publica/selecciona.

Salida JSON limitada: ok (exit 0) si canal y selector deshabilitado coherentes;
pending_selector (exit 2) si canal/auditoria validos sin selector; failed (exit 1)
ante fallo, sin excepcion/URL/secretos. Informe indica expresamente autenticacion
personal no verificada y activacion no autorizada. No acredita provision integral,
JWT HTTP, grupo/permisos completos ni aceptacion real; completar runbook §108.

Seis pruebas nuevas: ausencia de selector sin bootstrap, seleccion deshabilitada
sin cambios y pool limpio, owner/tenant rechazados, escritura accidental bloqueada
por PostgreSQL READ ONLY (25006), error CLI sin divulgar texto sensible. 23 focalizadas
con canal/pool aprobadas en 1.84 s; Black/Ruff/diff correctos. Sin nueva suite completa;
ultima 3654 §106. No migracion/configuracion/roles/credenciales reales modificados.
No preflight ejecutado contra entorno operativo; pruebas usan login/roles sinteticos.
Proximo: ampliar diagnostico de permisos de grupo/dominio y evidencia de entorno
sin secretos; ejecutar provision solo sobre destino/identidad acreditados. Fuentes/
aceptacion real pendientes, activacion bloqueada, ley fija, M3-T1 EN PROGRESO.
Sin commit/push.

## §110 — Permisos efectivos y limites de evidencia del preflight (2026-10-09)

Base f0f5224118886cb21a5c8024ccfd1728bce66391. Preflight readonly amplía catalogo:
grupo NOLOGIN/NOINHERIT sin privilegios amplios, membresias superiores ni propiedad
de relaciones; app_user sin membresia administrativa; login sin ADMIN OPTION;
login/grupo sin CREATE sobre public. Tres tablas globales con RLS y SELECT/INSERT,
UPDATE solo selector; sin DELETE/TRUNCATE/REFERENCES/TRIGGER ni UPDATE por columna
en publicaciones/eventos. Rechaza permisos efectivos de login sobre relaciones
public y del grupo fuera de las tres admitidas, incluidos grants PUBLIC/por columna.
No consulta filas del dominio tenant. No repara permisos ni modifica configuracion.

Informe versionado report_version=1, permissions_verified=true con alcance explicito
public_relations_and_role_flags solo al completar chequeos. environment_identity_verified
/migration_head_verified/personal_authentication_verified/activation_authorized=false:
no acredita destino, head operativo, JWT ni decision de activacion. No cubre todo
privilegio de funciones/secuencias/otros schemas ni equivalencia del cuerpo de RLS;
requiere revisar migraciones/config/entorno y ejecutar matriz HTTP por separado.

Ocho PostgreSQL nuevas: grants efectivos SELECT tabla/columna al grupo/login/PUBLIC
sobre tabla temporal vacia, ADMIN OPTION del login temporal y CREATE public del login.
Rechazos observados y objetos/grants eliminados por cleanup; canal normal vuelve a
superar chequeos. 31 focalizadas con canal y preflight anteriores: 3.26 s; formato/
diff correctos. No nueva suite completa; ultima 3654 §106. Sin migracion/grants
persistentes/credenciales reales ni ejecucion contra entorno operativo acreditado.

Proximo: completar expediente de destino/commit/head/login/staff/responsable y
registrar resultados del preflight/HTTP en entorno acordado. No ampliar privilegios
para hacer pasar el informe; corregir provision conforme contrato. Fuentes oficiales
complementarias/aceptacion real aun pendientes, activacion bloqueada. Ley reformada
base fija; M3-T1 EN PROGRESO integral. Sin commit/push.

## §111 — Expediente inicial y comprobacion de configuracion (2026-10-09)

Base limpia d57b2206b2ae432ae93e6a278e24483d4db1ece9. Se agrega
m3-t1-eipd-expediente-operativo.md con evidencia ejecutada: environment development,
hosts configurados loopback (sin inferir ubicacion fisica), EIPD_ADMIN_DATABASE_URL
ausente, preflight CLI exit 1/failed sin canal inicializado y head local b17d95c0286f
via mantenimiento readonly. No URLs/JWT/passwords impresos ni datos tenant consultados.
No provision de roles/perfiles/secreto/politica; sin fallback owner ni .env modificado.

Destino operativo solicitado al usuario, pendiente. Continuar provision depende
de destino acreditado y del expediente; no crear actor staff ni credenciales ficticias
para simular resultado operativo. No nueva suite; ultima completa 3654 §106,
focalizadas 31 §110. Diff correcto. Fuentes/aceptacion/provision pendientes;
activacion bloqueada, ley fija, M3-T1 EN PROGRESO. Sin commit/push.

## §112 — Seleccion de desarrollo local y accion de provision pendiente

Fecha 2026-10-09. Usuario elige local. Comprobaciones readonly: head b17d95c0286f,
canal EIPD ausente, eipd_backend_local inexistente; un superadmin contado sin identificar
ni modificar. Identidad staff solicitada sin secretos, pendiente. Accion concreta
preparada para login limitado y archivo privado externo al repo; revision automatica
la rechaza antes de ejecucion por falta de autorizacion explicita de persistencia.
No roles/secreto/archivo nuevos ni configuracion/politica modificados. Se pide
aprobacion de provision exacta, sin reintentar por alternativa. Solo documentacion;
ultima suite completa 3654 §106, focalizadas 31 §110. EN PROGRESO; activacion bloqueada.

## §113 — Canal tecnico local provisionado y preflight ejecutado

Fecha 2026-10-09. Autorizacion explicita del usuario tras §112. Login
 eipd_backend_local limitado, miembro solo eipd_policy_admin; credencial nueva
fuera del repo en ~/.config/cumpleia-local-eipd/admin.env 0600, sin valor impreso.
.env habitual/perfiles/politicas intactos. Carga solo en proceso de diagnostico.
Preflight local pending_selector, codigo logico 2 confirmado: canal/permisos/auditoria
coherentes, selector ausente, sin bootstrap. No acredita backend HTTP/JWT personal
ni provision integral. Staff solicitado pendiente; proximo vincular identidad real
y validar proceso HTTP configurado. Sin nueva suite; ultima 3654 §106, focalizadas
31 §110. Ley fija, EN PROGRESO, activacion bloqueada. Sin commit/push.

## §114 — Staff indicado y verificacion pendiente (2026-10-09)

Usuario informa correo de staff (no se reproduce PII en evidencia versionada).
Consulta parametrizada readonly: exactamente un perfil local, auth_user_id presente,
is_superadmin=false. No se modifica ni promueve perfil. Configuracion de autenticacion
presente; GET administrativo readonly del usuario por ID no se completa: ConnectError
en etapa auth_request. No respuesta de Supabase ni identidad externa/JWT acreditados.
Metodo GET consultado en fuente primaria de Supabase auth-js GoTrueAdminApi.
No secretos/URL/JWT/respuestas privadas impresos, ni mensajes enviados al usuario.

Pendientes: identificador de Supabase aportado por usuario para contrastar el vinculo,
autorizacion explicita de superadmin global del perfil local indicado, y humo JWT/HTTP
con proceso configurado. Permiso global permite acceso a organizaciones del entorno
local; elegir staff/correo no se interpreta como promocion autorizada. Canal tecnico
§113 disponible, selector ausente; sin nuevas politicas ni activacion. Sin nueva suite;
ultima 3654 §106/focalizadas 31 §110. EN PROGRESO; sin commit/push.

## §115 — Superadmin local explicitamente autorizado (2026-10-09)

Usuario autoriza superadmin global en base local para el perfil del correo indicado.
Mantenimiento verifica entorno development/host loopback, exactamente un perfil y
vinculo auth_user_id presente, toma FOR UPDATE y cambia solo is_superadmin=true
por id/auth_user_id existentes. Commit realizado y lectura posterior confirma true.
No se crea usuario, cambia email/sub ni modifica Supabase. PII/IDs no se imprimen
ni se incorporan a evidencia versionada. Alcance: organizaciones de base local.

Autoridad local provisionada por autorizacion humana; identidad externa de Supabase
/JWT personal sigue sin verificar (ConnectError previo; User UID aun pendiente).
No declarar humo HTTP aprobado ni sources_status/aceptacion/activacion habilitadas.
Canal tecnico §113 permanece; selector/politica sin cambios. No nueva suite ni
migracion; ultima 3654 §106, focalizadas 31 §110. Proximo contrastar User UID y
completar autenticacion/proceso HTTP configurado. EN PROGRESO; sin commit/push.

## §116 — UID contrastado y rechazo HTTP anonimo (2026-10-09)

Usuario aporta User UID de Supabase; consulta local readonly confirma un perfil
unico por correo, auth_user_id coincide exactamente con UID aportado y superadmin=true.
No se reproduce PII/UID en evidencia versionada. Este contraste usa dato aportado
por usuario y base local; no acredita respuesta externa de Supabase ni JWT firmado.

Backend local 127.0.0.1:8000 responde health 200; OpenAPI 200 registra POST
/admin/eipd/publications y /admin/eipd/selections. Ambas solicitudes sin token
(cuerpo vacio) -> 401. No filas/identidad/canal de DB mutados. Prueba negativa
real acreditada; no acredita SHA del proceso, carga del secreto EIPD o prueba positiva.

Pendiente proceso HTTP configurado con secreto privado del canal y solicitud
personal JWT validada por issuer/JWKS, seguida de publicacion/seleccion deshabilitada
y auditoria/retirada. No solicitar tokens/passwords por chat; usar inicio de sesion
local y canal seguro. ConnectError previo en consulta de autenticacion externa
no se considera resuelto por el contraste UID. Canal tecnico y autoridad local
estan provisionados; selector ausente. Fuentes/aceptacion pendientes, activacion
bloqueada; EN PROGRESO. Sin nueva suite ni commit/push.

## §117 — Proceso local configurado e identidad externa verificada (2026-10-09)

Base limpia 6474873b2cd0eb0a9e941322cbca04bb9e59d365. Archivo privado externo
presente, modo 0600 validado; carga solo en memoria de nuevo proceso local,
DEBUG=false, access_log=false, uvicorn en 127.0.0.1:8001. Proceso de validacion
separado del backend existente 8000; .env habitual sin cambios y secreto no impreso.
Sesión de herramienta que mantiene proceso: 30969 (referencia efimera, no garantiza
persistencia tras cierre/reinicio de herramienta). No despliegue remoto ni servicio
persistente del sistema; verificar salud antes de cada paso.

DNS de proyecto de autenticacion accesible y JWKS publico GET 200. Reintento GET
administrativo readonly de usuario Supabase -> 200; id/correo coinciden con perfil
local y dato humano aportado, email confirmado, superadmin local true. ConnectError
anterior ya no se reproduce en estas consultas. No se exponen PII/claves/respuestas.
Esto acredita identidad externa por consulta administrativa, no JWT de sesion personal.

Proceso nuevo health 200; POST ambas rutas EIPD sin token -> 401. No se publica ni
selecciona politica ni modifica perfil. Credencial privada del canal cargada por
proceso iniciado; pool inicializacion diferida, prueba readonly del canal acreditada
§113. No inferir solicitud autenticada por salud o rechazo anonimo.

Se intento inspeccion de navegador mediante herramienta CUA; inicializacion falla
por helper/setup refresh, sin estado de navegador disponible. Habilidad instalada
leida (computer-use 26.1002.52244); ruta anterior del catalogo ausente, encontrada
mediante busqueda local. No bypass de automatizacion ni extraccion de tokens.
Pendiente sesion autentica del usuario por canal local seguro. No pedir contrasena/
JWT por chat ni generar token sintetico como evidencia operacional.

Proximo: solicitud autenticada con JWT real del staff contra proceso configurado,
politica deshabilitada y auditoria; requiere acceso a sesion del usuario. Fuentes/
aceptacion/provision integral siguen pendientes; activacion bloqueada. Sin nueva
suite, ultima completa 3654 §106 y focalizadas 31 §110. M3-T1 EN PROGRESO.
Sin commit/push.

## 2026-10-09 — M3-T1 §118: comprobacion local de acceso personal preparada

Se incorpora GET /admin/eipd/status, protegido por el canal administrativo y la
autoridad personal existentes. Devuelve solo un resumen de acceso y presencia de
selector; activation_authorized permanece false. No publica, selecciona ni crea
politicas. La pantalla de desarrollo /admin/eipd-validation utiliza la sesion
Supabase del navegador sin mostrar ni persistir el token y consulta el backend
local 127.0.0.1:8001.

Validacion: 40 pruebas focalizadas de API aprobadas; Black/Ruff, type-check y lint
del frontend aprobados. HTTP real sin sesion: pantalla redirige al login (307),
GET de estado rechaza sin token (401). Esto no acredita JWT personal real: queda
pendiente iniciar sesion, abrir la pantalla y pulsar Comprobar acceso. Los procesos
locales son efimeros; backend anterior 8000 permanece. No cambios de credenciales,
perfil ni politicas. Ultima suite completa: 3654 pruebas (§106).

La Ley 21.719 / 19.628 reformada permanece como base fija. Fuentes complementarias,
aceptacion y validacion operacional integral pendientes. M3-T1 EN PROGRESO;
activacion excepcional bloqueada. Sin commit/push en este paso.

## 2026-10-09 — M3-T1 §118: comprobacion personal confirmada por el usuario

El usuario aporta captura de /admin/eipd-validation con el resultado:
«Acceso administrativo confirmado. La activacion EIPD permanece bloqueada».
Se registra como evidencia visual aportada por el usuario de la comprobacion con
su sesion real, posterior al cierre y nuevo inicio de sesion. No se capturan ni
persisten tokens, credenciales o datos personales; no se incorpora la imagen al
repositorio. No se afirma una inspeccion independiente de la solicitud HTTP.

La comprobacion de acceso queda satisfecha con esta evidencia. No publica ni
selecciona politicas y no habilita activacion. Proximo paso: preparar la validacion
operacional de publicacion/seleccion de politica deshabilitada y auditoria con
sesion personal. Fuentes complementarias y aceptacion integral siguen pendientes.
M3-T1 EN PROGRESO. Sin commit/push.

## 2026-10-09 — M3-T1 §119: consulta personal del registro operativo

Se incorpora GET /admin/eipd/audit con AdminDb y el contrato cerrado de snapshot
validado. La lectura conserva la comprobacion JWT, autoridad global y canal
restringido; errores de coherencia devuelven 409. No crea ni modifica politicas.
La pantalla local incorpora Consultar registro y muestra revision vigente,
numero de publicaciones/selecciones y referencias/estado de las politicas.
Sin selector la revision mostrada es cero; no se inventa una seleccion inicial.

Pruebas API y concurrencia: 54 aprobadas en 12.91 s. Nuevos casos cubren lectura
sin escrituras antes/despues de publicar y seleccionar, rechazo sin JWT y rechazo
tenant. Black/Ruff y type-check/lint frontend aprobados. Backend de validacion
reiniciado; GET real /audit sin token devuelve 401. No se acredita consulta real
con sesion personal hasta el resultado aportado por el usuario. La comprobacion
de acceso personal §118 ya fue confirmada mediante captura.

Proximo: consultar el registro con la sesion personal; luego preparar publicacion
y seleccion deshabilitadas con revision vigente y evidencia operacional.
No hubo publicaciones/selecciones operacionales en este paso. Ley fija, fuentes
complementarias/aceptacion pendientes; M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §119: consulta del registro confirmada por el usuario

El usuario aporta dos capturas de la pantalla local: entrada y resultado de
Consultar registro. La segunda muestra revision actual 0, publicaciones 0,
selecciones 0, ninguna politica seleccionada y activacion EIPD bloqueada.
Se registra como evidencia visual aportada por el usuario de la consulta con su
sesion personal; no como inspeccion independiente de la solicitud HTTP.
No se incorporan imagenes, datos personales, claves ni tokens al repositorio.

La consulta personal del registro queda confirmada. No hubo publicaciones ni
selecciones operacionales en este paso. Proximo: preparar la publicacion de una
politica deshabilitada y verificar su persistencia/auditoria; posteriormente,
seleccionarla con revision vigente. Ley fija, fuentes complementarias y aceptacion
integral pendientes. M3-T1 EN PROGRESO; activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §120: publicacion local deshabilitada preparada

GET /admin/eipd/publication-draft protegido por AdminDb devuelve la propuesta fija
resolve_eipd_gate_policy_v1, sin escrituras ni aceptacion: fuentes pendientes,
aceptacion pendiente, sin responsables/evidencia de aceptacion inventados y
activacion deshabilitada. Motivo operacional y referencia documental explicitos.

La pantalla de desarrollo prepara la propuesta tras consultar el snapshot actual,
evita ofrecer publicacion si su referencia ya existe y muestra que el registro
local es permanente. Solo Publicar politica deshabilitada solicita POST existente
con JWT personal. Tras 201 consulta nuevamente la auditoria y contrasta ID/hash y
estado deshabilitado. No selecciona ni activa; no hay reintentos automaticos.
Ante resultado incierto requiere consultar el registro, sin repetir a ciegas.

56 pruebas API/concurrencia aprobadas en 13.27 s; casos nuevos cubren propuesta
readonly, JWT/autoridad, publicacion seguida de auditoria, selector ausente y
rechazo de duplicados sin cambios. Black/Ruff y type-check/lint frontend aprobados.
Proceso local 8001 actualizado; GET propuesta sin token devuelve 401. La publicacion
operacional con sesion personal sigue pendiente: no se ejecuta ni se acredita por
estas pruebas. No se cambian credenciales, perfiles ni el backend previo 8000.

Proximo: usuario prepara/revisa/publica politica deshabilitada en pantalla y aporta
resultado; luego verificar auditoria y preparar seleccion con revision vigente.
Ley 21.719 / 19.628 reformada fija; fuentes complementarias/aceptacion pendientes.
M3-T1 EN PROGRESO; activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §120: publicacion personal confirmada por captura

El usuario aporta captura posterior a Publicar politica deshabilitada. Muestra
revision actual 0, publicaciones 1, selecciones 0, ninguna politica seleccionada,
referencia m3-t1-eipd-deshabilitada-v1 en estado deshabilitada y mensaje de
publicacion confirmada en el registro; activacion EIPD bloqueada.
Se registra como evidencia visual aportada por el usuario de la publicacion con
su sesion personal y comprobacion posterior de la pantalla, sin afirmar una
inspeccion independiente de la solicitud HTTP o de los campos de auditoria.
No se incorporan imagenes, PII, claves ni tokens al repositorio.

La publicacion operacional queda confirmada por esta evidencia. No acredita
seleccion ni aceptacion juridica. Proximo: preparar seleccion explicita de la
publicacion deshabilitada con revision vigente y comprobar evento/selector en
la auditoria. Fuentes complementarias y aceptacion integral siguen pendientes;
ley fija, M3-T1 EN PROGRESO y activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §121: seleccion local deshabilitada preparada

La pantalla prepara la seleccion tras consultar GET /audit, toma publication_id,
hash y revision vigentes y muestra referencia/revision antes del boton explicito.
Solo admite la publicacion fija deshabilitada y no ofrece reseleccion de una
publicacion ya presente en eventos. POST /selections existente mantiene autoridad,
control optimista de revision y rechazo de politica habilitada. Tras 201 se consulta
el snapshot y se contrastan evento, hash, revision y selector, conservando estado
deshabilitado. No hay reintentos automaticos ante 409 o respuesta incierta.
La seleccion operacional personal sigue pendiente; no se ejecuta por este paso.

Type-check/lint frontend y formato aprobados. La primera suite en base operacional
produjo 52 aprobadas/4 fallidas porque los casos esperan registro vacio y ya existe
la publicacion personal. Se creo cumpleia_eipd_tests_20261009 vacia, solo esquema
migrado a head, funciones auth y permisos app_user equivalentes; sin copiar datos
personales ni cambiar URLs persistentes. Suite focalizada API/concurrencia en esa
base: 56 aprobadas en 12.15 s. Usar esa base aislada en siguientes suites; no ejecutar
pruebas de escritura contra el registro operacional. La base de pruebas queda local.

Comprobacion readonly posterior del snapshot operacional: 1 publicacion deshabilitada,
0 selecciones y sin selector (revision 0); registro personal preservado. No infiere
solicitud HTTP personal de esta consulta tecnica. Fuentes complementarias y aceptacion
integral pendientes; ley fija, M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §121: seleccion personal y registro confirmados

El usuario aporta dos capturas: revision 1, publicaciones 1, selecciones 1,
referencia m3-t1-eipd-deshabilitada-v1 deshabilitada y seleccionada. La segunda
muestra rechazo preventivo de reseleccion: publicacion ya seleccionada, sin
ofrecer otra seleccion. Se registra como evidencia visual del usuario; no como
inspeccion independiente del JWT o de la solicitud HTTP original.

Comprobacion tecnica readonly posterior mediante canal dedicado: snapshot validado,
1 publicacion, 1 evento y selector revision 1; identidades publicacion/evento/selector
y hash coinciden, actor de publicacion/seleccion consistente, fuentes/aceptacion
pendientes y activacion deshabilitada. Sin nuevas escrituras ni datos personales,
claves, tokens o capturas incorporados al repositorio.

Queda confirmada la seleccion operacional deshabilitada y su persistencia coherente.
No constituye aceptacion juridica ni habilitacion. Proximo: revisar el cierre de la
validacion operacional y pendientes de provision/rotacion/retiro y aceptacion,
manteniendo la ley fija. M3-T1 EN PROGRESO; activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §122: cierre delimitado de validacion local

La secuencia acceso personal -> consulta -> publicacion -> seleccion deshabilitada
queda documentada por capturas aportadas por el usuario (§118–121), y snapshot
tecnico posterior readonly coherente. Este cierre solo cubre esa secuencia local;
no marca DONE del modulo ni aceptacion juridica ni puesta en produccion.

Nuevo preflight readonly real: status ok, salida 0, channel_verified y
permissions_verified true, audit_coherent true, selector_present true y revision 1;
activation_authorized false. Las banderas de identidad del entorno/head/autenticacion
personal del CLI permanecen false por alcance limitado de esa herramienta, sin
sustituir la evidencia personal previa. Head comprobado separadamente por lectura
de alembic_version: b17d95c0286f. Sin escrituras ni nueva suite en este checkpoint;
ultima focalizada: 56 aprobadas en base aislada §121, ultima completa: 3654 §106.

Pendientes separados: (1) asegurar ejecucion de futuras suites solo en base aislada,
(2) probar rotacion/retiro del canal y recuperacion local preservando auditoria,
(3) verificar fuentes complementarias y registrar aceptacion real con responsables,
(4) resolver regimenes especiales/representacion y criterios del alcance integral.
No se identifica una fuente nueva ni se cambia una regla legal en esta revision.
Ley 21.719/19.628 reformada fija. M3-T1 EN PROGRESO; activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §123: ejecutor focalizado de pruebas aisladas

backend/scripts/run_eipd_tests.py proporciona python -m scripts.run_eipd_tests.
Deriva ambas URLs solo en entorno hijo hacia cumpleia_eipd_tests_20261009, mantiene
roles separados y exige development, hosts loopback iguales, sin parametros URL,
runtime app_user. Antes de pytest consulta readonly current_database/head y registro
EIPD vacio, confirma runtime sin superuser/BYPASSRLS. Rechaza destino/head/roles/estado
incompatibles con salida logica 2 y mensaje sin secretos. No crea/borra DB ni copia
datos; no imprime URLs. Elimina overrides heredados de pytest y credenciales Supabase/
canal administrativo; usa emisor sintetico de pruebas y targets fijos sin argumentos.

Guardas probadas: URLs a base fija y roles intactos, entorno padre sin cambios,
rechazo remoto/query/produccion, runtime owner/destinos distintos, DB/head/registro
no vacio y privilegios runtime incompatibles. Ejecucion por el runner: 60 aprobadas
en 9.45 s (56 API/concurrencia + 4 guardas); Black/Ruff aprobados. Invocacion con
argumento extra bloqueada antes de pytest. Sin nuevas escrituras operacionales ni
cambios de perfil/secretos/backend. No suite completa nueva.

Alcance: protege las invocaciones mediante este ejecutor; pytest directo sigue
resolviendo DATABASE_URL habitual y no queda protegido por este wrapper. Usar este
punto de entrada para la suite EIPD focalizada, sin ejecutar pytest directo contra
la base operacional. Cambios de head requieren revision explicita de la guarda.
Siguiente: preparar ensayo de rotacion/retiro y recuperacion local preservando
historial. Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN
PROGRESO y activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §124: ensayo aislado de rotacion/retiro y recuperacion

Se agregan tres pruebas PostgreSQL de ciclo de vida al ejecutor fijo, sobre login
aleatorio temporal de fixture y base aislada. Rotacion: clave antigua rechazada en
conexiones nuevas (28P01), conexion previa sobrevive, pool se dispone y clave nueva
permite recuperar el canal; rol local e identidad se limpian tras rollback. NOLOGIN:
conexion nueva rechazada (28000), conexion previa sigue viva pero _prepare_channel
rechaza con 503; restaurar LOGIN y renovar pool recupera. Retiro de membresia:
conexion caliente rechazada por guarda 503, restauracion recupera el canal.

63 pruebas focalizadas aprobadas en 13.03 s; Black/Ruff aprobados. El snapshot de
pruebas permanece igual antes/despues de cada ensayo (registro inicialmente vacio
por guarda del runner); no se extrapola a prueba de historial no vacio. Fixtures
restauran flags/membresia cuando procede, disponen pools y eliminan solo su rol
aleatorio. No cambian login/secreto/pool operacional ni perfil personal.
Preflight readonly posterior del canal original: ok, auditoria coherente, selector
revision 1 y activation_authorized false. No rotacion/retiro real del canal de usuario
ni actualizacion de su archivo privado en este checkpoint.

Pendiente operacional: ensayo coordinado sobre canal provisionado, renovacion de
procesos/conexiones y referencia de recuperacion segura con historial real. Ensayo
tecnico aislado no acredita ese cambio. Fuentes/aceptacion y alcance integral siguen
pendientes; ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §125: rotacion real local preparada

Plan concreto en docs/project/m3-t1-eipd-plan-rotacion-local.md. Lectura previa:
archivo externo 0600, destino development/loopback y login dedicado esperado;
preflight ok, revision 1, head b17d95c0286f. Dos conexiones idle durante diagnostico
(incluida la propia); pool del diagnostico dispuesto al terminar. Requerir nueva
comprobacion de drenaje antes de ejecutar. No se cambia clave/archivo/rol/proceso.

Secuencia preparada: snapshot previo, detener solo validacion 8001 y drenar,
reemplazo privado/recuperacion 0600, cambio de clave y sustitucion atomica con
recuperacion ante fallo, conexiones nuevas antigua rechazada/nueva aceptada,
comparacion exacta de auditoria, reinicio y comprobacion personal. Backend 8000 y
perfil permanecen fuera del cambio. Rotacion REAL pendiente, no acreditada por
ensayo aislado §124 ni por este plan. Sin nueva suite; ultima focalizada 63 §124.
Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN PROGRESO y
activacion bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §126: rotacion real local ejecutada

Se detuvo el proceso propio de validacion 8001 y se comprobo ausencia de conexiones
del login dedicado antes de alterar password. Destino development/loopback, login
esperado, archivo privado 0600 y head b17d95c0286f verificados. Snapshot previo
validado: 1 publicacion deshabilitada, 1 seleccion, revision 1.

Nueva clave aleatoria en memoria, copia privada de recuperacion 0600 externa al
repo y reemplazo privado preparado; cambio password de eipd_backend_local y
sustitucion atomica de admin.env. Conexion NUEVA con credencial anterior rechazada;
nueva credencial: preflight ok. Snapshot completo posterior exactamente igual al
previo; no cambios de perfiles, permisos, publicaciones, eventos ni selector.

Proceso propio 8001 reiniciado con nuevo secreto en memoria, DEBUG=false y sin
access log. GET /admin/eipd/status sin token -> 401. Backend previo 8000 fuera del
cambio. No secretos ni PII en documentos/logs/repositorio. Copia privada de
recuperacion conservada hasta confirmar sesion personal; retirada aun pendiente.
No se afirma validacion personal tras reinicio a partir del diagnostico tecnico.

Proximo: usuario Comprobar acceso y Consultar registro en pantalla con sesion real,
confirmar revision 1/politica deshabilitada y luego retirar copia privada anterior.
No suite nueva (ultima 63 §124). Fuentes/aceptacion y alcance integral pendientes;
ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §126: comprobacion personal posterior y retirada de copia

El usuario aporta captura posterior al reinicio con mensaje de acceso administrativo
confirmado y activacion EIPD bloqueada; pantalla conserva revision 1, 1 publicacion,
1 seleccion y politica deshabilitada/seleccionada. Evidencia visual del usuario,
sin inspeccion independiente del JWT ni captura de credenciales.

Tras esta confirmacion se retira exclusivamente la copia privada anterior creada
para recuperacion §126, comprobando ruta/tipo/modo 0600 y ausencia posterior.
Archivo actual privado 0600 conservado. No se elimina historial, roles ni perfil;
no nuevas publicaciones/selecciones. La retirada es eliminacion del archivo de
recuperacion, sin afirmar borrado forense del almacenamiento.

Rotacion local y acceso posterior confirmados; recuperacion temporal cerrada.
Retiro definitivo del canal no ejecutado. Fuentes/aceptacion y alcance integral
siguen pendientes; ley fija, M3-T1 EN PROGRESO y activacion bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §127: retiro reversible del canal real y recuperacion

Proceso propio 8001 detenido y ausencia de sesiones dedicadas comprobada tras
snapshot previo validado. Login local eipd_backend_local cambiado temporalmente
a NOLOGIN: conexion NUEVA con credencial actual rechazada, SQLSTATE 28000.
LOGIN restaurado en finally; nueva conexion y preflight ok. Snapshot completo
posterior exactamente igual al previo, selector revision 1. No cambio de password,
archivo privado, membresias, perfiles, publicaciones, eventos ni selector.

Proceso 8001 reiniciado con credencial privada actual, DEBUG=false y sin access log;
GET /status sin token -> 401. Backend 8000 fuera del ensayo. Comprobacion personal
posterior al reinicio pendiente. No constituye retiro definitivo del canal ni
revocacion instantanea de transacciones ya autorizadas; se dreno antes del cambio.
No nueva suite; ultima 63 §124. Ley fija, fuentes/aceptacion y alcance integral
pendientes; M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §127: acceso personal recuperado confirmado

El usuario aporta captura con mensaje «Acceso administrativo confirmado. La
activacion EIPD permanece bloqueada» posterior al reinicio de recuperacion.
Se registra como evidencia visual del usuario, sin inspeccion independiente de
JWT/solicitud original ni almacenamiento de imagen, datos personales o tokens.
La captura no muestra el registro; su coherencia y revision 1 fueron comprobadas
tecnicamente antes/despues del ensayo y no se deducen de esta imagen.

Ensayo reversible real y acceso posterior confirmados. Canal activo restaurado;
no retiro definitivo, nuevas credenciales ni cambios de politica. No nueva suite.
Fuentes/aceptacion y alcance integral pendientes; ley fija, M3-T1 EN PROGRESO,
activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §128: siguiente brecha funcional delimitada

Tras cerrar ciclo local del canal, se revisa codigo actual: salud/biometria por
consentimiento ya tienen evaluadores; investigacion_art16quinquies aun deriva a
validador_no_implementado. Se elige preparacion documental inicial para datos no
sensibles/adultos con LIA vigente, decision de producto sin atribuirla como limite
juridico universal. Fuente primaria BCN Ley 21.719/art16quinquies consultada.

Diseno, completitud/aplicabilidad, integracion por pasos y criterios de aceptacion
en docs/project/m3-t1-investigacion-diseno.md. Proximo: schema y evaluador puro,
sin persistir ni levantar bloqueos hasta integrar/aceptar. Sin cambios de codigo,
politicas ni secretos; sin nueva suite. Ley fija, M3-T1 EN PROGRESO y activacion
EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §129: contrato/evaluador puro de investigacion

Se agregan app/schemas/research.py (ResearchAssessmentV1 cerrado, borrador opcional,
revalidacion de instancias) y app/services/research.py. Evaluador puro reutiliza LIA,
canonizacion de finalidad y RAT; exige base interes_legitimo y cobertura completa
conservadora, deriva sensibles/menores/vulnerabilidad a revision. Completa finalidad,
interes publico, exclusividad, medidas/evidencia y conservacion. Difusion si exige
documentacion de anonimizacion; no la hace no aplicable y material residual requiere
revision; pendiente deja aplicabilidad sin resolver. No verifica eficacia material.

Resultado completo solo describe preparacion documental; can_confirm siempre false.
No integra persistencia/API/binding ni levanta validador_no_implementado especial.
Snapshots y hashes historicos intactos; sin migracion ni escrituras operacionales.
Pruebas nuevas: ausencia de campos, si/no/pendiente, difusion/material residual,
alcance, finalidad/base/LIA incompatible, sensibles/menores, schema cerrado,
revalidacion, determinismo y entradas sin cambios. Runner aislado ampliado para
incluir pruebas de investigacion; Black/Ruff aprobados. Suite aislada: 87 pruebas
aprobadas en 13.20 s (24 nuevas de investigacion y 63 previas). No nueva suite completa.

Proximo: ampliar casos de aplicabilidad y limites antes de diseñar binding nuevo e
integracion persistente. Ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada.
Sin commit/push.

## 2026-10-09 — M3-T1 §130: limites y aplicabilidad de investigacion probados

20 casos nuevos en test_services_research.py: difusion ausente/pendiente mantiene
anonimizacion sin resolver, evidencia con referencia/tipo vacios no acredita
preparacion, cada componente de anonimizacion requerido si se publica, RAT parcial
y selectores semanticamente duplicados requieren revision, adolescentes/vulnerables/
sensibilidad declarada no evaden limites iniciales, expediente/snapshot ausentes y
respuestas sin razonamiento impiden completo. No fue necesario cambiar evaluador.

Suite via ejecutor aislado: 107 aprobadas en 13.05 s (44 investigacion, 63 previas).
Black/Ruff aprobados. Sin escritura operacional, cambios legales ni politicas;
can_confirm sigue false, sin persistencia/API/binding ni integracion especial.

Proximo: implementar identidad/binding documental nuevo y probar cambios de
finalidad, RAT, LIA y expediente; conservar schemas y hashes historicos. No inferir
asociacion vigente a partir de completitud. Ley fija, M3-T1 EN PROGRESO y activacion
EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §131: asociacion nueva de investigacion

ResearchContextBindingV1 y BoundResearchAssessmentV1 son contratos cerrados nuevos,
independientes de SpecialContextBinding historico. research_binding.py calcula
SHA-256 con dominio/version explicitos: contexto incluye RAT completo/base/LIA;
documento incluye expediente completo. JSON ordenado por claves; orden de listas y
textos conservado deliberadamente (comparacion conservadora, sin prometer equivalencia
semantica). Bind revalida y devuelve copia; chequeo no actualiza hashes automaticamente.

Cambios RAT/finalidad/base/LIA producen asociacion_contexto_obsoleta; cambios de
expediente producen asociacion_documento_obsoleta. Ausencia requiere revision;
contrato historico/version desconocida no se convierte silenciosamente. Asociacion
vigente no acredita completitud/autoridad; can_confirm sigue false. Sin migracion,
API, persistencia ni cambios de bindings/hashes historicos.

La primera ejecucion detecto error previo de catalogo: evaluador research usaba
interes_legitimo abreviado. Corregido a interes_legitimo_art13d, igual que LegalBasis;
pruebas actualizadas y regresion rechaza el alias. Suite final aislada: 119 aprobadas
en 10.04 s (11 asociacion, 45 evaluador investigacion y 63 previas). Black/Ruff
aprobados. Sin escrituras operacionales ni cambio de selector EIPD.

Proximo: diseñar persistencia/API y versiones de asociacion especiales/EIPD para
incorporar investigacion sin reinterpretar historicos. Ley fija, M3-T1 EN PROGRESO,
confirmacion de investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §132: persistencia/API de investigacion delimitadas

Plan concreto en docs/project/m3-t1-investigacion-integracion.md: columna JSONB
nullable sin backfill, input documental/output con binding de servidor, contratos
sin ciclos de importacion y semantica PATCH omision/null/reaporte. Contexto cambiado
sin reaporte conserva binding y debe marcar obsolescencia. Historicos no reciben
hash nuevo automaticamente; protecciones tenant/inmutabilidad y gates preservados.

Orden: schema/modelo/migracion, luego servicios/API, readiness y finalmente nuevas
versiones especiales/EIPD con aceptacion. Sin cambios de codigo ni migracion aplicada,
no nueva suite; ultima focalizada 119 §131. Siguiente implementar primer incremento
persistente de schema/modelo/migracion en base aislada. Ley fija, M3-T1 EN PROGRESO,
confirmacion de investigacion y activacion EIPD bloqueadas. Sin commit/push.

## 2026-10-09 — M3-T1 §133: almacenamiento nullable de investigacion

Migracion append-only c28f1a9d730b sobre b17d95c0286f agrega research_assessment
JSONB nullable a legal_assessments, CHECK SQL NULL u objeto, sin backfill. ORM
agrega campo/constraint; ninguno de los expedientes historicos se reinterpreta.
Contratos nuevos movidos antes de DraftCreate en licitud.py y reexportados por
schemas/research.py para evitar ciclos de importacion; no se agrega input/output
API aun, evitando aceptar datos sin servicio de guardado. Hashes historicos intactos.

Primero upgrade/head y alembic check en base aislada aprobados. Dos pruebas nuevas
verifican columna/nullable/RLS/permisos runtime y borrador HTTP real con SQL NULL,
rechazo arrays/texto/numero/bool/JSON null y almacenamiento objeto. CHECK SQL no
valida todo el contrato; servicio/API posterior lo hara. La primera comprobacion
por nombre de constraint fallo por convencion de nombres; ajustada a tabla/definicion.
Suite final aislada: 121 aprobadas en 10.03 s. Black/Ruff aprobados; runner exige
nuevo head c28f1a9d730b, base aislada y registro EIPD vacio como antes.

Luego migracion aplicada al desarrollo local, alembic check aprobado y snapshot
EIPD completo exactamente igual antes/despues: selector revision 1. Sin cambios de
password/perfil/politicas; no suite contra base operacional ni despliegue remoto.
Nuevo head de ambas bases c28f1a9d730b; procedimientos antiguos con head previo son
historicos, requieren ese sucesor para la version actual del codigo.

Proximo: crear/leer/PATCH de expediente con binding de servidor, omision/null/reaporte
y aislamiento tenant, manteniendo investigacion bloqueada hasta integrar readiness.
Ley fija, M3-T1 EN PROGRESO y activacion EIPD bloqueada. Sin commit/push.

## 2026-10-09 — M3-T1 §134: expediente de investigacion en API de borrador

Create/PATCH aceptan ResearchAssessmentV1 nullable; salida GET/POST/PATCH expone
BoundResearchAssessmentV1 nullable. Servidor genera hashes con RAT/base/LIA finales.
PATCH model_fields_set distingue omision (preserva objeto/binding), null (retira)
y reaporte (revalida/vincula). Base/LIA cambiadas sin reaporte conservan asociacion
anterior, detectable como obsoleta sin renovacion en GET. No cambios a contratos,
hashes ni gates historicos especiales/EIPD. No nueva migracion.

Seis casos HTTP/OpenAPI nuevos contra PostgreSQL aislado: crear/consultar, cambio
simultaneo LIA/base/reaporte, obsolescencia sin reaporte, retiro, rechazo de binding
cliente en create/PATCH, acceso con organizacion ajena rechazado y PATCH bloqueado
en confirmado/reemplazado con expediente conservado. Estados historicos preparados
por fixture con metadatos validos; no equivale a habilitar confirmacion investigacion.
La prueba de acceso usa identidad A con cabecera B (403); no afirma por si sola una
prueba SQL directa de RLS. Las pruebas HTTP existentes verifican compatibilidad.

Primera suite ampliada: 297 aprobadas y tres fallos de preparacion de pruebas nuevas
(dict LIA y overrides de identidad). Corregidos; segundo intento detecto metadatos
obligatorios de ciclo de vida en fixtures, corregidos sin cambiar restricciones.
Resultado final: 127 pruebas focalizadas aprobadas en 11.78 s; los 174 casos HTTP
existentes de licitud ya aprobaron en la ejecucion ampliada. Black/Ruff aprobados.
Runner incluye ambas suites para siguientes ejecuciones. Sin pruebas en base
operacional, cambios de politica/credenciales ni despliegue remoto.

Proximo: integrar readiness documental y estado de asociacion de investigacion,
con bloqueo conservador e inmutabilidad; luego versiones especiales/EIPD nuevas.
Ley fija, M3-T1 EN PROGRESO, confirmacion de investigacion y activacion EIPD
bloqueadas. Sin commit/push en este paso.

## 2026-10-09 — M3-T1 §135: readiness de investigacion y bloqueo conservador

Readiness agrega research nullable con result/issues/applicability documentales,
association_result/association_issues independientes y can_confirm fijo false.
Evalua sobre RAT actual recomponible, base y LIA; compara binding persistido sin
renovarlo. Si RAT no disponible informa contexto_rat_no_disponible; si investigacion
es declarada y no hay expediente informa expediente/asociacion ausentes. Historicos
sin expediente ni regimen detectado conservan research null, sin hash sintetico.

Control transversal compartido por readiness y confirmacion agrega bloqueo 409
investigacion_confirmacion_bloqueada si hay expediente o regimen detectado, incluso
si se declararon respuestas negativas o el documento esta completo/vigente.
No se cambia validador especial ni versiones/hashes especiales/EIPD anteriores.
Completitud documental no implica autoridad ni activa una ruta excepcional.

Nuevos casos HTTP verifican completo+vigente+bloqueado, confirmacion 409 sin mutar
expediente, lectura reiterada sin escrituras, LIA cambiada sin reaporte produce
obsolescencia aun con documento completo, reaporte recupera vigencia, falta evidencia
produce incompleto y retiro deja null para ruta no declarada. Otro caso verifica
investigacion declarada sin documento, con bloqueos y sin asociacion sintetica.
Validacion final ampliada en base aislada: 303 pruebas aprobadas en 248.17 s
(incluye 174 HTTP existentes de licitud y 129 focalizadas). Black/Ruff aprobados.
Sin ejecucion de suite contra base operacional ni nueva migracion.

Proximo: delimitar nuevas versiones de asociaciones especiales/EIPD que cubran el
expediente de investigacion sin reinterpretar material historico. Mantener el gate
bloqueado hasta integracion completa y aceptacion revisada. Ley fija, M3-T1 EN
PROGRESO, activacion EIPD bloqueada. Sin migracion/despliegue ni commit/push.

## 2026-10-09 — M3-T1 §136: asociaciones de investigacion delimitadas

Plan concreto en docs/project/m3-t1-investigacion-asociaciones.md. Sucesores previstos:
SpecialContextBindingV11 y EipdContextBindingV12, envelope de dominio/version nuevo
con hash anterior intacto y expediente BoundResearchAssessmentV1 completo o null;
screening incluye base explicita. No regenerar binding research ni hashes historicos.
Dispatch por version; asociaciones antiguas con research requieren revision por falta
de cobertura. PATCH respeta orden RAT/base/LIA, research, especiales, screening y
solo renueva los documentos reaportados. GET sin escrituras e historicos inmutables.

Se delimita tambien la deuda de contexto de resolucion/revision EIPD para no atribuir
aceptacion historica a investigacion antes de ampliar esa frontera explicitamente.
Proximo: contratos y funciones puras nuevos, luego dispatch/API. Sin implementacion,
migracion ni suite nueva; ultima validacion 303 §135. Ley fija, M3-T1 EN PROGRESO,
confirmacion investigacion y activacion EIPD bloqueadas. Sin commit/push.
