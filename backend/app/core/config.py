from typing import List

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
    CKAN_IPC_RESOURCE_URL: str = (
        "https://catalogodatos.gub.uy/dataset/126e6604-eb45-4376-90fd-a6c5f77d9a1f/"
        "resource/50995d42-9475-47df-9d92-d302180efd8c/download/10449_indice_de_precios_al_consumo_-ipc-.csv"
    )
    BCU_COTIZACIONES_URL: str = "https://www.bcu.gub.uy/Estadisticas-e-Indicadores/Paginas/Cotizaciones.aspx"
    BCU_DOLAR_ROW_FILTER: str = "DLS. USA"

    # OPP - Gasto público (fuente primaria)
    # CSV historico credito y ejecucion presupuestal por UE (1999-2010)
    # Dataset: opp-historico-de-credito-y-ejecucion-presupuestal-por-ue
    CKAN_MEF_EJECUCION_URL: str = (
        "http://transparenciapresupuestaria.opp.gub.uy/sites/default/files/"
        "datos-abiertos/credito_y_ejecucion_1999_2010.csv"
    )
    # OPP CKAN - dataset ID para PresupuestoAbiertoETL (descubrimiento dinamico)
    OPP_BALANCE_EJECUCION_CKAN_DATASET_ID: str = "opp-historico-de-credito-y-ejecucion-presupuestal-por-ue"

    # Scheduler
    ETL_SCHEDULE_HOUR: int = 2
    ETL_SCHEDULE_MINUTE: int = 0
    ETL_UTILITIES_DAY_OF_WEEK: str = "mon"

    # Rate limiting
    RATE_LIMIT_GENERAL: int = 60  # requests/min
    RATE_LIMIT_ETL: int = 5  # requests/min para /api/v1/etl/*

    # ETL admin API key (set in .env for production, empty = no protection in dev)
    ETL_API_KEY: str = ""

    # Sentry
    SENTRY_DSN: str = ""

    # Alerting
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_EMAIL_TO: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_USE_TLS: bool = True

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from comma-separated string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [url.strip() for url in self.CORS_ORIGINS.split(",") if url.strip()]
        return self.CORS_ORIGINS


settings = Settings()
