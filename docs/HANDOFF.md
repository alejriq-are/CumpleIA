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

## Proxima transferencia

Piloto DS-001: ampliar prueba de bloqueo del editor durante una respuesta
pendiente. Solo frontend/e2e/child-adolescent-editor.spec.ts editable.
Contrato: docs/ai/tasks/DS-001.json. Contexto: ese test y su componente.
Estado: DS-001, DS-002 y bloque DS-003 terminados. DS-003: tres tareas, una
generacion, sin reparaciones; 13 UI y checks aprobados. Ver docs/ai/pilot-results.md.
No reenviar pilotos terminados; ahorro neto ChatGPT aun no demostrado.

Desde raiz y checkout limpio:

    python3 scripts/handoff.py state --remote
    python3 scripts/handoff.py packet --task docs/ai/tasks/DS-001.json --remote > /tmp/CumpleIA-DS-001.json

Modalidad recomendada por preferencia del usuario: lanzador local + API,
`python3 scripts/deepseek_run.py ID`. Por defecto prepara sin gasto. Clave dedicada
y servicio verificados; tres generaciones pagadas, una por piloto/bloque. Nuevas tareas requieren
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
