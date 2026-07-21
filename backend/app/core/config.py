from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ancla al .env de la raíz del repo (no al cwd): así docker compose (cwd=raíz)
# y uvicorn directo desde backend/ (cwd=backend/) leen el mismo archivo.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_ENV_FILE = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
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

    @model_validator(mode="before")
    @classmethod
    def _exigir_supabase_url(cls, valores: object) -> object:
        """Falla rápido y con mensaje claro si SUPABASE_URL no se resolvió.

        Sin esto, un .env ausente o mal ubicado produce el genérico "Field
        required" de pydantic, que no dice dónde buscar. Aquí se apunta
        directamente al archivo que Settings intenta leer.
        """
        if isinstance(valores, dict) and not valores.get("supabase_url"):
            raise ValueError(
                "SUPABASE_URL no está definido. Verifica que exista "
                f"{_ENV_FILE} con esa variable, o expórtala como variable "
                "de entorno antes de arrancar el backend."
            )
        return valores

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
