# Benchmark BENCH-001: Codex directo y delegacion Deepseek

Fecha local: 2026-10-15 (medicion UTC 2026-10-16). Base Git: 6ee359a237f9e69b92aeda3e530b0136c3c4acc9.

Resultado: **no se observo ahorro operativo de cuota al delegar estos bloques pequenos**.
No es una estimacion causal de tokens OpenAI ni de ahorro para funciones mayores.

Tres pares, tres casos por bloque: texto (edad/interes superior), selector
(sensibles/ruta), casilla (categoria/titulares). Criterios comunes de guardar,
vaciar/alternar, solo lectura, una PATCH, evidencia intacta y EIPD bloqueada.
Orden prefijado L1 D1 D2 L2 L3 D3; no aleatorio. Misma base, fixtures, formateador,
Chromium, tipos y lint. Ambos brazos usan Codex para supervision; delegacion
incluye preparacion de llamadas, revision, diagnostico y correcciones, no solo API.

## Mediciones por bloque

Puntos de cuota = diferencia observada de porcentaje de cuenta en ventana 5h;
no tokens exactos. Tiempo = inicio del bloque hasta validacion, incluida coordinacion.

| Bloque | Ejecutor | Par | Puntos cuota Codex | Segundos | Calls Deepseek | Correcciones Codex |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| L1 | Codex | 1 | 2 | 16.71 | 0 | 0 |
| D1 | Deepseek | 1 | 6 | 78.82 | 2 | 0 |
| L2 | Codex | 2 | 1 | 18.03 | 0 | 0 |
| D2 | Deepseek | 2 | 13 | 208.11 | 2 | 1 |
| L3 | Codex | 3 | 2 | 16.99 | 0 | 0 |
| D3 | Deepseek | 3 | 3 | 39.82 | 1 | 0 |

Totales observados: Codex directo **5 puntos**, delegacion **22 puntos**.
Preparacion comun **5 puntos adicionales** (28% a 33%), incluidos protocolo,
adaptador y consulta documental; cierre/documentacion/publicacion fuera de los
intervalos de bloques, sin repartir artificialmente entre brazos. No omitir ese
costo al decidir si vale la pena construir/reutilizar el sistema.

Calidad: 9/9 pruebas locales y 9/9 delegadas aprobadas; seis mutaciones de
actualizacion perdida detectadas. Local: 3/3 primeras entregas aprobadas;
Deepseek: 1/3. D1 requirio una devolucion por guardado duplicado y ajuste de
interpretacion de lista de fragmentos (sin cambio de codigo). D2 requirio una
devolucion por alcance y reparacion de localizador por Codex. D3 paso a la primera.
Ninguna fixture ni assertion se debilito para pasar. No cambios de producto.
Suite combinada de 18 regresiones incluida en CI; comando ampliado: **91 aprobadas**,
tipos/lint/formato aprobados.

Deepseek: **5 llamadas, 37499 tokens**, estimacion **USD0.005383896–0.010767792**
con tarifas de referencia 2026-10-15; no factura ni limite de cobro del proveedor.
Presupuesto total USD0.20. Saldos inmediatos no mostraron diferencia por llamada;
no acredita gratuidad ni cargo exacto. Sin llamadas fuera del limite.

## Limitaciones que impiden afirmar ahorro exacto

- Cuota redondeada/compartida; otras sesiones y retraso de contabilizacion no
  pudieron excluirse. No convertir puntos a dolares ni a tokens OpenAI.
- Una conversacion larga, sin sesiones independientes; contexto, cache, orden y
  aprendizaje influyen. Tres pares no acreditan significacion estadistica.
- Par 2 contaminado por un defecto del protocolo: getByLabel exact incluia texto
  de opciones del select. Se diagnostico en D2, conto tiempo/consumo y se cambio
  al combobox con prefijo unico; L2 se beneficio del diagnostico. Protocolo original
  y enmienda conservados. El timeout se redujo despues; no ocultar esta deriva.
- Adaptador adicional sobre ejecutor existente; no es una comparacion de flujo
  estable sin preparacion. Tests similares, no identicos; no extrapolar a
  arquitectura, RLS, migraciones ni desarrollo funcional complejo.

## Decision operativa

Para bloques pequenos como estos, mantener implementacion directa en Codex:
este flujo de delegacion no justifico ahorro y agrego coordinacion. Deepseek API
es economico, pero precio de API y ahorro de cuota ChatGPT son medidas distintas.
Mantener delegacion para bloques coherentes mayores solo con contrato/ejecutor
estable, presupuesto y revision final; no ampliar permisos por este benchmark.
Si se repite, congelar el adaptador y los localizadores antes, usar sesiones
comparables y muestreo suficiente. No hay gasto recurrente autorizado.

EIPD bloqueada, datos ficticios; sin merge/despliegue. Fuentes/artefactos:
- [Datos y snapshots](BENCH-001.json)
- [Protocolo original](BENCH-001-protocol-original.json) y [enmienda](BENCH-001-protocol.json)
- Evidencia local: /tmp/cumpleia-deepseek/BENCH-001/ (respuestas, logs, mutaciones reversibles, adaptador).
- [OpenAI: cuota compartida, contexto y cache afectan uso; API no representa costo de suscripcion](https://learn.chatgpt.com/docs/pricing).
- [Deepseek: tarifas API de referencia](https://api-docs.deepseek.com/quick_start/pricing/).
