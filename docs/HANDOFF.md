# Handoff vigente de CumpleIA

## Entrada y limites

Participan usuario, ChatGPT/Codex y Deepseek. Claude no tiene rol activo.
Leer AGENTS.md y docs/ai/handoff-contract.md. Para una tarea acotada, leer solo
su paquete y los ADR relevantes, no toda la historia de status.md.
EIPD bloqueada; datos ficticios; sin merge/despliegue. Credenciales nunca via chat.

## Estado operativo

Base verificada para preparar este contrato: 39dfad5, rama
feature/m3-t1-licitud-persistencia. CI 38819932076 success, comprobada por Codex
via GitHub Actions 2026-10-15: 4454 backend aprobadas, 1 omitida; frontend e
integrada aprobados. Esta observacion es un snapshot, no el HEAD perpetuo.
Antes de transferir, generar scripts/handoff.py state --remote: ese resultado
identifica el HEAD exacto de la tarea. Una CI anterior no prueba un commit nuevo.

## Bloque funcional vigente — producto

18/10: recorrido manual ficticio de Bases de licitud cerrado: clientes,
trabajadores e infancia; guardado/reapertura, dos resoluciones, revisiones negativas,
decision documental y grant/revocacion. Decision conservada, nuevas decisiones
bloqueadas en UI tras recarga; JSON con faculty_current=false y EIPD/datos reales
bloqueados. Escritura temporal local restituida a false y override retirado.
CI funcional de 33039d3 success (39040075836), Handoff tambien success.
No hay pruebas pendientes del recorrido acotado; pendientes de producto/operacion
no equivalen a aprobacion para datos reales. Evidencia y limites en
project/m3-t1-recorrido-frontend.md; hallazgos en backlog.md. Sin merge/despliegue.

16/10: piloto sigue ficticio. Usuario define escenario [FICTICIA] Comercial Piloto
Andes SpA / [FICTICIA] Persona Facultada Piloto, contactos example.invalid y RUT
simulados. V2 genera actas descargables HTML/JSON con marca ACTA DE PRUEBA,
DATOS FICTICIOS, SIN VALOR JURIDICO; referencias SIMULADA- exigidas en servidor.
Revision pendiente/no realizada por defecto; cualquier otra decision es simulada.
Escenario no sustituye identidad tecnica de sesion, no registra aceptacion real
ni cierra gates. V1 e historiales conservados, datos reales y EIPD bloqueados.
20 backend/guardas, 13 UI/cliente y una integrada real aprobadas; tipos/lint/formato.
Docker/WSL restablecido; CI previa b229fb3 aprobada. Verificar nuevo HEAD/CI.
[Contrato y evidencia](project/m3-t1-piloto-preparacion.md).
Pendientes reales: empresa/actas/facultades, revision humana y controles de piloto.
Piloto poblado local validado: clientes/trabajadores con LIA borrador e infancia
con dos resoluciones, dos revisiones negativas, dos eventos documentales y
otorgamiento/revocacion de facultades (ocho registros historicos). Restauracion
de 39 tablas conserva conteos/checksums/politicas y lecturas API como app_user;
aislamiento, facultad revocada y EIPD bloqueada comprobados en la copia.
Ejecutor fijo: backend `python -m scripts.run_populated_pilot`; limpia solo fixtures
y copia propias. Evidencia: project/pilot-evidence/populated-history-restore-20261016.json.
41 pruebas dirigidas y recorrido local poblado aprobados; CI del previo 8a8903f
aprobada. Comprobar candidato por HEAD. No certifica produccion ni backup externo.
Sin migraciones, provision de identidades, merge o despliegue.

## Proxima transferencia

Estado: DS-001 a DS-005 terminados. DS-005 agrega reordenacion de evidencia;
25 UI aprobadas (7 independientes), tipos/lint/formato aprobados tras Prettier
final de Codex. El bucle Deepseek se detuvo tras tres fallos de formato;
no acredita autonomia completa. Ver docs/ai/pilot-results.md y results/DS-005.json.
Permisos acotados, no agente general; no reenviar pilotos terminados.
BENCH-001: tres pares pequenos, 5 puntos cuota local vs 22 delegados; no ahorro
observado, cuota compartida y par 2 contaminado. No extrapolar. Informe:
docs/ai/benchmarks/BENCH-001.md. 18 regresiones nuevas, comando CI 91 aprobadas.

Desde raiz y checkout limpio:

    python3 scripts/handoff.py state --remote
    python3 scripts/handoff.py packet --task docs/ai/tasks/DS-001.json --remote > /tmp/CumpleIA-DS-001.json

No hay bloque Deepseek activo. Decision: seleccionar bloques coherentes caso a
caso; microtareas directas en Codex. Ejecutor consolidado y validado localmente
sin API: 36 unitarias + 25 Chromium. Guia: docs/ai/deepseek-automation.md.

Modalidad recomendada por preferencia del usuario: lanzador local + API,
`python3 scripts/deepseek_run.py ID`. Por defecto prepara sin gasto. Clave dedicada
y servicio verificados; trece generaciones pagadas entre pilotos y BENCH-001. Nuevas tareas requieren
contrato y autorizacion de gasto; no hay lote mensual autorizado. Ver
docs/ai/deepseek-automation.md.

Fallback manual: copiar el JSON completo a Deepseek y pedir diff unificado + reporte, sin aplicar.
Al volver, guardar el diff fuera del checkout y comprobarlo usando el HEAD del
paquete (nunca sustituirlo por el HEAD actual para eludir una base obsoleta):

    python3 scripts/handoff.py check --task docs/ai/tasks/DS-001.json --base HEAD_DEL_PAQUETE --patch /tmp/DS-001.patch

El check no aplica el parche ni aprueba pruebas. Codex revisa, aplica y ejecuta
los checks del contrato. Solo tras aceptar el bloque se hace commit/push bajo
la autorizacion del usuario. Mantener un unico responsable por tarea.

## Evidencia y continuidad

Tabla de verificacion, resultados del ensayo local y criterios del piloto:
docs/ai/pilot-results.md. Accesos: docs/ai/access-matrix.md.
Los handoffs fechados previos permanecen como antecedentes para preservar enlaces.
Nuevos cierres historicos, solo cuando aporten una decision o evidencia necesaria,
van a docs/archive/. No duplicar el historial en este archivo.
