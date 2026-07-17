from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Base de datos
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cumpleia"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = "dev-jwt-secret-cambiar-en-produccion"

    # IA
    anthropic_api_key: str = ""
    voyage_api_key: str = ""

    # Backend
    secret_key: str = "dev-secret-key-cambiar-en-produccion"
    environment: str = "development"
    debug: bool = True
    allowed_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
