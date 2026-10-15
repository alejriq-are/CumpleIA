# Piloto DS-001: protocolo y resultados

## Criterios antes del intercambio

1. Deepseek reconoce ID/HEAD, sus accesos y el unico archivo editable sin pedir
   el repo entero ni conversaciones anteriores.
2. Devuelve diff aplicable limitado al test; declaraciones separadas de ejecucion.
3. El ejecutor reproduce las pruebas del contrato; maximo una devolucion concreta.
4. Ningun cambio a producto, permisos, datos, bindings, politica o activacion.
5. Registrar caracteres de entrada/salida, tiempo activo del usuario/ejecutor,
   numero de intercambios y uso que muestre cada plataforma, si esta disponible.
   Comparar con una tarea similar hecha solo en ChatGPT; sin inventar ahorro.

## Ensayo local del protocolo (no es ejecucion de Deepseek)

| Afirmacion | Estado | Verificador | Metodo / artefacto | Fecha |
| --- | --- | --- | --- | --- |
| Base funcional 39dfad5 y CI 38819932076 success | CI_verificada | Codex | Git/GitHub Actions comprobados en tarea anterior; docs/HANDOFF.md | 2026-10-15 |
| 10 pruebas del empaquetador/validador aprobadas | ejecutado_localmente | Codex | python3 -m unittest discover -s scripts/tests -v; scripts/tests/test_handoff.py | 2026-10-15 |
| Parche de ensayo queda sin aplicar | ejecutado_localmente | Codex | test_check_does_not_apply_or_validate_tests verifica bytes intactos | 2026-10-15 |
| Deepseek implemento DS-001 / pruebas del producto aprobadas | pendiente | Nadie | Falta intercambio real y retorno | — |

Ajustes incorporados al ensayo: preservar bytes exactos del archivo al calcular
hash (sin strip), bloquear cambios de modo/symlinks/renombres, exigir checkout
limpio y HEAD exacto, rechazar sobrepresupuesto y rutas fuera del contrato. CI de otro SHA se rechaza. Fallo
de red no se presenta como CI aprobada. Applicabilidad no significa aceptacion.

## Segunda fase: retorno real

Usuario lleva el paquete a Deepseek si usa chat manual y trae diff + reporte.
Registrar capacidad declarada y criterio 1 antes de evaluar implementacion.
Codex inspecciona el diff; ejecuta check del protocolo, aplica tras revision y
corre checks dirigidos del contrato. No fingir un ensayo independiente con otra
instancia de ChatGPT. Si hay un fallo, devolver causa y evidencia minima; repetir
solo checks afectados. Ajustar contexto/presupuesto/criterios segun ese resultado.

Resultado externo, metricas de consumo, reintentos y ajustes posteriores:
pendientes de la respuesta real. Hasta entonces el ADR permanece en piloto.
