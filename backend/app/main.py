import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.middleware.security import setup_security_middleware
from app.routers import etl_router, precios_router
from app.scheduler import start_scheduler, stop_scheduler

# Configure Sentry for error tracking (if configured)
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,  # Monitoreo de 10% de transacciones
        environment="development" if settings.DEBUG else "production",
        attach_stacktrace=True,
    )

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación"""
    logger.info("Starting application...")

    # Iniciar scheduler para tareas periódicas
    start_scheduler()
    logger.info("Scheduler started successfully")

    yield

    # Detener scheduler al cerrar
    stop_scheduler()
    logger.info("Application shutdown complete")


# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API REST para consulta de precios regulados en Uruguay",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure security middleware (headers, rate limiting)
setup_security_middleware(app)

# Include routers
app.include_router(precios_router)
app.include_router(etl_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PreciosRegulados.uy API", "version": "1.0.0", "status": "running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """
    Health check for monitoring.

    Returns 200 if app is running; use this for uptime monitoring.
    Incluye timestamp UTC para sincronización.
    """
    import datetime

    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "environment": "development" if settings.DEBUG else "production",
        "version": "1.0.0",
    }


@app.get("/metrics")
async def metrics():
    """
    Métricas básicas de la aplicación.

    Útil para monitoreo básico sin Prometheus.
    Expone: uptime, estado de DB, último ETL, etc.
    """
    from datetime import datetime

    # Verificar conexión a DB
    try:
        from sqlalchemy import text

        from app.core.database import SessionLocal

        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "running",
        "database": db_status,
        "debug": settings.DEBUG,
        "cors_origins": settings.get_cors_origins(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
