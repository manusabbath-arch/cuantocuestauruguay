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
from app.etl.macro_contexto import MacroContextoETL
from app.etl.utilities import UtilitiesETL
from app.services.analytics import run_deteccion
from app.services.watchdog import run_watchdog

logger = logging.getLogger(__name__)


class ETLScheduler:
    """Scheduler para ejecutar ETL automáticamente"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    @staticmethod
    def _offset_schedule(offset_minutes: int) -> tuple[int, int]:
        total_minutes = (settings.ETL_SCHEDULE_HOUR * 60) + settings.ETL_SCHEDULE_MINUTE + offset_minutes
        return (total_minutes // 60) % 24, total_minutes % 60

    async def run_watchdog_job(self):
        """Job diario que verifica la salud de todas las fuentes ETL."""
        logger.info("Starting scheduled watchdog job")
        db = SessionLocal()
        try:
            result = run_watchdog(db)
            estado = result.get("estado_general", "ok")
            resumen = result.get("resumen", {})
            logger.info(
                f"Watchdog completed: estado={estado} "
                f"ok={resumen.get('ok')} warn={resumen.get('warn')} error={resumen.get('error')}"
            )
            if estado == "error":
                alert_manager.send_alert(
                    alert_type="watchdog_error",
                    etl_name="Watchdog",
                    message=f"Watchdog detected {resumen.get('error')} source(s) in error state.",
                    context=resumen,
                    severity="error",
                )
            elif estado == "warn":
                alert_manager.send_alert(
                    alert_type="watchdog_warn",
                    etl_name="Watchdog",
                    message=f"Watchdog detected {resumen.get('warn')} source(s) with warnings.",
                    context=resumen,
                    severity="warning",
                )
        except Exception as e:
            logger.error(f"Error in scheduled watchdog job: {e}")
        finally:
            db.close()

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

    async def run_macro_job(self):
        """Job mensual que actualiza los indicadores macroeconómicos de contexto."""
        logger.info("Starting scheduled macro contexto ETL job")
        db = SessionLocal()
        start_time = time.monotonic()
        try:
            etl = MacroContextoETL(db)
            result = await etl.run()
            logger.info(f"Macro contexto ETL job completed: {result}")
            self._process_etl_result("MacroContexto", result, time.monotonic() - start_time)
        except Exception as e:
            logger.error(f"Error in scheduled macro contexto ETL job: {e}")
            alert_manager.alert_etl_failure("MacroContexto", e, time.monotonic() - start_time)
        finally:
            db.close()

    async def run_gasto_job(self):
        """Job mensual que ejecuta el ETL de ejecución presupuestal del MEF
        y luego dispara la detección de anomalías sobre los datos actualizados."""
        logger.info("Starting scheduled gasto público ETL job")
        db = SessionLocal()
        start_time = time.monotonic()
        try:
            etl = GastoPublicoETL(db)
            result = await etl.run()
            logger.info(f"Gasto público ETL job completed: {result}")
            self._process_etl_result("GastoPublico", result, time.monotonic() - start_time)

            if result.get("success"):
                try:
                    detection = run_deteccion(db)
                    logger.info(f"Anomaly detection completed: {detection}")
                except Exception as det_err:
                    logger.error(f"Anomaly detection failed (non-blocking): {det_err}")
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

        # ETL de indicadores macro mensual el dia 2 a las 4:00 AM (despues del gasto)
        self.scheduler.add_job(
            self.run_macro_job,
            CronTrigger(day=2, hour=4, minute=0),
            id="monthly_macro_etl",
            name="Monthly ETL for macro indicators (ISR, PIB sectorial)",
            replace_existing=True,
        )

        # Watchdog diario a las 6:00 AM (luego de todos los ETLs nocturnos)
        self.scheduler.add_job(
            self.run_watchdog_job,
            CronTrigger(hour=6, minute=0),
            id="daily_watchdog",
            name="Daily ETL source health watchdog",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(
            f"Scheduler started - Combustibles ETL at {settings.ETL_SCHEDULE_HOUR}:{settings.ETL_SCHEDULE_MINUTE:02d}, "
            f"Utilities ETL on {settings.ETL_UTILITIES_DAY_OF_WEEK} at {utilities_hour}:{utilities_minute:02d}, "
            f"Indices ETL at {indices_hour}:{indices_minute:02d}, "
            f"Gasto publico ETL monthly day=1 at 03:30, "
            f"Macro ETL monthly day=2 at 04:00, "
            f"Watchdog daily at 06:00"
        )

    def stop(self):
        """Detiene el scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


# Singleton instance
scheduler = ETLScheduler()
