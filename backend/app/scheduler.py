"""
Scheduler para ejecutar tareas periódicas de ETL
"""
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.etl.combustibles_v2 import CombustiblesETLv2
from app.etl.utilities import UtilitiesETL

logger = logging.getLogger(__name__)

# Crear scheduler global
scheduler = AsyncIOScheduler()


async def run_etl_job():
    """
    Ejecuta todos los ETLs de forma programada
    """
    logger.info("=" * 80)
    logger.info(f"Starting scheduled ETL job at {datetime.now().isoformat()}")
    logger.info("=" * 80)

    db: Session = SessionLocal()
    
    try:
        # Ejecutar ETL de Combustibles
        logger.info("Running Combustibles ETL...")
        combustibles_etl = CombustiblesETLv2(db)
        # Ejecutar ETL sincrónico en thread para no bloquear loop async
        combustibles_result = await asyncio.to_thread(combustibles_etl.run)
        logger.info(f"Combustibles ETL completed: {combustibles_result}")

        # Ejecutar ETL de Utilities
        logger.info("Running Utilities ETL...")
        utilities_etl = UtilitiesETL(db)
        utilities_result = await utilities_etl.run_all()
        logger.info(f"Utilities ETL completed: {utilities_result}")

        logger.info("=" * 80)
        logger.info("Scheduled ETL job completed successfully")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error in scheduled ETL job: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """
    Inicia el scheduler con tareas configuradas
    """
    # Configurar tarea diaria de ETL
    # Por defecto se ejecuta a las 2:00 AM según settings
    scheduler.add_job(
        run_etl_job,
        trigger=CronTrigger(
            hour=settings.ETL_SCHEDULE_HOUR,
            minute=settings.ETL_SCHEDULE_MINUTE
        ),
        id="etl_daily_job",
        name="Daily ETL Job - Combustibles & Utilities",
        replace_existing=True,
    )

    # También ejecutar al iniciar (para testing/desarrollo)
    # Comentar esta línea en producción si no quieres ejecución inmediata
    if settings.DEBUG:
        scheduler.add_job(
            run_etl_job,
            trigger="date",  # Ejecutar una vez al iniciar
            id="etl_startup_job",
            name="Startup ETL Job",
            replace_existing=True,
        )

    scheduler.start()
    logger.info(f"Scheduler started. ETL will run daily at {settings.ETL_SCHEDULE_HOUR:02d}:{settings.ETL_SCHEDULE_MINUTE:02d}")
    logger.info(f"Next scheduled run: {scheduler.get_job('etl_daily_job').next_run_time}")


def stop_scheduler():
    """
    Detiene el scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
