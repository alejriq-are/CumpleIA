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
| Retorno API DS-001 y validacion local | ejecutado_localmente | Deepseek propone; Codex corrige/valida | Resultado real detallado abajo | 2026-10-15 |

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

Resultado externo y ajustes: ver ejecucion real siguiente. El flujo sigue en piloto;
una tarea no acredita autonomia ni ahorro total de ChatGPT.

## Extension para API local

16 pruebas del protocolo/lanzador aprobadas localmente: transporte falso con
clave ficticia, preparacion sin leer clave ni enviar, sin segunda llamada al
reusar salida, rechazo de pruebas inventadas y base obsoleta, codigo intacto y
sin clave en logs. Fecha 2026-10-15; ejecutor Codex; metodo unittest en scripts/tests.
Esta extension fue simulada. La llamada real posterior se registra por separado.

## Ejecucion real DS-001 — 2026-10-15

Base enviada: 69e2041b4fa81eb9eecc858ac2dba3acde57f014. Una generacion
API deepseek-flash, pensamiento deshabilitado, sin reintento. Clave dedicada
verificada; saldo API disponible USD4.70 y CNY5.39. El intento previo fallo en
consulta de saldo HTTP401 antes de enviar contenido; la nueva salida se uso solo
tras confirmar ese fallo y corregir la credencial.

Uso del proveedor: 7878 tokens entrada, 996 salida, 8874 total, 0 cache.
Estimacion por tarifas de referencia: USD0.0017793–0.0035586; no es factura.
Delta inmediato: USD0.00 y CNY0.00. Precision/contabilizacion del saldo no permite
atribuir un cargo exacto. No interpretar delta cero como prueba gratuita.
Evidencia local fuera de Git: /tmp/cumpleia-deepseek/DS-001-69e2041b4fa8-corrected-key/
(response.json, expense.json, balance-before.json, balance-after.json, candidate.patch).

Retorno: ID/HEAD y archivo correctos; declaro todos los checks no_ejecutado.
No aceptado directamente: diff corrupto (conteo de hunk/contexto), y duplico
la prueba en lugar de ampliarla. Codex no aplico ese diff: adapto sus assertions
al test existente, agrego conteo PATCH despues de liberar y valido localmente.
Sin segunda generacion ni cambios al componente/producto. La aportacion del
modelo y la correccion humana/Codex quedan diferenciadas.

Validacion: 10 pruebas Chromium del editor y 20 unitarias del protocolo/lanzador
aprobadas; type-check, ESLint, Prettier, Ruff y Black aprobados. Datos ficticios;
EIPD bloqueada. No se repitio suite backend porque no cambia producto/backend.

Ajustes: prompt exige ampliar test existente y diff con contexto literal/conteos;
parche corrupto conserva gasto y genera result.json con rechazo explicito,
cubierto con regresion simulada. No se normalizan/aplican diffs automaticamente.

Conclusion: acceso API, transferencia, medicion y validacion funcionan; retorno
requiere revision y reparacion local. No habilitar aplicacion/publicacion desatendida.
Falta una segunda tarea independiente para validar los ajustes y definir presupuesto
antes de lotes. No hay comparacion controlada con ChatGPT solo: no afirmar ahorro
neto ni extrapolar costo por tarea desde esta muestra.

## Ejecucion real DS-002 — 2026-10-15

Base 6c9699408d09cd5d559ddba31aa2a99817a70c10. Contrato DS-002: ampliar
solo lectura parametrizado para Notas, checkbox y retirada deshabilitados, sin
PATCH ni cambios a producto. Paquete con un archivo (sin componente redundante).
Una generacion, sin reintento: 4667 entrada + 576 salida = 5243 tokens, cache 0;
3.97 segundos para llamada/saldo/validacion. Estimacion USD0.00104565–0.0020913,
no factura; delta saldo inmediato USD0.00/CNY0.00, cargo exacto no confirmado.
Evidencia local: /tmp/cumpleia-deepseek/DS-002/ (paquete, respuesta, parche, gasto,
saldos y snapshots de cuota sin credenciales).

Parche aplicable con offset; ID/HEAD/alcance correctos, checks no_ejecutado.
Se aplico tal como recibido y pasaron 10 Chromium, type-check y ESLint.
Prettier fallo; unica correccion local: formato automatico, recheck aprobado.
Ninguna correccion semantica, segundo envio ni nueva prueba duplicada. Cambios
finales: cinco lineas de assertions en test existente. No suite backend/protocolo
repetida: no se modificaron sus implementaciones.

Comparacion observable: tokens Deepseek totales 8874 → 5243 (-40.9%); reparacion
semantica requerida → ninguna. Tareas parecidas, no identicas: menor contexto y
menor cambio tambien explican diferencia, no prueba causal de mejora del prompt.
La primera muestra no midio cuota ChatGPT. DS-002 obtuvo snapshots Codex de cuenta
86% → 90% en ventana 5h y 29% → 30% semanal, antes del cierre/documentacion/push.
Son porcentajes redondeados y compartidos, sin tokens/turno, con posibles otras
sesiones; no atribuirlos como costo exacto ni afirmar ahorro frente a ChatGPT solo.
No hubo ejecucion control de esta tarea en ChatGPT (evita gastar dos veces).

Decision: conservar revision de Codex; flujo util para ejecucion acotada, ahorro
neto ChatGPT aun no demostrado. Para reducir coordinacion, preparar varios
contratos simples en una sola planificacion, ejecutar Deepseek localmente y
revisar un bloque coherente una vez. Siguiente ensayo: lote con presupuesto
acordado y registro automatico; no habilitado/autorizado por estas dos pruebas.
No nuevas mejoras al lanzador en DS-002. EIPD bloqueada; datos ficticios.

## Bloque DS-003 — tres tareas, 2026-10-15

Usuario autorizo presupuesto USD0.20; limite adicional tres iteraciones.
Base 463b83589480d8b69a5f2093c3b2cbec7fc36be8. Tres pruebas nuevas de un
mismo bloque: añadir/editar/guardar evidencia preservando la anterior; quitar
la evidencia; cambiar grupos declarados conservando evidencia. Una sola PATCH
por recorrido; fixtures existentes y EIPD bloqueada. Contrato DS-003.json.

Ejecutor experimental fuera del checkout: /tmp/cumpleia-deepseek/DS-003/run_block.py.
Una reserva previa por llamada y saldo consultado; limite admite volumen usando
bytes UTF8 + margen y tarifa pico de referencia, no tope de facturacion del
proveedor. Error de transporte incierto detiene sin duplicar la llamada.
Entrega JSON con reemplazo old/new de ancla unica; ejecutor genera diff mediante
difflib y verifica ID/base/ruta, preservacion del archivo y exactamente tres tests.
Puede pedir correccion estructural hasta el limite; esa rama no se ejercito.
Candidato guardado fuera del repo; no ejecuta codigo/comandos del modelo ni publica.
No es aun un agente general ni un lanzador de produccion reproducible para lotes.

Resultado: una generacion, 5.79 segundos (API/saldo/validacion), sin intercambios
manuales por subtarea. 8126 tokens entrada + 1235 salida = 9361, cache 0.
Estimacion USD0.0019599–0.0039198, no factura. Delta inmediato saldo CNY0.00 y
USD0.00; cargo exacto no acreditado por precision/contabilizacion de saldo.
Resumen persistido: docs/ai/results/DS-003.json. Originales locales en directorio
DS-003 (packet, respuesta, parche, saldos, gasto y candidato aislado).

Una revision final de Codex: parche aceptado sin reparaciones de codigo ni formato.
13 pruebas Chromium aprobadas (10 existentes + 3 nuevas), type-check, ESLint y
Prettier aprobados. Codigo de producto, permisos y activacion intactos. No se
repitieron backend ni unitarias del lanzador porque no cambia su implementacion.

Comparacion: tres tareas recibidas/validadas/publicadas juntas; ningun paso del
usuario entre subtareas. No convertir esto en ahorro exacto ChatGPT: falta control
comparable y medicion por tarea. La preparacion del ejecutor experimental tambien
consume coordinacion Codex; no ocultarla ni atribuirla a trabajo Deepseek.
Autonomia verificada: preparacion/entrega del bloque; pruebas y aceptacion ejecutadas
por Codex. No se verifico bucle autonomo de correccion a partir de tests ni acceso
Deepseek a terminal. Siguiente decision: consolidar ejecutor reutilizable solo si
se decide continuar; este piloto no autoriza gasto recurrente ni lotes nuevos.

## DS-004 — correccion desde fallo real controlado, 2026-10-15

Base 3a24ec974f1fa28b1792befd500ab2623b73380c. Presupuesto referencia USD0.20,
maximo tres llamadas. Bloque nuevo: notas vacias persistidas null; añadir/quitar
una evidencia temporal preservando la original; recuperar un 403 y guardar las
mismas notas sin status falso, alerta residual ni activacion EIPD. Tres tests
nuevos; componente, harness y tests anteriores intactos.

Deepseek entrego codigo en llamada 1. Reporto checks como objeto, no lista;
ejecutor inicial se detuvo antes de pruebas con AttributeError. Codex reviso la
respuesta existente, normalizo solo interpretacion de metadatos y reviso el codigo
antes de ejecutarlo. No hubo segunda generacion para ese problema ni reparacion
manual del codigo. Esta friccion del prototipo tambien cuenta como coordinacion.

Copia aislada del frontend desde Git, sin .env; dependencias existentes reutilizadas.
API key no se hereda a subprocess de pruebas; comandos fijos del ejecutor, ningun
comando arbitrario del modelo. Fallo controlado introducido por Codex en una
expectativa de referencia del test nuevo B, no en el codigo original de Deepseek.
Red real: 1 fallo/15 aprobadas; Expected PRUEBA: FALLO_CONTROLADO_DS004,
Received PRUEBA: evidencia. Deepseek recibio log y corrigio el literal en llamada 2.
El ejecutor acepto solo ese literal JSON, conservando toBe y el resto del codigo;
comparo contra la entrega inicialmente revisada para impedir debilitamiento.
Luego ejecuto automaticamente 16 UI, type-check, ESLint y Prettier: aprobados.
Sin intervencion Codex/usuario entre fallo, decision de reparacion y checks finales.

Total dos llamadas: entrada 10471, salida 1444, total 11915 tokens, cache 0.
Estimacion USD0.00243705–0.0048741, no factura; delta inmediato USD0.00/CNY0.00
por llamada, cargo exacto no confirmado. Bucle red/feedback/fix/checks 17.01 segundos.
Resumen persistido docs/ai/results/DS-004.json; originales y ejecutores
experimentales /tmp/cumpleia-deepseek/DS-004/. Codigo final aplicado exactamente
al checkout base; no repetir suite backend por un cambio de tests UI.

Autonomia validada: implementar bloque y reparar una expectativa a partir del
fallo real del ejecutor. No prueba que Deepseek resuelva errores arbitrarios de
producto, RLS, migraciones o politica: esa reparacion esta limitada a un literal
sembrado deliberadamente. Codex conserva revision inicial/final y publicacion;
no hay shell libre para el modelo ni agente general listo para lotes recurrentes.
Siguiente alcance razonable: correcciones UI/test acotadas con criterios fijos y
preservacion de assertions, ampliar permisos solo por bloque. Ahorro neto de
ChatGPT sigue sin medicion comparable; preparacion/revision del prototipo tiene
costo y no debe omitirse. EIPD bloqueada, datos ficticios, sin merge/despliegue.
