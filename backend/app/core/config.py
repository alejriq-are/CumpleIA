from functools import lru_cache

from pydantic import model_validator
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
    # supabase_url es OBLIGATORIO: de él se deriva la URL del JWKS y el emisor (iss)
    # esperado al validar los access tokens. Sin él la app no puede autenticar y
    # no debe arrancar.
    supabase_url: str
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # IA
    anthropic_api_key: str = ""
    voyage_api_key: str = ""

    # Backend
    secret_key: str = ""
    environment: str = "development"
    debug: bool = True
    allowed_origins: list[str] = ["http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def _require_secrets_in_production(self) -> "Settings":
        """En producción, exige los secretos que en dev pueden quedar vacíos.

        Así el arranque en producción falla ruidosamente si el .env está
        incompleto, sin frenar el desarrollo local (donde estos valores son
        opcionales).
        """
        if self.is_production:
            faltantes = [
                nombre
                for nombre, valor in (
                    ("SUPABASE_SERVICE_ROLE_KEY", self.supabase_service_role_key),
                    ("SUPABASE_ANON_KEY", self.supabase_anon_key),
                    ("SECRET_KEY", self.secret_key),
                )
                if not valor
            ]
            if faltantes:
                raise ValueError(
                    "Variables obligatorias en producción sin definir: "
                    + ", ".join(faltantes)
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
