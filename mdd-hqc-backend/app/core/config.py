"""Application configuration loaded from environment and `.env`."""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    """Pydantic settings for MDD-HQC (env vars + defaults)."""

    # Configuración de lectura de .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    LOG_LEVEL: str = "INFO"
    LOG_FILE_NAME: str = "mdd_hqc.jsonl"
    LOG_MAX_BYTES: int = 10_485_760
    LOG_BACKUP_COUNT: int = 5
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    # Configuración de LLMs
    # Cambiado a host.docker.internal para que Docker vea tu Windows
    LMSTUDIO_BASE_URL: str = "http://host.docker.internal:1234/v1"
    LMSTUDIO_MODEL_NAME: str = "meta-llama-3.1-8b-instruct"
    
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL_NAME: str = "deepseek/deepseek-r1-distill-llama-70b"
    
    # Cambiamos el default a lmstudio para mayor seguridad
    LLM_PROVIDER: str = "lmstudio"

    @property
    def cors_origins(self) -> list[str]:
        """Returns the configured CORS origins as a normalized list."""
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

config = Config()