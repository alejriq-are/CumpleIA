# Estado del benchmark RAT

## F1.25 — Cerrada: viabilidad operativa con revisión de integración

El [cierre F1.25](F1.25_Cierre_LLM_local_Claude_Code_RAT_2026-09-10.md)
consolida las pruebas por capas, RTX 5060 detectada, sweep con mejor punto
`ncmoe=32`, pp/tg 16K y transporte/SRT sin degradación relevante. Claude Code
con `--name` alcanzó 41.56 t/s al evitar la request auxiliar de título.
Registra el parche Jinja, `CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1`, los 16 tests
aprobados y SHA-256 del harness histórico.

| Etapa | Estado preservado | Interpretación |
|---|---|---|
| F1.25-A | HARNESS_ERROR | Calibración: request inicial 23315 tokens frente a 16K; Docker apagado |
| F1.25-B | FAIL | 64K, agentExitCode 0, 630.223109 s, timedOut false; checks generales PASS y verifier contractual FAIL |

En B, el rechazo nominal por `organizaciones[0]` frente a `memberships[0]`
coexiste con defectos reales del selector y de sincronización de `organizationId`.
`npm ci`, type-check y tests pasaron en una copia de validación, pero los tests
duplican el helper en JS sin importar el TS real. El resultado funcional es
parcial; no se modifica la RAT ni se convierte el FAIL en PASS.

Qwen3.6-35B-A3B IQ4_XS en el OMEN es viable para desarrollo con Claude Code,
con revisión de integración; conviene reservar Claude/DeepSeek para tareas
críticas. F1.25 no requiere otra RAT para su cierre documental. Una futura
calibración del verifier o mejora de pruebas se tratará como trabajo separado.

**Nota histórica F1.24H:** produjo un hallazgo válido con configuración MoE
subóptima; **5.23 tok/s NO representa el límite del hardware/modelo**.
Se conserva esa medición y toda la historia anterior.

## F1.24 — Evaluación del nivel local cerrada

El [documento F1.24](F1.24_Evaluacion_candidato_local_2026-09-07.md) registra
la identidad del modelo, configuración, métricas y evidencia reportada.

| Etapa | Estado | Resultado |
|---|---|---|
| F1.24A | PASS | Qwen3.5-9B Q4_K_M operativo a 8K/16K/24K/32K; full GPU offload 33/33 |
| F1.24B | PASS | Claude Code fuera y dentro de SRT; chatml, thinking desactivado y dependencia de `/etc/hosts` documentados |
| F1.24C | FAIL | Corrida válida `rat-active-organization-selector-v2-qwen3.5-9b-local-r2`: contrato 1/4, 21.685523 s, agentExitCode 0, sin timeout |

La evidencia de r2 fue reportada como verificada: `status=PASS`, `VERIFY_EXIT=0`.
Esto no cambia el FAIL funcional. El intento inicial queda como HARNESS_ERROR
por Docker Desktop detenido: fallo de infraestructura, no del modelo.

La política de enrutamiento asigna tareas de bajo riesgo al nivel LOCAL, de
riesgo medio a DeepSeek y de alto riesgo a Claude. El verificador confiable
decide el resultado: un FAIL escala la tarea. Qwen3.5-9B queda validado para
el nivel LOCAL por operación y transporte; el contrato 1/4 limita su resultado
en esta tarea y obliga a escalarla, sin promoverlo a otros niveles.

El [preflight F1.24D](F1.24D_Preflight_siguiente_candidato_local_2026-09-07.md)
descarta Qwen3-Coder-Next por memoria y registra Qwen3-Coder-30B-A3B-Instruct:
superó gates técnicos, pero agotó el timeout funcional y obtuvo contrato 1/4.

## F1.24E — Preflight cerrado por rendimiento

El siguiente preflight propone Qwen2.5-Coder-14B-Instruct Q4_K_M desde el GGUF
oficial de Qwen (8.99 GB, contexto base 32K). El gate operativo local 8K pasó;
el transporte SRT 8K, 16K y 24K también pasó. El prefill limpio 24K agotó
1800 s tras procesar 14.336 tokens; no se prueban 32K ni la corrida funcional.
El candidato no se selecciona como reemplazo local de mayor capacidad. No se
continúa la búsqueda de candidatos locales para F1.24.

## Histórico preservado

[F1.23D — Ronda calibrada cerrada](F1.23D_Cierre_ronda_calibrada_RAT_2026-09-07.md):
Claude Sonnet 5 PASS 4/4; Qwen3-4B y DeepSeek V4 Pro FAIL 1/4.
Sus resultados y evidencias se conservan. No se ejecutan benchmarks autoritativos
ni se eliminan evidencias como parte de este cierre documental.
