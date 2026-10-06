# M3-T1 — Revisión de aceptación

Fecha: 2026-10-06. Estado: EN PROGRESO. Revisión documental y de código;
no modifica reglas ni amplía el alcance. Última suite completa registrada:
2998 passed (§76), posterior a exposicion readiness de composicion EIPD.
Checkpoints inferiores son históricos; el total no acredita cierre integral.

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
| Tablas, constraints, índices, JSONB y migraciones | Implementado; head local b51d3f6a9c20 | db/models.py; alembic/versions/5997a757f17b_modulo3_licitud_persistencia.py y migraciones posteriores |
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
