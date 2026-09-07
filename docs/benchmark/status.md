# Estado del benchmark RAT

## F1.24 — Cierre documental hasta F1.24C; evaluación abierta

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

Qwen3.5-9B no mejoró el 1/4 de Qwen3-4B en esta tarea y **no queda seleccionado
como candidato local final**. F1.24 continúa con otro candidato local de mayor
capacidad. El [preflight F1.24D](F1.24D_Preflight_siguiente_candidato_local_2026-09-07.md)
descarta Qwen3-Coder-Next por memoria y registra la descarga verificada de
Qwen3-Coder-30B-A3B-Instruct. Los gates operativo y de transporte a 8K, 16K,
24K y 32K pasaron; el prefill limpio 24K fue 24.000 tokens en 64.515 s
(~372 tok/s). La corrida funcional v2 agotó el timeout: 1812.713011 s,
agentExitCode `null`, contrato 1/4 y evidencia verificada. El candidato no
queda seleccionado como local final; F1.24 continúa con otro candidato.

## F1.24E — Siguiente candidato preparado

El siguiente preflight propone Qwen2.5-Coder-14B-Instruct Q4_K_M desde el GGUF
oficial de Qwen (8.99 GB, contexto base 32K). El gate operativo local 8K pasó;
el transporte SRT 8K también pasó. Faltan contextos superiores y la corrida
funcional.

**Pausa operativa:** servidor activo en 8K; reinicio a 16K pendiente. Ninguna
prueba 16K o superior se ha iniciado para este candidato.

## Histórico preservado

[F1.23D — Ronda calibrada cerrada](F1.23D_Cierre_ronda_calibrada_RAT_2026-09-07.md):
Claude Sonnet 5 PASS 4/4; Qwen3-4B y DeepSeek V4 Pro FAIL 1/4.
Sus resultados y evidencias se conservan. No se ejecutan benchmarks autoritativos
ni se eliminan evidencias como parte de este cierre documental.
