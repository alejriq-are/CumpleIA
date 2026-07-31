# ADR: Alcance de la lógica adaptativa en el motor de puntaje (Autodiagnóstico)

**Número:** pendiente de asignar según secuencia del repositorio
**Fecha:** 2026-07-31
**Estado:** Aceptado
**Módulo:** Módulo 1 — Autodiagnóstico, Tarea 3
**Relacionado:** Tarea 0 (catálogo de preguntas), Tarea 2 (motor de puntaje)

## Contexto

El catálogo de preguntas (Tarea 0) contiene 50 preguntas activas sin datos de aplicabilidad por rubro o tamaño de empresa: todas aplican por igual a cualquier organización. El plan de Tarea 3 menciona "lógica adaptativa" sin especificar su alcance, lo que exige definir hasta dónde llega esa adaptabilidad sin inventar contenido no anclado a la fuente CCS (principio que CLAUDE.md pide respetar).

Al analizar el problema se identificaron cuatro capas distintas que estaban siendo tratadas como una sola:

1. Aplicabilidad de preguntas del cuestionario según rubro/tamaño.
2. Clasificación de riesgo de las brechas detectadas (alto/medio/bajo).
3. Plazos de resolución de brechas según tamaño/rubro/riesgo.
4. Profundidad y extensión de la documentación de salida (reporte) para organizaciones de alto riesgo.

Cada capa tiene una relación distinta con las fuentes normativas disponibles:

- La CCS define las categorías de riesgo (alto/medio/bajo) y su significado → la capa 2 está anclada a fuente.
- La CCS no define aplicabilidad condicional de preguntas por rubro/tamaño → la capa 1 no tiene fuente.
- La CCS no define plazos de resolución por tamaño/rubro. Se consideró inicialmente definir esos plazos como "buena práctica" propia de CumploIA (ej. 30 días para riesgo alto en sector financiero, 60 días para riesgo medio), pero eso implica que la app fije criterios normativos sin respaldo en ninguna fuente.

Existen además dos fuentes legítimas para resolver el punto de los plazos que no se habían considerado:

- La política de gobernanza interna de cada organización, que define cómo esa organización resuelve sus propias brechas.
- Los instructivos y ordenanzas del Consejo Directivo de la Agencia de Protección de Datos Personales, creada por la Ley 21.719.

Se verificó el estado de esta segunda fuente: la Ley 21.719 fue publicada el 13 de diciembre de 2024 y entra en vigencia el 1 de diciembre de 2026. El Consejo Directivo (tres integrantes) se encontraba en proceso de ratificación en el Senado a mayo de 2026, con asunción de funciones esperada para octubre de 2026. Es decir, a la fecha de este ADR la fuente existe legalmente pero no tiene contenido publicado todavía.

## Decisión

Se tratan las cuatro capas por separado:

**1. Cuestionario (aplicabilidad de preguntas) — diferido.**
`GET /diagnostico/cuestionario` sigue devolviendo las 50 preguntas activas sin filtrar por rubro/tamaño. Queda anotado en backlog como pendiente hasta que el catálogo incorpore datos de aplicabilidad.

**2. Clasificación de riesgo — se implementa en Tarea 3.**
Las categorías alto/medio/bajo y su criterio de asignación están definidas en la guía CCS, por lo que el motor de puntaje puede calcular el nivel de riesgo de cada brecha sin inventar contenido.

**3. Plazos de resolución de brechas — CumploIA no fija plazos propios.**
En su lugar, se incorpora un mecanismo de documentos de referencia asociable a cada brecha o al diagnóstico completo, con dos tipos:

- `politica_interna_gobernanza`: documento que la propia organización sube o vincula, donde define sus propios criterios y plazos de resolución. CumploIA no interpreta su contenido, solo lo referencia.
- `instructivo_agencia`: catálogo estructurado igual que el catálogo CCS (Tarea 0), inicialmente vacío, para los instructivos que emita el Consejo Directivo de la Agencia. Se puebla cuando exista contenido publicado (no antes de octubre–diciembre de 2026).

El reporte de brechas muestra el nivel de riesgo (capa 2) y, si existen, enlaces a estos documentos de referencia, sin proponer un plazo propio de CumploIA.

**4. Profundidad de la documentación de salida — variación de plantilla.**
Se implementa como variación del reporte según el nivel de riesgo ya calculado en la capa 2 (más detalle y extensión para brechas de riesgo alto). No introduce reglas normativas nuevas, solo variación de presentación.

## Consecuencias

- Se elimina el riesgo de que CumploIA emita contenido normativo no anclado a fuente (plazos de cumplimiento propios).
- Queda pendiente en backlog:
  - Datos de aplicabilidad de preguntas por rubro/tamaño en el catálogo (capa 1).
  - Población del catálogo `instructivo_agencia` cuando la Agencia publique instructivos, estimado no antes de octubre–diciembre de 2026 (capa 3).
  - Diseño de la funcionalidad de carga/vinculación de `politica_interna_gobernanza` a nivel de Organization (capa 3).
- El modelo de datos de Tarea 3 debe incluir una entidad de "documento de referencia" (tipo, título, fecha, organización o brecha asociada, archivo/URL) además del cálculo de nivel de riesgo.
- Se mantiene consistencia con el principio de CLAUDE.md de no generar contenido no anclado a la fuente normativa.

## Fuentes consultadas

- Ley 21.719 y creación de la Agencia de Protección de Datos Personales, Chile: publicación 13-dic-2024, entrada en vigencia 1-dic-2026.
- Estado del Consejo Directivo (ratificación en Senado, asunción estimada octubre 2026).
