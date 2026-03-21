from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.etl.utilities import UtilitiesETL
from app.models.models import Producto


@pytest.mark.asyncio
async def test_extract_ute_tarifas_prefers_mappable_pdf_rows(db_session: Session, monkeypatch):
    etl = UtilitiesETL(db_session)

    monkeypatch.setattr("app.etl.utilities.discover_and_download_latest_pdf", lambda **_: None)
    monkeypatch.setattr("app.etl.utilities.list_pdfs_in_directory", lambda _: ["ute_tarifas.pdf"])
    monkeypatch.setattr(
        "app.etl.utilities.parse_ute_tariff_pdf",
        lambda _: [
            {"nombre": "Tarifa Residencial BT1", "valor_str": "5,11"},
            {"nombre": "Tarifa Industrial", "valor_str": "8,22"},
        ],
    )

    df = await etl.extract_ute_tarifas()

    assert df is not None
    assert set(df["producto"].tolist()) == {"UTE_RESIDENCIAL_BT1", "UTE_INDUSTRIAL"}
    assert all("URSEA PDF" in fuente for fuente in df["fuente"].tolist())


@pytest.mark.asyncio
async def test_extract_ute_tarifas_falls_back_to_history_when_pdf_has_no_mappable_rows(db_session: Session, monkeypatch):
    etl = UtilitiesETL(db_session)

    monkeypatch.setattr("app.etl.utilities.discover_and_download_latest_pdf", lambda **_: None)
    monkeypatch.setattr("app.etl.utilities.list_pdfs_in_directory", lambda _: ["ute_finanzas.pdf"])
    monkeypatch.setattr(
        "app.etl.utilities.parse_ute_tariff_pdf",
        lambda _: [{"nombre": "Escenario financiero", "valor_str": "1234"}],
    )

    df = await etl.extract_ute_tarifas()

    assert df is not None
    assert set(df["producto"].tolist()) == {
        "UTE_RESIDENCIAL_BT1",
        "UTE_RESIDENCIAL_BT2",
        "UTE_GENERAL_BT3",
        "UTE_INDUSTRIAL",
    }
    assert all(fuente == "URSEA - Historical (verified)" for fuente in df["fuente"].tolist())
    assert all(fecha == date.today() for fecha in df["fecha"].tolist())


@pytest.mark.asyncio
async def test_extract_ute_tarifas_alerts_when_pdf_rows_are_not_mappable(db_session: Session, monkeypatch):
    etl = UtilitiesETL(db_session)
    sent_alerts = []

    monkeypatch.setattr("app.etl.utilities.discover_and_download_latest_pdf", lambda **_: None)
    monkeypatch.setattr("app.etl.utilities.list_pdfs_in_directory", lambda _: ["ute_finanzas.pdf"])
    monkeypatch.setattr(
        "app.etl.utilities.parse_ute_tariff_pdf",
        lambda _: [{"nombre": "Escenario financiero", "valor_str": "1234"}],
    )
    monkeypatch.setattr(
        "app.etl.utilities.alert_manager.send_alert",
        lambda **kwargs: sent_alerts.append(kwargs),
    )

    await etl.extract_ute_tarifas()

    assert len(sent_alerts) == 1
    assert sent_alerts[0]["alert_type"] == "utilities_pdf_unmapped"
    assert sent_alerts[0]["etl_name"] == "Utilities-UTE"


@pytest.mark.asyncio
async def test_extract_ute_tarifas_uses_downloaded_pdf(db_session: Session, monkeypatch):
    etl = UtilitiesETL(db_session)

    monkeypatch.setattr(
        "app.etl.utilities.discover_and_download_latest_pdf",
        lambda **_: "/tmp/ute_latest.pdf",
    )
    monkeypatch.setattr("app.etl.utilities.list_pdfs_in_directory", lambda _: [])
    monkeypatch.setattr(
        "app.etl.utilities.parse_ute_tariff_pdf",
        lambda _: [{"nombre": "Tarifa Residencial BT1", "valor_str": "5,11"}],
    )

    df = await etl.extract_ute_tarifas()

    assert df is not None
    assert df.iloc[0]["producto"] == "UTE_RESIDENCIAL_BT1"


@pytest.mark.asyncio
async def test_extract_ose_tarifas(db_session: Session, monkeypatch):
    etl = UtilitiesETL(db_session)
    # Evita dependencia de red durante tests.
    monkeypatch.setattr("app.etl.utilities.discover_and_download_latest_pdf", lambda **_: None)
    df = await etl.extract_ose_tarifas()

    assert df is not None
    assert len(df) > 0
    assert "producto" in df.columns


@pytest.mark.asyncio
async def test_extract_antel_tarifas(db_session: Session):
    etl = UtilitiesETL(db_session)
    df = await etl.extract_antel_tarifas()

    assert df is not None
    assert len(df) > 0
    assert "producto" in df.columns


@pytest.mark.asyncio
async def test_utilities_etl_run_ute(db_session: Session, monkeypatch):
    etl = UtilitiesETL(db_session)
    monkeypatch.setattr("app.etl.utilities.discover_and_download_latest_pdf", lambda **_: None)
    result = await etl.run_ute()

    assert result["success"] is True
    assert result["service"] == "UTE"
    assert "records_loaded" in result


@pytest.mark.asyncio
async def test_utilities_etl_run_all(db_session: Session, monkeypatch):
    etl = UtilitiesETL(db_session)
    monkeypatch.setattr("app.etl.utilities.discover_and_download_latest_pdf", lambda **_: None)
    result = await etl.run_all()

    assert result["success"] is True
    assert "results" in result
    assert "ute" in result["results"]
    assert "ose" in result["results"]
    assert "antel" in result["results"]


@pytest.mark.asyncio
async def test_ensure_productos(db_session: Session):
    etl = UtilitiesETL(db_session)
    await etl._ensure_productos("electricidad")

    ute_product = db_session.query(Producto).filter(Producto.nombre.like("UTE%")).first()

    assert ute_product is not None
    assert ute_product.categoria in ["electricidad", "agua", "telecomunicaciones"]
