import importlib
from unittest.mock import MagicMock

from app.core.config import settings
from app.etl.alerts import ETLAlert
from app.services.scheduler import ETLScheduler


scheduler_module = importlib.import_module("app.services.scheduler")


def test_send_alert_sends_email_when_smtp_is_configured(monkeypatch):
    smtp_instance = MagicMock()
    smtp_factory = MagicMock()
    smtp_factory.return_value.__enter__.return_value = smtp_instance

    monkeypatch.setattr("app.etl.alerts.smtplib.SMTP", smtp_factory)
    monkeypatch.setattr(settings, "ALERT_EMAIL_TO", "ops@example.com")
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "SMTP_USER", "user@example.com")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "secret")
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "alerts@example.com")
    monkeypatch.setattr(settings, "SMTP_USE_TLS", True)

    alert = ETLAlert(email_enabled=True)

    sent = alert.send_alert(
        alert_type=alert.ALERT_ETL_FAILURE,
        etl_name="Combustibles",
        message="Job failed",
        context={"records_loaded": 0},
        severity="error",
    )

    assert sent is True
    smtp_factory.assert_called_once_with("smtp.example.com", 587, timeout=30)
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with("user@example.com", "secret")
    smtp_instance.sendmail.assert_called_once()


def test_process_etl_result_alerts_when_no_records_are_loaded(monkeypatch):
    scheduler = ETLScheduler()
    no_records_alert = MagicMock()
    partial_load_alert = MagicMock()
    long_execution_alert = MagicMock()
    failure_alert = MagicMock()

    monkeypatch.setattr(scheduler_module.alert_manager, "alert_no_records_loaded", no_records_alert)
    monkeypatch.setattr(scheduler_module.alert_manager, "alert_partial_load", partial_load_alert)
    monkeypatch.setattr(scheduler_module.alert_manager, "alert_long_execution", long_execution_alert)
    monkeypatch.setattr(scheduler_module.alert_manager, "send_alert", failure_alert)

    scheduler._process_etl_result(
        "Combustibles",
        {"success": True, "records_extracted": 10, "records_loaded": 0},
        12.5,
    )

    long_execution_alert.assert_called_once_with("Combustibles", 12.5)
    no_records_alert.assert_called_once_with("Combustibles", 10, 12.5)
    partial_load_alert.assert_not_called()
    failure_alert.assert_not_called()


def test_process_etl_result_alerts_when_etl_finishes_without_success(monkeypatch):
    scheduler = ETLScheduler()
    send_alert = MagicMock()

    monkeypatch.setattr(scheduler_module.alert_manager, "alert_long_execution", MagicMock())
    monkeypatch.setattr(scheduler_module.alert_manager, "send_alert", send_alert)

    scheduler._process_etl_result(
        "Combustibles",
        {"success": False, "message": "Transformation failed"},
        3.4,
    )

    send_alert.assert_called_once()
    kwargs = send_alert.call_args.kwargs
    assert kwargs["etl_name"] == "Combustibles"
    assert kwargs["message"] == "Transformation failed"
    assert kwargs["severity"] == "error"


def test_start_schedules_utilities_with_weekly_day(monkeypatch):
    scheduler = ETLScheduler()
    add_job = MagicMock()

    monkeypatch.setattr(scheduler.scheduler, "add_job", add_job)
    monkeypatch.setattr(scheduler.scheduler, "start", MagicMock())
    monkeypatch.setattr(settings, "ETL_SCHEDULE_HOUR", 2)
    monkeypatch.setattr(settings, "ETL_SCHEDULE_MINUTE", 0)
    monkeypatch.setattr(settings, "ETL_UTILITIES_DAY_OF_WEEK", "sun")

    scheduler.start()

    utilities_calls = [call for call in add_job.call_args_list if call.kwargs.get("id") == "daily_utilities_etl"]
    assert len(utilities_calls) == 1

    utilities_trigger = utilities_calls[0].args[1]
    assert "day_of_week='sun'" in str(utilities_trigger)
