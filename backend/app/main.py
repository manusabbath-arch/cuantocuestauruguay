import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.middleware.security import setup_security_middleware
from app.routers import etl_router, precios_router
from app.scheduler import start_scheduler, stop_scheduler

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
    """Health check for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
