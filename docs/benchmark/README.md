# Benchmark RAT

Este directorio reúne el diseño, las validaciones y los cierres autoritativos
del benchmark reproducible de CumpleIA.

## Estado vigente

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
