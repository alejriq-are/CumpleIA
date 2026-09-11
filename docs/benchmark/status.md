# Estado del benchmark RAT

## F1.26 — Cerrada: operational viability FAIL; no seleccionado

El [cierre F1.26](F1.26_Cierre_Qwen3_Coder_recalibrado_RAT_2026-09-11.md)
consolida Qwen3-Coder-30B-A3B-Instruct Q4_K_M recalibrado con `-ncmoe 32`:
pp512 518.83, tg128 37.86, pp16384 69.80 y tg256 30.89 tok/s.
`/v1/messages`, template nativo, SRT y Claude Code funcionan. La mini-prueba
agentic logró PASS fuerte (5/5 tests independientes, aproximadamente 5m43s).

La RAT `f1.26-rat-active-org-qwen3-coder-30b-a3b-local`, baseline
`c29ac90b7486a8ab02af282b6c0978eaccd5809c`, conserva **TIMEOUT**:
límite 1800 s, duración 1814.351633 s. El verifier nominal dio FAIL por la
regex `organizaciones[0]` frente a `memberships[0]`, pero hay **FAIL real**:
prop `activeOrganization` no declarada y `OrganizacionForm` no importado
(dos errores de type-check), helper con `null` ante parámetro ausente,
selector reutilizable y tests frontend incompletos.

**Operational viability: FAIL. No seleccionado.** Se mantiene
**Qwen3.6-35B-A3B IQ4_XS como candidato local principal**, con revisión de
integración y sin convertir F1.25-B en PASS. No quedan ejecuciones pendientes
para cerrar F1.26; nuevas calibraciones requieren evidencia separada.

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
### Punto de reanudación histórico — 2026-09-08 (superado por F1.25)

La jornada se cierra después de completar y documentar F1.24H.

Estado al cierre:

- F1.24H cerrado como `CANDIDATO NO SELECCIONADO`;
- commit de cierre: `37787b8`;
- rama `main` sincronizada con `origin/main`;
- working tree limpio al finalizar el cierre de F1.24H;
- no se inicia F1.24I;
- se preservan los resultados de las evaluaciones locales realizadas y no deben repetirse sin una justificación técnica nueva.

**Próxima actividad:** realizar una revisión consolidada de los resultados de F1.24 y decidir si se cierra la búsqueda de candidatos locales formalizando la arquitectura local + nube de CumpleIA, o si existe un candidato adicional que justifique abrir F1.24I.

No ejecutar nuevas pruebas de modelos antes de esta decisión.
## Histórico preservado

[F1.23D — Ronda calibrada cerrada](F1.23D_Cierre_ronda_calibrada_RAT_2026-09-07.md):
Claude Sonnet 5 PASS 4/4; Qwen3-4B y DeepSeek V4 Pro FAIL 1/4.
Sus resultados y evidencias se conservan. No se ejecutan benchmarks autoritativos
ni se eliminan evidencias como parte de este cierre documental.
