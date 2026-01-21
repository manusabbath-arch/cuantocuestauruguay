from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.etl.combustibles import CombustiblesETL

logger = logging.getLogger(__name__)


class ETLScheduler:
    """Scheduler para ejecutar ETL automáticamente"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def run_etl_job(self):
        """Job que ejecuta el ETL"""
        logger.info("Starting scheduled ETL job")
        db = SessionLocal()
        try:
            etl = CombustiblesETL(db)
            result = await etl.run()
            logger.info(f"ETL job completed: {result}")
        except Exception as e:
            logger.error(f"Error in scheduled ETL job: {e}")
        finally:
            db.close()
    
    def start(self):
        """Inicia el scheduler"""
        # Programar ETL diario a las 2:00 AM
        self.scheduler.add_job(
            self.run_etl_job,
            CronTrigger(
                hour=settings.ETL_SCHEDULE_HOUR,
                minute=settings.ETL_SCHEDULE_MINUTE
            ),
            id='daily_etl',
            name='Daily ETL for combustibles',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started - ETL will run daily at {settings.ETL_SCHEDULE_HOUR}:{settings.ETL_SCHEDULE_MINUTE:02d}")
    
    def stop(self):
        """Detiene el scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


# Singleton instance
scheduler = ETLScheduler()
