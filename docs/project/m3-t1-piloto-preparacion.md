# Preparacion de organizacion piloto — simulacion de desarrollo

16/10/2026. Usuario confirma que aun no existe organizacion piloto: preparar y
probar con datos ficticios. Este bloque no produce actas o facultades reales ni
reemplaza la revision juridica de la organizacion. Datos reales y EIPD bloqueados.

## Flujo implementado

Consultar expediente documental MVP en la pagina M3. Con una facultad ficticia
vigente registrada en el panel de aceptacion, declarar referencias ficticias en
el nuevo formulario: revision juridica, entorno, control de accesos, restauracion,
retencion, soporte e incidentes. Se permiten faltantes y decisiones negativas o
pendientes; el resultado los enumera. No crea/upload documentos ni consulta URLs.

POST `/licitud/treatments/{tid}/assessments/{aid}/pilot-preparation/v1` exige
edit_content, suscripcion y tenant validos, entorno development/test, data_kind
ficticios, facultad explicita propia vigente y hashes de los tres documentos
consultados. Releer expediente tras cambio; revocacion o hashes distintos rechazan
la simulacion. Actores/habilitaciones no son campos editables. Series compartidas
serializan frente a cambio M3/revocacion. No toca selector ni politica global.

`preparation_complete` solo acredita presencia de referencias de prueba y decision
ficticia acepta. No acredita autenticidad, vigencia o suficiencia del contenido.
Salida evidence_status declarada_no_verificada, persistence simulacion_no_registrada;
legal_acceptance pendiente_organizacion_piloto. mvp_ready, allows_real_data,
authorizes_action y can_confirm false. EIPD deshabilitada. No se escribe un evento
de aceptacion ni se cierra G2/G5 por referencias completas. Cambiar el formulario
retira el resultado anterior; rechazo conserva referencias para corregirlas.

## Restauracion local ensayada

Ejecutor fijo desde backend: `python -m scripts.check_pilot_restore`.
Requiere Docker local y contenedor ya existente cumpleia_db (pgvector/pgvector:pg16).
Fuente exclusiva cumpleia_eipd_tests_20261009, head/rol/registro verificados por
las barreras existentes. No admite argumentos ni destinos externos. Crea solo
cumpleia_pilot_restore_check_20261016 si no existe; copia temporal privada, rol
runtime app_user sin superuser/BYPASSRLS, checksums/conteos y politicas comparados.
No copia secretos al repo ni guarda el dump. No modifica la base de desarrollo.
Limpieza solo para copia creada por este proceso y marca propia comprobada con
shobj_description. Nunca sobrescribe/borra una base preexistente ni usa DROP FORCE.

[Resultado local](pilot-evidence/restore-development-2026-10-16.json): 39 tablas,
cuatro historiales con RLS/privilegios inmutables; origen intacto y copia retirada.
Historiales vacios en esta corrida: no prueba recuperacion de historial poblado.
Tres argumentos externos rechazados y rechazo real de destino ya existente,
conservando su marca. Error inicial en consulta de marca corregido; copias propias
identificadas y retiradas antes de ensayo final. Es una copia en el mismo servidor,
no evidencia de backup externo, restauracion de produccion, RPO/RTO o cifrado.

## Validacion y salida pendiente

87 pruebas API/DB enfocadas (nueve nuevas de preparacion), cuatro barreras del
restaurador, 11 UI/cliente (tres nuevas), tipos/lint/formato y una integrada
Chromium/API/PostgreSQL real aprobadas. Ensayo de restauracion y negativas
registrados. CI del anterior 01d1576 aprobada; nuevo candidato se verifica por HEAD.
Docker/WSL restablecido por el usuario; pruebas locales dirigidas, integrada y
restauracion repetidas satisfactoriamente antes de V2. No se reiniciaron servicios.
Sin migraciones, provision de cuentas, cambios de entorno, merge o despliegue.

Para cierre real faltan empresa/entorno piloto, persona y evidencia autentica de
facultad, acta de decision y alcance sobre documentos exactos, revision humana de
fuentes/aplicabilidad, y evidencias operativas revisadas: copia externa/cifrada,
retencion/RPO/RTO, restauracion con historial, accesos, soporte e incidentes.
No exigir empresa real para continuar desarrollo; no afirmar G2/G5 cerrados.


## Actas de prueba V2 — escenario indicado por el usuario

Escenario fijo: [FICTICIA] Comercial Piloto Andes SpA, RUT de prueba 00.000.000-0,
Calle Ficticia 123, Santiago, contacto@piloto.example.invalid; comercio minorista
en linea, clientes/trabajadores y programa de fidelizacion con menores. Persona:
[FICTICIA] Persona Facultada Piloto, RUT de prueba 00.000.001-0, Gerencia General
(representante legal simulado), facultada@piloto.example.invalid. No se verifican
RUT ni se presentan como contribuyentes/personas autenticados. Es un escenario,
no un cambio de identidad del tenant o perfil tecnico de la sesion.

POST `pilot-preparation/v2` agrega actas de prueba, preservando V1. Todas las
referencias propias del acta exigen SIMULADA- con letras mayusculas, numeros o
guiones. Acta SIMULADA-PILOTO-ACTA-001, designacion SIMULADA-PILOTO-DES-001 y fecha
2000-01-01 explicitamente simulada. No hay documento juridico real asociado.
Revisar pendiente/no realizada por defecto, sin referencia obligatoria ni revisor
inventado. Si se elige otra decision, legal_review_status simulada_sin_valor_juridico;
aceptacion real y gates siguen pendientes. Referencias tecnicas previas no se
reescriben: el acta enlaza por ID a la facultad vigente, con referencia SIMULADA-.

Descarga HTML imprimible y JSON, ambos con marca obligatoria:
ACTA DE PRUEBA, DATOS FICTICIOS, SIN VALOR JURIDICO (acentos en interfaz/artefacto).
El HTML repite la marca en cabecera y pie, escapa todo contenido; JSON conserva
watermark, data_kind, estado y escenario. Actas tambien pueden descargarse con
faltantes, explicitamente pendientes. No se persisten eventos ni se promueven
snapshots. El prefijo o data_kind no acreditan por si solos procedencia ficticia
ni validez juridica. mvp_ready/allows_real_data/can_confirm/authorizes_action false.

Validacion V2: 20 backend/guardas enfocadas (siete casos V2 nuevos), 13 UI/cliente
(dos negativas nuevas y descarga JSON pendiente), tipos/lint/formato y una
integrada real con HTML descargado, marca/escenario/leyenda contrastados. CI del
previo b229fb3 aprobada; comprobar candidato nuevo por HEAD exacto. Docker/WSL
restablecido por el usuario; no repetir pruebas amplias sin causa.


## Piloto poblado — recorrido local reproducible

Desde backend: `../.venv/bin/python -m scripts.run_populated_pilot`.
No admite argumentos ni destinos externos. Primero verifica DB fija/head,
registro de politica vacio y runtime app_user. Luego fixtures locales conocidas
pueblan el escenario [FICTICIA] Comercial Piloto Andes SpA. Dos RAT y LIA borrador
se crean por API (clientes/trabajadores); la fixture infancia declara menores
antes de crear la evaluacion. No se provisionan personas reales ni identidades
operativas. Todos los textos/referencias propios son ficticios/simulados.

Historia: resolucion inicial y sucesora tras cambio de material, revision negativa
por cada una, evento documental requiere_cambios por cada una, otorgamiento y
revocacion de facultad: 2 registros en cada uno de cuatro historiales. El sucesor
no hereda aceptacion; el anterior se conserva obsoleto. Tras revocar, nuevas
aceptaciones rechazan 403 sin borrar eventos. Acta V2 conserva marca visible,
revision pendiente/no realizada y mvp_ready/allows_real_data/can_confirm false.
La simulacion del acta no se persiste como revision juridica real.

La variante interna poblada exige tenant de prueba fijo, nombre simulado,
publicacion exacta de fixture y payload/hash de politica negativa del servidor,
selector unico, head esperado y cuatro historiales ficticios del tenant. Rechaza
publicacion ajena/politica distinta antes de copiar. El ejecutor normal de
restauracion sigue exigiendo registro vacio. La declaracion data_kind o el nombre
por si solos no prueban procedencia: este ensayo acredita fixtures controladas.

[Resultado poblado](pilot-evidence/populated-history-restore-20261016.json): 39
tablas y ocho registros historicos restaurados. Conteos/checksums y politicas
coinciden; source_unchanged y temporary_database_removed true. Se contrastan por
API RAT, evaluaciones, resoluciones/revisiones/facultades/eventos y documentos
exactos del dossier, incluidos hashes. app_user conserva RLS y carece de
UPDATE/DELETE/TRUNCATE en cuatro historiales; otro tenant ve cero filas. En la
copia, confirmacion EIPD sigue 409, facultad revocada 403 y tenant ajeno 403/404.
Autenticacion de pruebas mediante override de perfil/claim sintetico: no acredita
login/JWT externo ni disponibilidad del sistema de autenticacion.

Validacion: 41 casos dirigidos de aceptacion, preparacion, guardas y recorrido
API aprobados; ensayo local poblado aprobado adicionalmente. Se corrigio una
incompatibilidad del nuevo test asincrono de guardas con el loop de pytest;
regresion combinada aprobada tras correccion. Sin cambios frontend, no se repite
Chromium. CI corre el recorrido API sin restauracion Docker; esta ultima requiere
el lanzador fijo local y no debe contabilizarse como cubierta por CI.

Fixtures y nombre de organizacion se retiran/restauran al terminar; el reporte
solo guarda metadatos, no dump, credenciales ni contenido personal. Copia temporal
con marca propia retirada, ninguna base preexistente sobrescrita. Sigue siendo
mismo servidor: no cierra backup externo/cifrado, recuperacion ante desastre,
RPO/RTO ni validacion juridica/operativa real. No hay migracion, merge o despliegue.
