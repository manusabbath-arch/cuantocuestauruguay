"""
Tests para GastoPublicoETL (P2-A).

Estrategia:
- mock de requests.get para evitar red real
- mock de DB con MagicMock (no SQLite; la interfaz ya está cubierta por otros tests)
- test_transform_* cubren normalización de columnas, tipos numéricos y limpieza
- test_load_* cubren upsert (insert nuevo, update existente)
- test_run_* cubren flujo completo y manejo de errores
"""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from app.etl.gasto_publico import FIELD_CANDIDATES, GastoPublicoETL, _find_col


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CSV_STANDARD = """Ejercicio,Mes,Cod. Inciso,Inciso,Crédito Vigente,Ejecutado
2023,1,02,Ministerio de Economía,1000000,850000
2023,1,04,Ministerio del Interior,500000,450000
2023,2,02,Ministerio de Economía,1100000,900000
"""

CSV_ALTERNATE_COLS = """año,organismo,codigo inciso,devengado,presupuesto vigente
2022,Presidencia,01,780000,1000000
2022,Ministerio Interior,04,430000,500000
"""

CSV_COMMA_NUMBERS = """Ejercicio,Inciso,Crédito Vigente,Ejecutado
2023,02,"1.000.000,50","850.000,00"
"""

CSV_MISSING_REQUIRED = """Ejercicio,Mes
2023,1
"""


def _make_etl(csv_text: str = CSV_STANDARD, db=None) -> GastoPublicoETL:
    """Devuelve un GastoPublicoETL con la configuración mínima para tests."""
    mock_db = db or MagicMock()
    etl = GastoPublicoETL(mock_db)
    etl.url = "http://test.ckan/resource.csv"
    return etl


def _mock_response(csv_text: str):
    mock = MagicMock()
    mock.text = csv_text
    mock.content = csv_text.encode("utf-8")
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# _find_col
# ---------------------------------------------------------------------------


class TestFindCol:
    def test_exact_match(self):
        df = pd.DataFrame(columns=["Ejercicio", "Mes", "Ejecutado"])
        assert _find_col(df, ["ejercicio"]) == "Ejercicio"

    def test_case_insensitive(self):
        df = pd.DataFrame(columns=["CRÉDITO VIGENTE", "Ejecutado"])
        assert _find_col(df, ["crédito vigente"]) == "CRÉDITO VIGENTE"

    def test_first_candidate_wins(self):
        df = pd.DataFrame(columns=["año", "ejercicio"])
        result = _find_col(df, ["ejercicio", "año"])
        assert result == "ejercicio"

    def test_returns_none_when_no_match(self):
        df = pd.DataFrame(columns=["foo", "bar"])
        assert _find_col(df, ["inciso", "organismo"]) is None


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------


class TestExtract:
    @pytest.mark.anyio
    async def test_extract_returns_dataframe(self):
        etl = _make_etl()
        with patch("requests.get", return_value=_mock_response(CSV_STANDARD)):
            df = await etl.extract()
        assert df is not None
        assert len(df) == 3

    @pytest.mark.anyio
    async def test_extract_returns_none_on_http_error(self):
        etl = _make_etl()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("HTTP 500")
        with patch("requests.get", return_value=mock_resp):
            df = await etl.extract()
        assert df is None

    @pytest.mark.anyio
    async def test_extract_returns_none_on_network_error(self):
        etl = _make_etl()
        with patch("requests.get", side_effect=ConnectionError("timeout")):
            df = await etl.extract()
        assert df is None


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


class TestTransform:
    @pytest.mark.anyio
    async def test_transform_standard_csv(self):
        etl = _make_etl()
        raw = pd.read_csv(io.StringIO(CSV_STANDARD), dtype=str)
        result = await etl.transform(raw)
        assert result is not None
        assert len(result) == 3
        assert set(result.columns) >= {"anio", "mes", "inciso", "nombre_organismo", "credito_vigente", "ejecutado"}

    @pytest.mark.anyio
    async def test_transform_alternate_column_names(self):
        etl = _make_etl()
        raw = pd.read_csv(io.StringIO(CSV_ALTERNATE_COLS), dtype=str)
        result = await etl.transform(raw)
        assert result is not None
        assert len(result) == 2

    @pytest.mark.anyio
    async def test_transform_comma_number_format(self):
        etl = _make_etl()
        raw = pd.read_csv(io.StringIO(CSV_COMMA_NUMBERS), dtype=str)
        result = await etl.transform(raw)
        assert result is not None
        assert len(result) == 1
        row = result.iloc[0]
        assert abs(float(row["credito_vigente"]) - 1_000_000.50) < 0.01
        assert abs(float(row["ejecutado"]) - 850_000.00) < 0.01

    @pytest.mark.anyio
    async def test_transform_drops_rows_with_negative_values(self):
        csv = "Ejercicio,Inciso,Crédito Vigente,Ejecutado\n2023,02,-100,500\n2023,03,1000,600\n"
        etl = _make_etl()
        raw = pd.read_csv(io.StringIO(csv), dtype=str)
        result = await etl.transform(raw)
        assert result is not None
        assert len(result) == 1  # solo la fila con credito >= 0

    @pytest.mark.anyio
    async def test_transform_returns_none_on_missing_required_columns(self):
        etl = _make_etl()
        raw = pd.read_csv(io.StringIO(CSV_MISSING_REQUIRED), dtype=str)
        result = await etl.transform(raw)
        assert result is None

    @pytest.mark.anyio
    async def test_transform_returns_none_on_none_input(self):
        etl = _make_etl()
        assert await etl.transform(None) is None

    @pytest.mark.anyio
    async def test_transform_inciso_zero_padded(self):
        csv = "Ejercicio,Inciso,Cod. Inciso,Crédito Vigente,Ejecutado\n2023,Presidencia,1,100000,80000\n"
        etl = _make_etl()
        raw = pd.read_csv(io.StringIO(csv), dtype=str)
        result = await etl.transform(raw)
        assert result is not None
        assert result.iloc[0]["inciso"] == "01"

    @pytest.mark.anyio
    async def test_transform_mes_optional(self):
        """CSV sin columna mes debe producir filas con mes=None."""
        csv = "Ejercicio,Cod. Inciso,Inciso,Crédito Vigente,Ejecutado\n2023,05,ANTEL,200000,150000\n"
        etl = _make_etl()
        raw = pd.read_csv(io.StringIO(csv), dtype=str)
        result = await etl.transform(raw)
        assert result is not None
        assert result.iloc[0]["mes"] is None


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


class TestLoad:
    @pytest.mark.anyio
    async def test_load_inserts_new_record(self):
        etl = _make_etl()
        # Simular que no existe en DB
        etl.db.query.return_value.filter.return_value.first.return_value = None

        df = pd.DataFrame(
            [
                {
                    "anio": 2023,
                    "mes": 1,
                    "inciso": "02",
                    "nombre_organismo": "MEF",
                    "credito_vigente": 1000000.0,
                    "ejecutado": 850000.0,
                    "fuente": "test",
                }
            ]
        )

        count = await etl.load(df)
        assert count == 1
        etl.db.add.assert_called_once()
        etl.db.commit.assert_called_once()

    @pytest.mark.anyio
    async def test_load_updates_existing_record(self):
        etl = _make_etl()
        existing = MagicMock()
        etl.db.query.return_value.filter.return_value.first.return_value = existing

        df = pd.DataFrame(
            [
                {
                    "anio": 2023,
                    "mes": 1,
                    "inciso": "02",
                    "nombre_organismo": "MEF actualizado",
                    "credito_vigente": 1100000.0,
                    "ejecutado": 900000.0,
                    "fuente": "test",
                }
            ]
        )

        count = await etl.load(df)
        assert count == 0  # no inserciones nuevas, solo update
        assert existing.credito_vigente == 1100000.0
        assert existing.ejecutado == 900000.0
        etl.db.add.assert_not_called()

    @pytest.mark.anyio
    async def test_load_returns_zero_for_empty_df(self):
        etl = _make_etl()
        count = await etl.load(pd.DataFrame())
        assert count == 0

    @pytest.mark.anyio
    async def test_load_handles_none_mes(self):
        etl = _make_etl()
        etl.db.query.return_value.filter.return_value.first.return_value = None

        df = pd.DataFrame(
            [
                {
                    "anio": 2023,
                    "mes": None,
                    "inciso": "10",
                    "nombre_organismo": "ANTEL",
                    "credito_vigente": 500000.0,
                    "ejecutado": 400000.0,
                    "fuente": "test",
                }
            ]
        )

        count = await etl.load(df)
        assert count == 1


# ---------------------------------------------------------------------------
# Run (flujo completo)
# ---------------------------------------------------------------------------


class TestRun:
    @pytest.mark.anyio
    async def test_run_returns_success(self):
        etl = _make_etl()
        etl.db.query.return_value.filter.return_value.first.return_value = None

        with patch("requests.get", return_value=_mock_response(CSV_STANDARD)):
            result = await etl.run()

        assert result["success"] is True
        assert result["records_extracted"] == 3
        assert result["records_loaded"] == 3

    @pytest.mark.anyio
    async def test_run_returns_failure_on_extract_error(self):
        etl = _make_etl()
        with patch("requests.get", side_effect=Exception("connection refused")):
            result = await etl.run()

        assert result["success"] is False
        assert "No data" in result["message"]

    @pytest.mark.anyio
    async def test_run_returns_failure_when_transform_fails(self):
        etl = _make_etl()
        with patch("requests.get", return_value=_mock_response(CSV_MISSING_REQUIRED)):
            result = await etl.run()

        assert result["success"] is False
        assert "transform" in result["message"].lower() or "column" in result["message"].lower()

    @pytest.mark.anyio
    async def test_run_result_has_timestamp(self):
        etl = _make_etl()
        etl.db.query.return_value.filter.return_value.first.return_value = None

        with patch("requests.get", return_value=_mock_response(CSV_STANDARD)):
            result = await etl.run()

        assert "timestamp" in result
