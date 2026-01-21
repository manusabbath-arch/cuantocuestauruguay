from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.etl.combustibles import CombustiblesETL
from app.etl.utilities import UtilitiesETL

logger = logging.getLogger(__name__)


class ETLScheduler:
    """Scheduler para ejecutar ETL automáticamente"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def run_combustibles_job(self):
        """Job que ejecuta el ETL de combustibles"""
        logger.info("Starting scheduled combustibles ETL job")
        db = SessionLocal()
        try:
            etl = CombustiblesETL(db)
            result = await etl.run()
            logger.info(f"Combustibles ETL job completed: {result}")
        except Exception as e:
            logger.error(f"Error in scheduled combustibles ETL job: {e}")
        finally:
            db.close()
    
    async def run_utilities_job(self):
        """Job que ejecuta el ETL de servicios públicos (UTE, OSE, Antel)"""
        logger.info("Starting scheduled utilities ETL job")
        db = SessionLocal()
        try:
            etl = UtilitiesETL(db)
            result = await etl.run_all()
            logger.info(f"Utilities ETL job completed: {result}")
        except Exception as e:
            logger.error(f"Error in scheduled utilities ETL job: {e}")
        finally:
            db.close()
    
    def start(self):
        """Inicia el scheduler"""
        # Programar ETL de combustibles diario a las 2:00 AM
        self.scheduler.add_job(
            self.run_combustibles_job,
            CronTrigger(
                hour=settings.ETL_SCHEDULE_HOUR,
                minute=settings.ETL_SCHEDULE_MINUTE
            ),
            id='daily_combustibles_etl',
            name='Daily ETL for combustibles',
            replace_existing=True
        )
        
        # Programar ETL de utilities diario a las 2:30 AM
        self.scheduler.add_job(
            self.run_utilities_job,
            CronTrigger(
                hour=settings.ETL_SCHEDULE_HOUR,
                minute=settings.ETL_SCHEDULE_MINUTE + 30
            ),
            id='daily_utilities_etl',
            name='Daily ETL for utilities (UTE, OSE, Antel)',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(
            f"Scheduler started - Combustibles ETL at {settings.ETL_SCHEDULE_HOUR}:{settings.ETL_SCHEDULE_MINUTE:02d}, "
            f"Utilities ETL at {settings.ETL_SCHEDULE_HOUR}:{settings.ETL_SCHEDULE_MINUTE+30:02d}"
        )
    
    def stop(self):
        """Detiene el scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


# Singleton instance
scheduler = ETLScheduler()
