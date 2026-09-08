# Benchmark RAT

Este directorio reúne el diseño, las validaciones y los cierres autoritativos
del benchmark reproducible de CumpleIA.

## Estado vigente

- [Estado del benchmark](status.md): F1.24 cerrada como evaluación del nivel LOCAL; el verificador escala los FAIL.
- [F1.24F — Preflight Qwen2.5-Coder-7B](F1.24F_Preflight_qwen25_coder_7b_2026-09-08.md): gate local 8K PASS y conectividad Claude Code/SRT PASS, pero compatibilidad exact-response FAIL; no seleccionado.
- [F1.24E — Preflight Qwen2.5-Coder-14B](F1.24E_Preflight_qwen25_coder_14b_2026-09-07.md): gates técnicos hasta 24K, pero prefill 24K agotó el timeout; no seleccionado.
- [F1.24 — Evaluación del nivel local](F1.24_Evaluacion_candidato_local_2026-09-07.md): Qwen3.5-9B validado para tareas de bajo riesgo; el contrato C FAIL 1/4 debe escalar.
- [F1.24D — Preflight del siguiente candidato local](F1.24D_Preflight_siguiente_candidato_local_2026-09-07.md): Qwen3-Coder-30B-A3B-Instruct superó gates técnicos, pero agotó el timeout funcional con contrato 1/4.

## Histórico

- [F1.23D — Cierre de ronda calibrada](F1.23D_Cierre_ronda_calibrada_RAT_2026-09-07.md): Claude PASS; Qwen y DeepSeek FAIL; evidencias verificadas.
- [F1.23B — Verifier calibrado de selector](F1.23B_Verifier_calibrado_selector_2026-09-04.md): baseline rechazado y solución retenida aprobada por comportamiento.
- [F1.23A — Calibración del verifier de selector](F1.23A_Calibracion_verifier_selector_2026-09-04.md): separa comportamiento observable de convenciones de nombres.
- [F1.22D — Cierre de la tercera ronda RAT](F1.22D_Cierre_tercera_ronda_RAT_2026-09-04.md): tres FAIL efectivos; evidencias trusted verificadas.
- [F1.22B — Verifier de selector de organización](F1.22B_Verifier_selector_organizacion_2026-09-04.md): baseline rechazado y solución dorada aprobada.
- [F1.22A — Diseño de selector de organización activa](F1.22A_Diseno_tercera_tarea_selector_organizacion_2026-09-04.md): tercera tarea funcional definida; verifier pendiente.
- [F1.21E — Cierre de la segunda ronda RAT](F1.21E_Cierre_segunda_ronda_RAT_2026-09-04.md): Claude PASS; Qwen y DeepSeek FAIL; evidencias trusted verificadas.
- [F1.21D — Reparación de sockets SRT](F1.21D_Reparacion_sockets_SRT_2026-09-04.md): TMPDIR corto por corrida y sonda SRT aprobados.
- [F1.21C — Configuración de la segunda ronda](F1.21C_Configuracion_segunda_ronda_RAT_2026-09-04.md): baseline, hashes y tres candidatos fijados; gate técnico aprobado.
- [F1.21B — Verifier de organización actual](F1.21B_Verifier_organizacion_actual_2026-09-04.md): perfil trusted validado; baseline rechaza y solución dorada aprueba.
- [F1.21A — Diseño de la segunda tarea](F1.21A_Diseno_segunda_tarea_organizacion_actual_2026-09-04.md): contrato fijado para `organization-current-v1`.
- [F1.20D — Cierre de la primera ronda RAT](F1.20D_Cierre_primera_ronda_RAT_2026-09-04.md): cierre autoritativo de la tarea `rat-na-section-v1` con tres candidatos.
- [F1.20B — Tarea y verifier N/A por sección](F1.20B_Tarea_y_verifier_NA_por_seccion_2026-09-04.md): contrato funcional y perfil trusted de la tarea.
- [F1.20A — Preflight de la primera ronda](F1.20A_Preflight_primera_ronda_2026-09-04.md): hardening y gate funcional previo.
- [F1.19E — Retención, limpieza y cierre de evidencia](F1.19E_Retencion_limpieza_evidencia_2026-09-04.md): validación independiente, cierre y conservación de evidencia.

Los documentos anteriores permanecen en este directorio como historial del
diseño. Las evidencias de ejecución no forman parte del repositorio y se
conservan cerradas bajo la raíz trusted del harness.
