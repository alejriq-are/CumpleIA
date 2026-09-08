# Estado del benchmark RAT

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
El candidato no se selecciona como reemplazo local de mayor capacidad. En ese punto no se continuó la búsqueda de candidatos locales; posteriormente
la evaluación se reabrió como F1.24F con un candidato de menor tamaño.

## F1.24F — Preflight cerrado por compatibilidad Claude Code

La búsqueda de un candidato local de mayor capacidad se reabrió posteriormente
con Qwen2.5-Coder-7B-Instruct Q4_K_M. El artefacto oficial de Qwen fue
verificado mediante SHA256
`509287f78cb4d4cf6b3843734733b914b2c158e43e22a7f4bf5e963800894d3c`.

El gate local 8K pasó y mostró 164.551 tok/s de prompt y 69.401 tok/s de
generación. La conectividad Claude Code -> SRT -> `llm-local.cumpleia` ->
llama-server también quedó confirmada.

Sin embargo, el candidato no devolvió el marcador exacto requerido por
Claude Code en la ejecución canónica. En lugar de
`F1.24F-8K-SRT-OK`, respondió:

`I am Claude, your AI assistant. How may I assist you today?`

El resultado se clasifica como conectividad PASS y compatibilidad
Claude Code/instruction-following FAIL, no como HARNESS_ERROR ni fallo de SRT.
Por este motivo no se ejecutan 16K, 24K, 32K, prefill limpio 24K ni una
corrida funcional RAT.

Qwen2.5-Coder-7B-Instruct no queda seleccionado como reemplazo local.
F1.24F se cierra preservando el resultado y sin repetir pruebas.
## Histórico preservado

[F1.23D — Ronda calibrada cerrada](F1.23D_Cierre_ronda_calibrada_RAT_2026-09-07.md):
Claude Sonnet 5 PASS 4/4; Qwen3-4B y DeepSeek V4 Pro FAIL 1/4.
Sus resultados y evidencias se conservan. No se ejecutan benchmarks autoritativos
ni se eliminan evidencias como parte de este cierre documental.
