from typing import Any, List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # API Configuration
    PROJECT_NAME: str = "PreciosRegulados.uy"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Secrets (definir en .env en producción)
    SECRET_KEY: str = "CHANGE_ME_IN_ENV"

    # CORS - Parse from comma-separated string or list
    # Valores por defecto apuntan a dominios productivos; sobrescribir en .env para dev
    # En desarrollo: CORS_ORIGINS="http://localhost:5173,http://localhost:3000"
    CORS_ORIGINS: str = "https://cuantocuestauruguay.com,https://www.cuantocuestauruguay.com,http://localhost:5173"

    # Security headers
    SECURE_HEADERS_ENABLED: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS: bool = True

    # Database
    # SQLite para desarrollo, PostgreSQL para producción (sobrescribir en .env)
    DATABASE_URL: str = "sqlite:///./preciosregulados.db"
    # DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/preciosregulados"

    # CKAN API
    CKAN_API_URL: str = "https://catalogodatos.gub.uy/api/3/action"
    CKAN_COMBUSTIBLES_RESOURCE_ID: str = "62bacbab-9bae-4316-af56-7c1bf468f546"

    # Scheduler
    ETL_SCHEDULE_HOUR: int = 2
    ETL_SCHEDULE_MINUTE: int = 0

    # Rate limiting
    RATE_LIMIT_GENERAL: int = 60  # requests/min
    RATE_LIMIT_ETL: int = 5  # requests/min para /api/v1/etl/*

    # ETL admin API key (set in .env for production, empty = no protection in dev)
    ETL_API_KEY: str = ""

    # Sentry
    SENTRY_DSN: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from comma-separated string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [url.strip() for url in self.CORS_ORIGINS.split(",") if url.strip()]
        return self.CORS_ORIGINS


settings = Settings()
