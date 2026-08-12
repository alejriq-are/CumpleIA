# IA, RAG y portabilidad de proveedor

## Dos conceptos distintos de “cambiar de IA”

### 1. Cambiar el agente que desarrolla el código

El proyecto es portable entre Claude Code, Codex, Cursor, Copilot, Gemini u otros porque el código vive en Git y usa tecnologías estándar. Para no perder contexto se propone `AGENTS.md` como memoria neutral.

### 2. Cambiar el LLM utilizado por la aplicación CumpleIA

La aplicación ya tiene una abstracción correcta, pero **hoy solo hay un adaptador LLM implementado**:

- `anthropic` -> `AnthropicLLMClient`

Y un adaptador de embeddings:

- `voyage` -> `VoyageEmbeddingClient`

Por lo tanto, cambiar `LLM_PROVIDER=openai` por env var **no basta todavía**. Primero hay que implementar un `OpenAILLMClient` compatible con `generate()` y `generate_structured()` y registrarlo en `_LLM_ADAPTERS`.

La misma regla aplica a embeddings.

## Uso de IA en Módulo 1

El diseño actual separa correctamente tareas deterministas y generativas:

- Scoring: determinista, sin LLM.
- Riesgo base/ajustado: determinista.
- Mapeo Pregunta -> Sección -> Obligación: estructurado.
- Narrativa del informe: LLM.
- Contexto legal: RAG.
- Citas: filtradas para aceptar solo referencias recuperadas realmente.

## Guardarraíles observados

- Tool calling estructurado para la salida del informe.
- Validación de `finding_id`.
- Validación de citas contra retrieval real.
- Eliminación determinista de conteos de “brechas/hallazgos” declarados por el LLM, para evitar una segunda fuente de verdad.

## Fuentes usadas por el informe

`FUENTES_ANCLAJE = ["ley_21719", "guia_ccs"]`.

La Ley 19.628 no se usa como fuente narrativa de ese informe, según la decisión documentada en ADR 0002.

## Riesgo de portabilidad en embeddings

`KnowledgeChunk.embedding` está definido como `Vector(1024)`. Si se cambia a un modelo con otra dimensión, se debe diseñar una migración o reingesta; no es una sustitución transparente por env var.
