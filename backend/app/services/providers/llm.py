"""Cliente de LLM, resuelto según LLM_PROVIDER/LLM_MODEL.

Sin consumidores todavía (los módulos de generación de documentos son de
Fase 1+), pero la fábrica queda lista para que ese código futuro nunca
importe un SDK de LLM directamente. Agregar un proveedor nuevo: crear una
clase que implemente `LLMClient` y agregarla a `_LLM_ADAPTERS`.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.services.providers.errors import ProveedorNoSoportadoError

if TYPE_CHECKING:
    from app.core.config import Settings

__all__ = ["LLMClient", "get_llm_adapter_class", "get_llm_client"]


class LLMClient(ABC):
    """Interfaz común para clientes de LLM, sin importar el proveedor."""

    @abstractmethod
    async def generate(self, *, system: str, prompt: str) -> str:
        """Genera texto a partir de un prompt de usuario y un system prompt."""

    @abstractmethod
    async def generate_structured(
        self, *, system: str, prompt: str, schema: dict, tool_name: str = "responder"
    ) -> dict:
        """Fuerza al modelo a responder vía tool-calling validado contra `schema`.

        Para salidas que el sistema debe poder validar (CLAUDE.md sección 5:
        "produce salidas estructuradas que el sistema valida"), no para texto
        libre — usar `generate()` para eso.
        """


class AnthropicLLMClient(LLMClient):
    def __init__(self, settings: "Settings") -> None:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY no configurada en el .env")
        import anthropic

        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.llm_model

    async def generate(self, *, system: str, prompt: str) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")

    async def generate_structured(
        self, *, system: str, prompt: str, schema: dict, tool_name: str = "responder"
    ) -> dict:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            tools=[
                {
                    "name": tool_name,
                    "description": "Devuelve la respuesta estructurada según el schema.",
                    "input_schema": schema,
                    "strict": True,
                }
            ],
            tool_choice={"type": "tool", "name": tool_name},
        )
        for block in response.content:
            if block.type == "tool_use" and block.name == tool_name:
                return block.input
        raise RuntimeError(
            "El modelo no devolvió una respuesta estructurada pese a tool_choice forzado."
        )


_LLM_ADAPTERS: dict[str, type[LLMClient]] = {
    "anthropic": AnthropicLLMClient,
}


def get_llm_adapter_class(provider: str) -> type[LLMClient]:
    """Resuelve el adaptador de LLM sin instanciarlo.

    No requiere la API key: se usa para validar LLM_PROVIDER al arrancar
    la app, aunque la clave todavía no esté configurada (dev).
    """
    try:
        return _LLM_ADAPTERS[provider.strip().lower()]
    except KeyError:
        raise ProveedorNoSoportadoError(
            "LLM", provider, sorted(_LLM_ADAPTERS)
        ) from None


def get_llm_client(settings: "Settings") -> LLMClient:
    adapter_cls = get_llm_adapter_class(settings.llm_provider)
    return adapter_cls(settings)
