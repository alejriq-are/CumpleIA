"""Fábricas de clientes LLM/embeddings, resueltas por variables de entorno.

Agregar un proveedor nuevo = agregar un adaptador en `embeddings.py` o
`llm.py` y registrarlo en el diccionario correspondiente. La lógica de
negocio (rag.py, ingest.py) nunca importa un SDK de proveedor directamente:
solo usa `get_embedding_client` / `get_llm_client`.
"""

from app.services.providers.embeddings import EmbeddingClient, get_embedding_client
from app.services.providers.errors import ProveedorNoSoportadoError
from app.services.providers.llm import LLMClient, get_llm_client

__all__ = [
    "EmbeddingClient",
    "LLMClient",
    "ProveedorNoSoportadoError",
    "get_embedding_client",
    "get_llm_client",
]
