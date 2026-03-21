import logging
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.database import SessionLocal
from app.etl.alerts import alert_manager
from app.etl.combustibles import CombustiblesETL
from app.etl.gasto_publico import GastoPublicoETL
from app.etl.indices import IndicesETL
from app.etl.utilities import UtilitiesETL

logger = logging.getLogger(__name__)


class ETLScheduler:
    """Scheduler para ejecutar ETL automáticamente"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    @staticmethod
    def _offset_schedule(offset_minutes: int) -> tuple[int, int]:
        total_minutes = (settings.ETL_SCHEDULE_HOUR * 60) + settings.ETL_SCHEDULE_MINUTE + offset_minutes
        return (total_minutes // 60) % 24, total_minutes % 60

    async def run_combustibles_job(self):
        """Job que ejecuta el ETL de combustibles"""
        logger.info("Starting scheduled combustibles ETL job")
        db = SessionLocal()
        start_time = time.monotonic()
        try:
            etl = CombustiblesETL(db)
            result = await etl.run()
            logger.info(f"Combustibles ETL job completed: {result}")
            self._process_etl_result("Combustibles", result, time.monotonic() - start_time)
        except Exception as e:
            logger.error(f"Error in scheduled combustibles ETL job: {e}")
            alert_manager.alert_etl_failure("Combustibles", e, time.monotonic() - start_time)
        finally:
            db.close()

    async def run_utilities_job(self):
        """Job que ejecuta el ETL de servicios públicos (UTE, OSE, Antel)"""
        logger.info("Starting scheduled utilities ETL job")
        db = SessionLocal()
        start_time = time.monotonic()
        try:
            etl = UtilitiesETL(db)
            result = await etl.run_all()
            logger.info(f"Utilities ETL job completed: {result}")
            self._process_utilities_result(result, time.monotonic() - start_time)
        except Exception as e:
            logger.error(f"Error in scheduled utilities ETL job: {e}")
            alert_manager.alert_etl_failure("Utilities", e, time.monotonic() - start_time)
        finally:
            db.close()

    async def run_gasto_job(self):
        """Job mensual que ejecuta el ETL de ejecución presupuestal del MEF"""
        logger.info("Starting scheduled gasto público ETL job")
        db = SessionLocal()
        start_time = time.monotonic()
        try:
            etl = GastoPublicoETL(db)
            result = await etl.run()
            logger.info(f"Gasto público ETL job completed: {result}")
            self._process_etl_result("GastoPublico", result, time.monotonic() - start_time)
        except Exception as e:
            logger.error(f"Error in scheduled gasto público ETL job: {e}")
            alert_manager.alert_etl_failure("GastoPublico", e, time.monotonic() - start_time)
        finally:
            db.close()

    async def run_indices_job(self):
        """Job que ejecuta el ETL de índices económicos."""
        logger.info("Starting scheduled indices ETL job")
        db = SessionLocal()
        start_time = time.monotonic()
        try:
            etl = IndicesETL(db)
            result = await etl.run()
            logger.info(f"Indices ETL job completed: {result}")
            self._process_etl_result("Indices", result, time.monotonic() - start_time)
        except Exception as e:
            logger.error(f"Error in scheduled indices ETL job: {e}")
            alert_manager.alert_etl_failure("Indices", e, time.monotonic() - start_time)
        finally:
            db.close()

    def _process_etl_result(self, etl_name: str, result: dict, execution_time: float):
        """Evalúa el resultado de un ETL y dispara alertas operativas relevantes."""
        alert_manager.alert_long_execution(etl_name, execution_time)

        if not result.get("success"):
            alert_manager.send_alert(
                alert_type=alert_manager.ALERT_ETL_FAILURE,
                etl_name=etl_name,
                message=result.get("message", "ETL finished without success"),
                context=result,
                severity="error",
            )
            return

        records_extracted = result.get("records_extracted")
        records_loaded = result.get("records_loaded")

        if records_extracted is None or records_loaded is None:
            return

        if records_extracted > 0 and records_loaded == 0:
            alert_manager.alert_no_records_loaded(etl_name, records_extracted, execution_time)
        elif records_loaded < records_extracted:
            alert_manager.alert_partial_load(etl_name, records_extracted, records_loaded, execution_time)

    def _process_utilities_result(self, result: dict, execution_time: float):
        """Evalúa el resultado agregado del ETL de utilities por cada servicio."""
        alert_manager.alert_long_execution("Utilities", execution_time)

        if not result.get("success"):
            alert_manager.send_alert(
                alert_type=alert_manager.ALERT_ETL_FAILURE,
                etl_name="Utilities",
                message=result.get("message", "Utilities ETL finished without success"),
                context=result,
                severity="error",
            )
            return

        for service_name, service_result in result.get("results", {}).items():
            normalized_name = service_result.get("service", service_name.upper())
            self._process_etl_result(normalized_name, service_result, execution_time)

    def start(self):
        """Inicia el scheduler"""
        utilities_hour, utilities_minute = self._offset_schedule(30)
        indices_hour, indices_minute = self._offset_schedule(60)

        # Programar ETL de combustibles diario a las 2:00 AM
        self.scheduler.add_job(
            self.run_combustibles_job,
            CronTrigger(hour=settings.ETL_SCHEDULE_HOUR, minute=settings.ETL_SCHEDULE_MINUTE),
            id="daily_combustibles_etl",
            name="Daily ETL for combustibles",
            replace_existing=True,
        )

        # Programar ETL de utilities semanalmente con día configurable
        self.scheduler.add_job(
            self.run_utilities_job,
            CronTrigger(
                day_of_week=settings.ETL_UTILITIES_DAY_OF_WEEK,
                hour=utilities_hour,
                minute=utilities_minute,
            ),
            id="daily_utilities_etl",
            name="Weekly ETL for utilities (UTE, OSE, Antel)",
            replace_existing=True,
        )

        # Programar ETL de índices una hora después del inicio del lote diario
        self.scheduler.add_job(
            self.run_indices_job,
            CronTrigger(hour=indices_hour, minute=indices_minute),
            id="daily_indices_etl",
            name="Daily ETL for economic indices",
            replace_existing=True,
        )

        # Programar ETL de gasto público mensualmente el día 1 a las 3:30 AM
        self.scheduler.add_job(
            self.run_gasto_job,
            CronTrigger(day=1, hour=3, minute=30),
            id="monthly_gasto_etl",
            name="Monthly ETL for gasto público (MEF)",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(
            f"Scheduler started - Combustibles ETL at {settings.ETL_SCHEDULE_HOUR}:{settings.ETL_SCHEDULE_MINUTE:02d}, "
            f"Utilities ETL on {settings.ETL_UTILITIES_DAY_OF_WEEK} at {utilities_hour}:{utilities_minute:02d}, "
            f"Indices ETL at {indices_hour}:{indices_minute:02d}, "
            f"Gasto publico ETL monthly day=1 at 03:30"
        )

    def stop(self):
        """Detiene el scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


# Singleton instance
scheduler = ETLScheduler()
