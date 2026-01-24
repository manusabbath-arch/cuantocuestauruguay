from typing import List, Any, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    # API Configuration
    PROJECT_NAME: str = "PreciosRegulados.uy"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # CORS - Parse from comma-separated string or list
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
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
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from comma-separated string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [url.strip() for url in self.CORS_ORIGINS.split(",") if url.strip()]
        return self.CORS_ORIGINS


settings = Settings()
