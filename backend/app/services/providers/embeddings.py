"""Cliente de embeddings, resuelto según EMBEDDING_PROVIDER/EMBEDDING_MODEL.

Agregar un proveedor nuevo: crear una clase que implemente `EmbeddingClient`
y agregarla a `_EMBEDDING_ADAPTERS`. Nada fuera de este módulo debe importar
un SDK de embeddings directamente.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.services.providers.errors import (
    EmbeddingRateLimitError,
    ProveedorNoSoportadoError,
)

if TYPE_CHECKING:
    from app.core.config import Settings

__all__ = [
    "EmbeddingClient",
    "EmbeddingRateLimitError",
    "get_embedding_adapter_class",
    "get_embedding_client",
]


class EmbeddingClient(ABC):
    """Interfaz común para clientes de embeddings, sin importar el proveedor."""

    @abstractmethod
    async def embed(self, texts: list[str], *, input_type: str) -> list[list[float]]:
        """Devuelve un vector por texto de entrada, en el mismo orden."""


class VoyageEmbeddingClient(EmbeddingClient):
    def __init__(self, settings: "Settings") -> None:
        if not settings.voyage_api_key:
            raise RuntimeError("VOYAGE_API_KEY no configurada en el .env")
        import voyageai

        self._voyageai = voyageai
        self._client = voyageai.AsyncClient(api_key=settings.voyage_api_key)
        self._model = settings.embedding_model

    async def embed(self, texts: list[str], *, input_type: str) -> list[list[float]]:
        try:
            result = await self._client.embed(
                texts=texts, model=self._model, input_type=input_type
            )
        except self._voyageai.error.RateLimitError as exc:
            raise EmbeddingRateLimitError(str(exc)) from exc
        return result.embeddings


_EMBEDDING_ADAPTERS: dict[str, type[EmbeddingClient]] = {
    "voyage": VoyageEmbeddingClient,
}


def get_embedding_adapter_class(provider: str) -> type[EmbeddingClient]:
    """Resuelve el adaptador de embeddings sin instanciarlo.

    No requiere la API key: se usa para validar EMBEDDING_PROVIDER al
    arrancar la app, aunque la clave todavía no esté configurada (dev).
    """
    try:
        return _EMBEDDING_ADAPTERS[provider.strip().lower()]
    except KeyError:
        raise ProveedorNoSoportadoError(
            "embeddings", provider, sorted(_EMBEDDING_ADAPTERS)
        ) from None


def get_embedding_client(settings: "Settings") -> EmbeddingClient:
    adapter_cls = get_embedding_adapter_class(settings.embedding_provider)
    return adapter_cls(settings)
