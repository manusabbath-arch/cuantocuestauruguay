"""
Sistema de alertas para ETL
Notifica sobre fallos, registros no cargados, etc.
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class ETLAlert:
    """Gestor de alertas para procesos ETL"""

    # Tipos de alerta
    ALERT_ETL_FAILURE = "etl_failure"
    ALERT_NO_RECORDS = "no_records_loaded"
    ALERT_PARTIAL_LOAD = "partial_records_loaded"
    ALERT_LONG_EXECUTION = "long_execution_time"

    def __init__(self, email_enabled: bool = False):
        """
        Inicializar sistema de alertas.

        Args:
            email_enabled: Habilitar envío de alertas por email (requiere SMTP configurado)
        """
        self.email_enabled = email_enabled
        self.alerts_log = []

    def send_alert(
        self,
        alert_type: str,
        etl_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "warning",
    ) -> bool:
        """
        Enviar una alerta.

        Args:
            alert_type: Tipo de alerta (ALERT_*)
            etl_name: Nombre del ETL que generó la alerta
            message: Mensaje descriptivo
            context: Contexto adicional (registros, tiempos, etc.)
            severity: Nivel de severidad (info, warning, error, critical)

        Returns:
            True si la alerta se envió exitosamente
        """
        timestamp = datetime.now().isoformat()
        alert_data = {
            "timestamp": timestamp,
            "type": alert_type,
            "etl": etl_name,
            "message": message,
            "severity": severity,
            "context": context or {},
        }

        # Log
        log_level = getattr(logging, severity.upper(), logging.WARNING)
        logger.log(
            log_level,
            f"[ETL ALERT] {alert_type.upper()} in {etl_name}: {message}",
        )

        # Guardar en historial local
        self.alerts_log.append(alert_data)

        # Enviar por email si está configurado
        if self.email_enabled and severity in ["error", "critical"]:
            self._send_email_alert(alert_data)
            return True

        return True

    def alert_etl_failure(self, etl_name: str, exception: Exception, execution_time: float) -> None:
        """Alerta de fallo en ETL"""
        self.send_alert(
            alert_type=self.ALERT_ETL_FAILURE,
            etl_name=etl_name,
            message=f"ETL failed with exception: {str(exception)}",
            context={
                "exception_type": type(exception).__name__,
                "execution_time_seconds": execution_time,
            },
            severity="error",
        )

    def alert_no_records_loaded(self, etl_name: str, records_extracted: int, execution_time: float) -> None:
        """Alerta cuando se extraen registros pero no se carga ninguno"""
        self.send_alert(
            alert_type=self.ALERT_NO_RECORDS,
            etl_name=etl_name,
            message=f"Extracted {records_extracted} records but loaded 0 to database",
            context={
                "records_extracted": records_extracted,
                "records_loaded": 0,
                "execution_time_seconds": execution_time,
            },
            severity="warning",
        )

    def alert_partial_load(
        self,
        etl_name: str,
        records_extracted: int,
        records_loaded: int,
        execution_time: float,
    ) -> None:
        """Alerta de carga parcial (algunos registros no se cargaron)"""
        skipped = records_extracted - records_loaded
        skipped_pct = (skipped / records_extracted * 100) if records_extracted > 0 else 0

        if skipped_pct > 50:  # Alertar si más del 50% se saltó
            self.send_alert(
                alert_type=self.ALERT_PARTIAL_LOAD,
                etl_name=etl_name,
                message=f"High skip rate: {skipped_pct:.1f}% of records skipped",
                context={
                    "records_extracted": records_extracted,
                    "records_loaded": records_loaded,
                    "records_skipped": skipped,
                    "skip_percentage": skipped_pct,
                    "execution_time_seconds": execution_time,
                },
                severity="warning",
            )

    def alert_long_execution(self, etl_name: str, execution_time: float) -> None:
        """Alerta cuando la ejecución tarda más de lo normal"""
        max_time = 300  # 5 minutos
        if execution_time > max_time:
            self.send_alert(
                alert_type=self.ALERT_LONG_EXECUTION,
                etl_name=etl_name,
                message=f"ETL execution took longer than expected: {execution_time:.1f}s",
                context={"execution_time_seconds": execution_time, "max_expected": max_time},
                severity="info",
            )

    def _send_email_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Enviar alerta por email (requiere SMTP configurado).
        Por ahora es un placeholder para usar en futuro.
        """
        # TODO: Implementar envío de email con SMTP
        # Requiere variables en .env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
        logger.debug(f"Email alert would be sent: {alert_data}")
        return False

    def get_recent_alerts(self, limit: int = 10) -> list:
        """Obtener alertas recientes"""
        return self.alerts_log[-limit:]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Resumen de alertas"""
        if not self.alerts_log:
            return {"total": 0, "by_type": {}, "by_severity": {}}

        by_type = {}
        by_severity = {}

        for alert in self.alerts_log:
            by_type[alert["type"]] = by_type.get(alert["type"], 0) + 1
            by_severity[alert["severity"]] = by_severity.get(alert["severity"], 0) + 1

        return {
            "total": len(self.alerts_log),
            "by_type": by_type,
            "by_severity": by_severity,
            "latest": self.alerts_log[-1] if self.alerts_log else None,
        }


# Instancia global de alertas
alert_manager = ETLAlert(email_enabled=False)
