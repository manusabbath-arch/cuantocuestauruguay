from datetime import date

import pandas as pd
import pytest

from app.etl.indices import IndicesETL
from app.models.models import Precio, Producto


class MockResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}")


@pytest.mark.asyncio
async def test_extract_downloads_ipc_and_bcu_sources(db_session, monkeypatch):
    etl = IndicesETL(db_session)
    ipc_csv = "fecha,ipc\n2026-01-01,112.4\n"
    bcu_html = """
    <table>
        <thead>
            <tr><th>Moneda</th><th>Fecha</th><th>Venta</th><th>Compra</th></tr>
        </thead>
        <tbody>
            <tr><td>DLS. USA CABLE</td><td>20/03/2026</td><td>40,735</td><td>40,735</td></tr>
        </tbody>
    </table>
    """
    responses = [MockResponse(ipc_csv), MockResponse(bcu_html)]

    def mock_get(url, timeout):
        return responses.pop(0)

    monkeypatch.setattr("app.etl.indices.requests.get", mock_get)

    datasets = await etl.extract()

    assert set(datasets.keys()) == {"ipc", "bcu"}
    assert len(datasets["ipc"]) == 1
    assert len(datasets["bcu"]) == 1


@pytest.mark.asyncio
async def test_transform_normalizes_ipc_and_bcu_rows(db_session):
    etl = IndicesETL(db_session)
    datasets = {
        "ipc": pd.DataFrame({"fecha": ["2026-01-01"], "ipc": [112.4]}),
        "bcu": pd.DataFrame(
            {
                "Moneda": ["DLS. USA BILLETE", "DLS. USA CABLE"],
                "Fecha": ["20/03/2026", "20/03/2026"],
                "Venta": [40.9, 40.735],
            }
        ),
    }

    transformed = await etl.transform(datasets)

    assert transformed is not None
    assert transformed.to_dict("records") == [
        {
            "fecha": date(2026, 1, 1),
            "producto_nombre": "IPC",
            "precio": 112.4,
            "fuente": "CKAN - Índice de Precios al Consumo (IPC)",
        },
        {
            "fecha": date(2026, 3, 20),
            "producto_nombre": "Dólar BCU",
            "precio": 40.735,
            "fuente": "BCU - Cotización de monedas",
        },
    ]


@pytest.mark.asyncio
async def test_transform_supports_year_and_month_columns_for_ipc(db_session):
    etl = IndicesETL(db_session)
    datasets = {
        "ipc": pd.DataFrame({"Año": [2026], "Mes": ["enero"], "Valor": [110.2]}),
    }

    transformed = await etl.transform(datasets)

    assert transformed is not None
    assert transformed.iloc[0]["fecha"] == date(2026, 1, 1)
    assert transformed.iloc[0]["producto_nombre"] == "IPC"
    assert transformed.iloc[0]["precio"] == 110.2


@pytest.mark.asyncio
async def test_load_creates_index_products_and_prices(db_session):
    etl = IndicesETL(db_session)
    transformed = pd.DataFrame(
        {
            "fecha": [date(2026, 1, 1), date(2026, 3, 20)],
            "producto_nombre": ["IPC", "Dólar BCU"],
            "precio": [112.4, 40.735],
            "fuente": ["CKAN", "BCU"],
        }
    )

    loaded_count = await etl.load(transformed)

    productos = db_session.query(Producto).order_by(Producto.nombre).all()
    precios = db_session.query(Precio).order_by(Precio.fecha, Precio.producto_id).all()

    assert loaded_count == 2
    assert [(producto.nombre, producto.categoria, producto.unidad) for producto in productos] == [
        ("Dólar BCU", "indice", "UYU"),
        ("IPC", "indice", "indice"),
    ]
    assert len(precios) == 2


@pytest.mark.asyncio
async def test_run_executes_complete_indices_pipeline(db_session, monkeypatch):
    etl = IndicesETL(db_session)
    datasets = {"ipc": pd.DataFrame({"fecha": ["2026-01-01"], "ipc": [112.4]})}
    transformed = pd.DataFrame(
        {
            "fecha": [date(2026, 1, 1)],
            "producto_nombre": ["IPC"],
            "precio": [112.4],
            "fuente": ["CKAN - Índice de Precios al Consumo (IPC)"],
        }
    )

    async def mock_extract():
        return datasets

    async def mock_transform(extracted):
        assert extracted == datasets
        return transformed

    async def mock_load(dataframe):
        assert dataframe.equals(transformed)
        return 1

    monkeypatch.setattr(etl, "extract", mock_extract)
    monkeypatch.setattr(etl, "transform", mock_transform)
    monkeypatch.setattr(etl, "load", mock_load)

    result = await etl.run()

    assert result["success"] is True
    assert result["records_extracted"] == 1
    assert result["records_loaded"] == 1
    assert result["sources"] == ["ipc"]
    assert "timestamp" in result
