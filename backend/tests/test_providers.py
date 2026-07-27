"""Tests de la capa de selección de proveedor LLM/embeddings.

Verifica que LLM_PROVIDER/EMBEDDING_PROVIDER seleccionen el adaptador
correcto y que un proveedor no soportado falle explícitamente (fail-fast),
sin depender de API keys reales.
"""

import pytest

from app.services.providers.embeddings import (
    VoyageEmbeddingClient,
    get_embedding_adapter_class,
    get_embedding_client,
)
from app.services.providers.errors import ProveedorNoSoportadoError
from app.services.providers.llm import (
    AnthropicLLMClient,
    get_llm_adapter_class,
    get_llm_client,
)


def test_embedding_adapter_class_selecciona_voyage():
    assert get_embedding_adapter_class("voyage") is VoyageEmbeddingClient


def test_embedding_adapter_class_es_insensible_a_mayusculas_y_espacios():
    assert get_embedding_adapter_class(" Voyage ") is VoyageEmbeddingClient


def test_embedding_adapter_class_proveedor_no_soportado_falla_explicito():
    with pytest.raises(ProveedorNoSoportadoError, match="openai"):
        get_embedding_adapter_class("openai")


def test_llm_adapter_class_selecciona_anthropic():
    assert get_llm_adapter_class("anthropic") is AnthropicLLMClient


def test_llm_adapter_class_proveedor_no_soportado_falla_explicito():
    with pytest.raises(ProveedorNoSoportadoError, match="cohere"):
        get_llm_adapter_class("cohere")


def test_get_embedding_client_usa_embedding_provider_de_settings(monkeypatch):
    from app.core.config import Settings

    settings = Settings(_env_file=None, supabase_url="https://x.supabase.co")
    monkeypatch.setattr(settings, "embedding_provider", "openai")

    with pytest.raises(ProveedorNoSoportadoError):
        get_embedding_client(settings)


def test_get_llm_client_usa_llm_provider_de_settings(monkeypatch):
    from app.core.config import Settings

    settings = Settings(_env_file=None, supabase_url="https://x.supabase.co")
    monkeypatch.setattr(settings, "llm_provider", "openai")

    with pytest.raises(ProveedorNoSoportadoError):
        get_llm_client(settings)


def test_get_embedding_client_sin_api_key_falla_con_mensaje_claro():
    from app.core.config import Settings

    settings = Settings(
        _env_file=None, supabase_url="https://x.supabase.co", voyage_api_key=""
    )
    with pytest.raises(RuntimeError, match="VOYAGE_API_KEY"):
        get_embedding_client(settings)


def test_get_llm_client_sin_api_key_falla_con_mensaje_claro():
    from app.core.config import Settings

    settings = Settings(
        _env_file=None, supabase_url="https://x.supabase.co", anthropic_api_key=""
    )
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        get_llm_client(settings)
