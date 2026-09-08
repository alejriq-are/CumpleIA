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

### F1.24G — Preflight Devstral Small 2 24B

**Estado:** CERRADO — CANDIDATO NO SELECCIONADO

Se evaluó `Devstral-Small-2-24B-Instruct-2512` en cuantización `Q4_K_M` como siguiente candidato local.

Artefacto:

- archivo: `mistralai_Devstral-Small-2-24B-Instruct-2512-Q4_K_M.gguf`;
- SHA-256: `bfd11c8679c6b81eb43763505465d7dcfa72e460ab1c220ecc235a3efadd7f7f`;
- tamaño visible: aproximadamente 14 GB;
- runtime: llama.cpp `b95502b`;
- arquitectura `mistral3`: soportada por el runtime fijado.

Durante el preflight se detectó que WSL disponía inicialmente de aproximadamente 16 GiB de RAM. Se aumentó la asignación a 24 GB y se repitió desde cero el gate local 8K.

Resultado definitivo 8K:

- carga del modelo: PASS;
- respuesta exacta `F1.24G-8K-LOCAL-OK`: PASS;
- VRAM: 7796 / 8151 MiB;
- prompt throughput: aproximadamente 17.4 tok/s;
- generation throughput reproducido: aproximadamente 0.54 tok/s.

La ampliación de memoria WSL no produjo una mejora material en la velocidad de generación. El rendimiento observado resulta insuficiente para una corrida agentic con timeout de 1800 segundos.

Por esta razón no se ejecutaron los gates posteriores de Claude Code/SRT, 16K, 24K, prefill limpio 24K, 32K ni la corrida funcional RAT.

**Decisión:** Devstral-Small-2-24B-Instruct-2512 no se selecciona como candidato local definitivo.

A partir de F1.24G, las evaluaciones locales posteriores utilizan WSL con 24 GB de memoria asignada. Los resultados históricos anteriores permanecen válidos bajo las condiciones registradas en sus respectivas ejecuciones.

Documento: `docs/benchmark/F1.24G_Preflight_devstral_small_2_24b_2026-09-08.md`.
### F1.24H — Preflight Qwen3.6-35B-A3B

**Estado:** CERRADO — CANDIDATO NO SELECCIONADO

Se evaluó Qwen3.6-35B-A3B IQ4_XS como candidato local de mayor capacidad mediante un runtime llama.cpp paralelo con soporte `qwen35moe`.

Resultados principales:

- runtime llama.cpp b10837 / commit `5202104b59ada9005db079eea43882a2b7bf5802`: PASS;
- integridad del artefacto GGUF: PASS;
- offload CUDA 42/42 capas: PASS;
- inferencia local 8K: PASS;
- transporte SRT hacia `llm-local.cumpleia`: PASS;
- Claude Code con template nativo: FAIL por `Jinja Exception: System message must be at the beginning`;
- mitigación con `chatml`: FAIL, porque el modelo continúa generando `<think>` incluso con `--reasoning off` y `--reasoning-budget 0`;
- pruebas 16K/24K/32K: NOT RUN;
- benchmark funcional RAT: NOT RUN.

**Decisión:** Qwen3.6-35B-A3B IQ4_XS no se selecciona como candidato local definitivo debido a incompatibilidad de integración con Claude Code. El descarte no se atribuye a falla de inferencia ni de transporte SRT.

Documento: `docs/benchmark/F1.24H_Preflight_qwen36_35b_a3b_2026-09-08.md`.

## Histórico preservado

[F1.23D — Ronda calibrada cerrada](F1.23D_Cierre_ronda_calibrada_RAT_2026-09-07.md):
Claude Sonnet 5 PASS 4/4; Qwen3-4B y DeepSeek V4 Pro FAIL 1/4.
Sus resultados y evidencias se conservan. No se ejecutan benchmarks autoritativos
ni se eliminan evidencias como parte de este cierre documental.
