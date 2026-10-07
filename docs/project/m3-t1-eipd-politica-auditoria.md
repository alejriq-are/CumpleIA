# M3-T1 — Contrato de auditoria y seleccion transaccional de politica EIPD

Fecha: 2026-10-07. Checkpoint §89. Estado: contratos §90, persistencia §§91–92, servicios §93 y resolver limitado §94
implementados; autoridad personal e integracion/coordinacion con acciones pendientes.
Base: §§82–88; Ley 21.719 / Ley 19.628 reformada fija por instruccion del usuario.
Este contrato describe controles de producto; no introduce requisitos legales ni
acredita verificacion de fuentes. Resolver actual fijo sigue deshabilitado.

## 1. Identidad, publicacion y seleccion

policy_version=1 sigue siendo version del schema; no es numero de publicacion.
Cada publicacion tiene UUID propio y referencia global unica no reutilizable,
payload EipdGatePolicyV1 cerrado, hash canonico §83, actor servidor, fecha UTC,
motivo y referencia de evidencia. El payload incluye fuentes y aceptacion §82.
Una publicacion es inmutable: no UPDATE/DELETE ni correccion en sitio. Publicar
no selecciona ni activa. Hash se calcula en servidor y se comprueba al leer.

El selector global unico contiene revision entera estricta creciente, UUID de
publicacion seleccionada y UUID del ultimo evento de seleccion. Estos identificadores
no sustituyen policy_reference/version/hash ya usados por las revisiones humanas.
Cambiar cualquier evidencia/ruta/activacion exige otra publicacion y referencia.
Toda reseleccion, incluida revocacion/reversion, exige nueva publicacion: no volver
a seleccionar el mismo artefacto habilitado ni revalidar automaticamente una vieja
revision. La referencia nueva cambia el hash y exige revision humana actual.

Cada seleccion genera evento append-only: UUID, revision anterior/nueva, publicacion
anterior/nueva, hashes respectivos, actor servidor, fecha UTC, motivo y evidencia.
Revision nueva = anterior + 1; evento y selector cambian en una transaccion.
Solicitud administrativa lleva revision esperada para detectar escritor obsoleto;
no cambia el selector si no coincide. La primera seleccion usa anterior null y
revision 1 durante bootstrap privilegiado, sin rellenar historicos de tenant.

## 2. Autoridad y lectura segura

Politica es control global de plataforma, no documento editable de organizacion.
No agregar policy a inputs publicos de tenant, query/env ni permiso edit_content.
Publicacion/seleccion usan canal administrativo de servidor separado, con actor
autenticado y autorizacion explicita de plataforma; accepted_by/verified_by dentro
del payload no acreditan permiso para publicar o seleccionar. No habilitar API
administrativa en este paso ni inferir acceso por rol owner/admin del tenant.

Persistencia futura requiere tablas de control global con privilegios y RLS
explicitos: app_user solo lectura de politica/selector/evidencia permitida, sin
INSERT/UPDATE/DELETE de control; auditoria solo append desde rol administrativo
separado. No convertir conexion owner en runtime ni crear tenant ficticio. Tablas
de dominio/eventos humanos conservan organization_id, RLS y FK actuales. Una nueva
migracion definira separadamente controles globales y pruebas de privilegios/RLS.

Sin selector/publicacion/evento, con hash incoherente, version desconocida o cadena
de seleccion inconsistente: resolver real falla cerrado en operaciones EIPD;
no usa politica previa, payload cliente ni artefacto habilitado de fallback.
El artefacto fijo actual es solo fase anterior, no bootstrap implicito de politica
activa. Negativas siguen parciales respecto a preparacion/fuentes/activacion, pero
resolver corrupto no debe inventar identidad para registrarlas. La seleccion valida
de politica deshabilitada permite negativas con metadatos y bloquea positivos.
Readiness consulta un snapshot coherente en una lectura SQL del selector y su
publicacion/evento; no escribe ni reemplaza eventos. Error de integridad explicito,
sin asegurar estado vigente despues de la respuesta orientativa.

## 3. Orden de bloqueos y estabilidad hasta commit

Orden futuro unico para revisar y confirmar: advisory xact compartido 719093,
selector global FOR SHARE, despues
serie FOR UPDATE, despues relecturas de borrador/contexto M2/ultimo evento.
La lectura inicial del selector obtiene solo lock; tras adquirir ambos locks se
relee su publicacion y se valida payload/hash/evento con una fecha comun explicita.
No usar hash capturado antes de una espera como fuente de verdad. Mantener ambos
locks hasta commit/rollback del caller; no liberar entre evaluar, flush y commit.

Seleccion administrativa (§93): advisory xact lock 719093 -> selector FOR UPDATE,
revision esperada, validacion de
nueva publicacion, append de evento y actualizacion del selector, commit conjunto.
No adquiere locks de series. Advisory serializa bootstrap sin fila; siempre se
adquiere antes del selector. Publicaciones inmutables no requieren UPDATE locks.
PATCH de assessment conserva lock de serie y no adquiere despues lock de selector.
Ningun camino adquiere selector despues de serie. Operaciones con multiples series
ordenan sus UUID; este alcance no introduce tales operaciones.

La lectura compartida permite revisiones/confirmaciones de series distintas en
paralelo y bloquea cambios de selector hasta terminar. Si cambio de politica gana
el lock, la operacion lee la politica nueva; si operacion gana, el cambio espera
su commit. Funcion limitada §94 permite lock compartido sin conceder UPDATE de control a
app_user; exige JWT/perfil y no escribe. Helper exige READ COMMITTED.
READ COMMITTED y relecturas explicitas son el contrato inicial; no
suponer snapshot actualizado bajo otra isolation ni adoptar cache entre operaciones.
Timeout/deadlock se revierte completo; no reintentar solo flush ni escribir auditoria
fuera de la transaccion fallida.

Confirmacion ordinaria sin supuestos EIPD actuales conserva §§78/88: historia sola
es diagnostica y no aplica politica como gate. Para evitar inversion por contexto
que cambia durante espera, confirmacion futura adquiere selector antes de serie,
pero aplica resultado de politica solo si el contexto releido exige gate EIPD.
Readiness no es autorizacion. Politica coherente no sustituye validadores ordinarios,
RAT, dependencias, resolucion preparada ni ultima continuar vigente y coincidente.

## 4. Revocacion y evidencia de confirmacion

Revocar selecciona nueva publicacion deshabilitada con motivo/evidencia, bajo mismo
protocolo; nueva revision/hash impide nuevas confirmaciones excepcionales. Revision
humana anterior permanece legible y se vuelve obsoleta para politica nueva.
La revocacion no modifica retroactivamente assessment confirmado ni afirma que
tratamiento fue licito: requiere evaluacion operativa posterior fuera de este paso.

Confirmacion EIPD exitosa futura debe guardar evidencia append-only en su propia
transaccion: tenant/assessment, evento humano usado, publicacion/revision/evento de
seleccion, policy_version/reference/hash, hashes documento/contexto, actor y fecha.
Eso permite saber con que politica se confirmo sin depender del selector posterior.
Necesita contrato/migracion propia y aislamiento tenant; no sobrecargar el evento
humano ni rellenar evidencia para confirmaciones historicas. Sin evidencia atomica,
no habilitar exitos excepcionales. Confirmado previo solo se reemplaza despues de
superar controles y preparar esta evidencia; fallo revierte ambas escrituras.

## 5. Matriz minima antes de conectar resolver real

| Caso | Resultado exigido |
| --- | --- |
| Publicacion valida deshabilitada | Registro inmutable, sin seleccion automatica |
| Hash alterado/extra/version/bool/actor no autorizado | Rechazo sin escribir |
| Dos selecciones con misma revision esperada | Solo una avanza; otra conflicto |
| Fallo tras insertar evento antes de actualizar selector | Rollback de ambos |
| Selector ausente/incoherente | Gate EIPD falla cerrado, sin fallback |
| app_user intenta publicar/seleccionar/borrar | Denegado por privilegios/RLS |
| Seleccion commit/rollback antes de revision o confirmacion | Relectura exacta nueva/anterior, nunca mezcla |
| Revision o confirmacion mantiene FOR SHARE | Selector administrativo espera hasta commit/rollback |
| Cambio de politica con positiva previa vigente documental | Nueva revision humana requerida |
| Revocacion tras confirmacion | Evidencia original conservada; nueva accion bloqueada |
| Falla de evidencia/reemplazo de confirmado | Todo revertido, historial intacto |
| Dos series/tenants y PATCH concurrentes | Sin inversion; aislamiento y campos de servidor |
| Ordinario sin EIPD y con historia diagnostica | Flujo previo conservado |
| Ambas rutas, politica habilitada sintetica | Exito solo con todos los controles y evidencia atomica |

## 6. Secuencia de implementacion y condicion de habilitacion

Contratos §90, persistencia §§91–92 y servicios internos/lectura auditada §93
implementados. Canal interno solo admite politica deshabilitada; rol DB acredita
canal, no autentica persona. Resolver transaccional con lock compatible con runtime SELECT implementado §94,
sin conexion a acciones. Siguiente: cambio uniforme de orden de locks en acciones;
HTTP/concurrencia PostgreSQL real y casos exitosos con politica sintetica de test.

Antes de habilitar politica real: fuentes complementarias verificadas con evidencia,
aceptacion tecnica trazable al commit, suite completa y matriz anterior aprobadas.
Publicar objeto que declare verificadas no verifica fuentes reales. Fechas o eventual
postergacion legal no activan politica. Hasta entonces resolver fijo deshabilitado;
M3-T1 EN PROGRESO dentro del alcance integral.
