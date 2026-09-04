# Ronda 1 — Transparencia de preguntas N/A por sección

Implementa la mejora pendiente «Preguntas N/A» del Módulo 1. El objetivo es
evitar que una persona interprete el puntaje de una sección como si todas sus
preguntas hubieran sido aplicables.

## Comportamiento requerido

1. Cada elemento de `puntaje_por_seccion` de `GET /diagnostico/actual` debe
   incluir dos enteros no negativos:
   - `respondidas`: preguntas de esa sección cuya respuesta vigente sea
     `Sí`, `Parcial` o `No`;
   - `no_aplica`: preguntas de esa sección cuya respuesta vigente sea `N/A`.
2. Los conteos se calculan por la relación del catálogo
   `Pregunta.seccion_id`. Respuestas ausentes o de preguntas que no pertenecen
   al catálogo no se cuentan. Una sección sin respuestas entrega ambos
   conteos en cero.
3. El dashboard de resultados muestra, para cada sección, el puntaje, las
   respondidas y las N/A con etiquetas inequívocas.
4. El HTML de `GET /diagnostico/informe/exportar` muestra los mismos dos
   conteos por sección en la tabla de puntajes.
5. No cambies la fórmula existente: N/A y preguntas sin responder continúan
   fuera del denominador del puntaje, y el puntaje global conserva su
   renormalización actual.
6. Actualiza el contrato TypeScript y agrega pruebas automatizadas que cubran
   mezcla de respuestas, una sección sin respuestas y la exclusión de N/A del
   puntaje.

## Restricciones

- No agregues migraciones ni dependencias.
- No modifiques archivos bajo `docs/benchmark/runner/`.
- No ejecutes seeds ni uses credenciales externas.
- Mantén compatibilidad con Python 3.12 y el TypeScript estricto actual.
- Limita los cambios a esta mejora y su documentación/pruebas directamente
  relacionadas.

El resultado autoritativo será determinado por verificadores trusted fuera del
workspace candidato. Que los tests modificables por el candidato pasen no
constituye por sí solo un PASS.
