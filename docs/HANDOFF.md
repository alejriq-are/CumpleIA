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

16/10: expediente documental MVP confirmado e implementado: consulta y descarga
JSON de RAT asociado, evaluacion de licitud/LIA y EIPD disponible; versiones,
hashes, eventos ficticios solo sobre EIPD exacta, fuentes oficiales consultadas y
gates MVP. G1 alcance definido; restantes pendientes/bloqueados. No acta real,
verificacion de facultades reales ni liberacion. RAT es snapshot asociado, no
inventario completo/atestacion de actualidad. Consulta solo development/test.
78 backend dirigidas, ocho nuevas UI/cliente y una integrada real aprobadas;
tipos/lint/formato correctos. No migracion ni cambio de opt-in/politica global.
Aceptacion organizacion previa permanece ligada solo al sucesor infancia.
[Contrato operativo y pendientes](project/m3-t1-mvp-alcance-propuesto.md).
EIPD bloqueada; datos ficticios; sin merge/despliegue. Consultar CI del HEAD exacto.

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
