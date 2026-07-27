from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.services.providers.embeddings import get_embedding_adapter_class
from app.services.providers.llm import get_llm_adapter_class

settings = get_settings()

# Fail-fast: LLM_PROVIDER/EMBEDDING_PROVIDER deben tener un adaptador
# registrado antes de levantar la app. No requiere las API keys todavía
# (eso se valida recién al usar el cliente), solo que el nombre del
# proveedor sea uno soportado.
get_embedding_adapter_class(settings.embedding_provider)
get_llm_adapter_class(settings.llm_provider)

app = FastAPI(
    title="CumpleIA API",
    description="API para adecuación a la Ley N° 21.719 de Protección de Datos Personales (Chile)",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
