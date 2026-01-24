from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "PreciosRegulados.uy"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # CORS - Parse from comma-separated string or list
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/preciosregulados"
    
    # CKAN API
    CKAN_API_URL: str = "https://catalogodatos.gub.uy/api/3/action"
    CKAN_COMBUSTIBLES_RESOURCE_ID: str = "62bacbab-9bae-4316-af56-7c1bf468f546"
    
    # Scheduler
    ETL_SCHEDULE_HOUR: int = 2
    ETL_SCHEDULE_MINUTE: int = 0
    
    # Sentry
    SENTRY_DSN: str = ""
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Convert CORS_ORIGINS from comma-separated string to list
        if "CORS_ORIGINS" in env_settings.data:
            cors_str = env_settings.data["CORS_ORIGINS"]
            if isinstance(cors_str, str):
                env_settings.data["CORS_ORIGINS"] = [url.strip() for url in cors_str.split(",")]

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()
