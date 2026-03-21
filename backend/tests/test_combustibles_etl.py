from datetime import date

import pandas as pd
import pytest

from app.etl.combustibles import CombustiblesETL
from app.models.models import Precio, Producto


class MockResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}")

    def json(self):
        return self.payload


@pytest.mark.asyncio
async def test_extract_paginates_ckan_results(db_session, monkeypatch):
    etl = CombustiblesETL(db_session)
    first_page_records = [
        {
            "Producto": "Gasolina Premium 97",
            "Precio": "81,89",
            "Año-Mes": "2026-01",
        }
        for _ in range(1000)
    ]
    responses = [
        {
            "success": True,
            "result": {
                "records": first_page_records
            },
        },
        {
            "success": True,
            "result": {
                "records": [
                    {
                        "Producto": "Gasolina Super 95",
                        "Precio": "78,54",
                        "Año-Mes": "2026-01",
                    }
                ]
            },
        },
    ]
    calls = []

    def mock_get(url, params, timeout):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return MockResponse(responses.pop(0))

    monkeypatch.setattr("app.etl.combustibles.requests.get", mock_get)

    df = await etl.extract()

    assert df is not None
    assert len(df) == 1001
    assert df.iloc[0]["Producto"] == "Gasolina Premium 97"
    assert df.iloc[-1]["Producto"] == "Gasolina Super 95"
    assert len(calls) == 2
    assert calls[0]["params"]["offset"] == 0
    assert calls[1]["params"]["offset"] == 1000


@pytest.mark.asyncio
async def test_transform_normalizes_combustibles_dataset(db_session):
    etl = CombustiblesETL(db_session)
    source_df = pd.DataFrame(
        {
            "Año-Mes": ["2026-01", "2026-01"],
            "Producto": ["Gasolina Premium 97", "Supergas"],
            "Precio": ["81,89", "88,75"],
        }
    )

    transformed = await etl.transform(source_df)

    assert transformed is not None
    assert list(transformed.columns) == ["fecha", "producto_nombre", "precio"]
    assert transformed.to_dict("records") == [
        {
            "fecha": date(2026, 1, 1),
            "producto_nombre": "Gasolina Premium 97",
            "precio": 81.89,
        },
        {
            "fecha": date(2026, 1, 1),
            "producto_nombre": "Supergas",
            "precio": 88.75,
        },
    ]


@pytest.mark.asyncio
async def test_transform_returns_none_without_required_columns(db_session):
    etl = CombustiblesETL(db_session)
    invalid_df = pd.DataFrame({"producto": ["Gasolina Premium 97"], "precio": [81.89]})

    transformed = await etl.transform(invalid_df)

    assert transformed is None


@pytest.mark.asyncio
async def test_load_creates_products_and_prices(db_session):
    etl = CombustiblesETL(db_session)
    transformed_df = pd.DataFrame(
        {
            "fecha": [date(2026, 1, 1), date(2026, 1, 1), date(2026, 1, 1)],
            "producto_nombre": ["Gasolina Premium 97", "Gasolina Super 95", "No mapeado"],
            "precio": [81.89, 78.54, 999.0],
        }
    )

    loaded_count = await etl.load(transformed_df)

    productos = db_session.query(Producto).order_by(Producto.nombre).all()
    precios = db_session.query(Precio).order_by(Precio.producto_id).all()

    assert loaded_count == 2
    assert [producto.nombre for producto in productos] == [
        "Gasoil 50-S",
        "Nafta Premium 97",
        "Nafta Súper 95",
        "Supergás",
    ]
    assert len(precios) == 2
    assert str(precios[0].valor) == "81.89"
    assert str(precios[1].valor) == "78.54"


@pytest.mark.asyncio
async def test_load_skips_duplicate_price_rows(db_session):
    etl = CombustiblesETL(db_session)
    transformed_df = pd.DataFrame(
        {
            "fecha": [date(2026, 1, 1)],
            "producto_nombre": ["Gasolina Premium 97"],
            "precio": [81.89],
        }
    )

    first_load = await etl.load(transformed_df)
    second_load = await etl.load(transformed_df)

    total_prices = db_session.query(Precio).count()

    assert first_load == 1
    assert second_load == 0
    assert total_prices == 1


@pytest.mark.asyncio
async def test_run_executes_pipeline_successfully(db_session, monkeypatch):
    etl = CombustiblesETL(db_session)
    extracted_df = pd.DataFrame(
        {
            "Año-Mes": ["2026-01"],
            "Producto": ["Gasolina Premium 97"],
            "Precio": ["81,89"],
        }
    )
    transformed_df = pd.DataFrame(
        {
            "fecha": [date(2026, 1, 1)],
            "producto_nombre": ["Gasolina Premium 97"],
            "precio": [81.89],
        }
    )

    async def mock_extract():
        return extracted_df

    async def mock_transform(dataframe):
        assert dataframe.equals(extracted_df)
        return transformed_df

    async def mock_load(dataframe):
        assert dataframe.equals(transformed_df)
        return 1

    monkeypatch.setattr(etl, "extract", mock_extract)
    monkeypatch.setattr(etl, "transform", mock_transform)
    monkeypatch.setattr(etl, "load", mock_load)

    result = await etl.run()

    assert result["success"] is True
    assert result["records_extracted"] == 1
    assert result["records_loaded"] == 1
    assert "timestamp" in result
