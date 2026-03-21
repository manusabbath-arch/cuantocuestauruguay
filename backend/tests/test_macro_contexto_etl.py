"""
Tests para MacroContextoETL.

Estrategia:
- mock de requests.get para evitar red real
- mock de DB con MagicMock
- _etl_isr y _etl_pib_industrias se testean con CSVs representativos
- MacroContextoETL.run() cubre el flujo completo
"""

from unittest.mock import MagicMock, patch

import pytest

from app.etl.macro_contexto import MacroContextoETL, _etl_isr, _etl_pib_industrias, _upsert


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

CSV_ISR = "ao,valor\n1996,108.23\n1997,107.22\n2018,137.67\n"

CSV_PIB = (
    '"Tipo de Actividad",ao,valor\n'
    '"INDUSTRIAS MANUFACTURERAS",2005,63125725\n'
    '"ACTIVIDADES PRIMARIAS",2005,38229925\n'
    '"CONSTRUCCION",2005,23542050\n'
    '"OTROS SERVICIOS",2005,100000000\n'
    '"COMERCIO. REPARACIONES. RESTAURANTES Y HOTELES",2005,92019404\n'
    '"SUMINISTRO DE ELECTRICIDAD. GAS Y AGUA",2005,13323287\n'
)

CSV_ISR_BAD_COLS = "year,index_value\n1996,108.23\n"


def _mock_resp(text: str):
    m = MagicMock()
    m.text = text
    m.content = text.encode("utf-8")
    m.status_code = 200
    m.raise_for_status = MagicMock()
    return m


def _make_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db


# ---------------------------------------------------------------------------
# _upsert
# ---------------------------------------------------------------------------


class TestUpsert:
    def test_inserts_new_record(self):
        db = _make_db()
        result = _upsert(db, "isr", "ISR", 2018, 137.67, "indice", "test")
        assert result is True
        db.add.assert_called_once()

    def test_updates_existing_record(self):
        db = MagicMock()
        existing = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = existing
        result = _upsert(db, "isr", "ISR", 2018, 140.0, "indice", "test")
        assert result is False
        assert existing.valor == 140.0
        db.add.assert_not_called()


# ---------------------------------------------------------------------------
# _etl_isr
# ---------------------------------------------------------------------------


class TestEtlIsr:
    def test_returns_success_with_valid_csv(self):
        db = _make_db()
        with patch("requests.get", return_value=_mock_resp(CSV_ISR)):
            result = _etl_isr(db)
        assert result["success"] is True
        assert result["records_loaded"] == 3

    def test_returns_failure_on_network_error(self):
        db = _make_db()
        with patch("requests.get", side_effect=Exception("timeout")):
            result = _etl_isr(db)
        assert result["success"] is False

    def test_returns_failure_on_bad_columns(self):
        db = _make_db()
        with patch("requests.get", return_value=_mock_resp(CSV_ISR_BAD_COLS)):
            result = _etl_isr(db)
        assert result["success"] is False

    def test_skips_non_numeric_values(self):
        csv = "ao,valor\n2010,abc\n2011,120.5\n"
        db = _make_db()
        with patch("requests.get", return_value=_mock_resp(csv)):
            result = _etl_isr(db)
        assert result["success"] is True
        assert result["records_loaded"] == 1

    def test_commits_to_db(self):
        db = _make_db()
        with patch("requests.get", return_value=_mock_resp(CSV_ISR)):
            _etl_isr(db)
        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# _etl_pib_industrias
# ---------------------------------------------------------------------------


class TestEtlPibIndustrias:
    def test_returns_success_with_valid_csv(self):
        db = _make_db()
        with patch("requests.get", return_value=_mock_resp(CSV_PIB)):
            result = _etl_pib_industrias(db)
        assert result["success"] is True
        # 4 sectores: industrial, agropecuario, construccion, servicios (suma 2 categorías)
        assert result["records_loaded"] == 4

    def test_returns_failure_on_network_error(self):
        db = _make_db()
        with patch("requests.get", side_effect=Exception("connection refused")):
            result = _etl_pib_industrias(db)
        assert result["success"] is False

    def test_servicios_sums_two_categories(self):
        """pib_servicios debe sumar OTROS SERVICIOS + COMERCIO para el mismo año."""
        db = _make_db()
        captured = []

        def fake_upsert(db_, codigo, nombre, anio, valor, unidad, fuente):
            captured.append((codigo, anio, valor))
            return True

        with patch("requests.get", return_value=_mock_resp(CSV_PIB)):
            with patch("app.etl.macro_contexto._upsert", side_effect=fake_upsert):
                _etl_pib_industrias(db)

        servicios = [(c, a, v) for c, a, v in captured if c == "pib_servicios"]
        assert len(servicios) == 1
        assert servicios[0][2] == pytest.approx(100_000_000 + 92_019_404)

    def test_commits_to_db(self):
        db = _make_db()
        with patch("requests.get", return_value=_mock_resp(CSV_PIB)):
            _etl_pib_industrias(db)
        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# MacroContextoETL.run()
# ---------------------------------------------------------------------------


class TestMacroContextoETLRun:
    @pytest.mark.anyio
    async def test_run_success(self):
        db = _make_db()
        etl = MacroContextoETL(db)

        def get_side_effect(url, **kwargs):
            if "10458" in url or "mides-indicador" in url and "11139" not in url:
                return _mock_resp(CSV_ISR)
            return _mock_resp(CSV_PIB)

        with patch("requests.get", side_effect=get_side_effect):
            result = await etl.run()

        assert result["success"] is True
        assert result["records_loaded"] >= 0
        assert "detalle" in result
        assert "isr" in result["detalle"]
        assert "pib_industrias" in result["detalle"]

    @pytest.mark.anyio
    async def test_run_partial_failure_still_returns_result(self):
        """Si un ETL parcial falla, run() retorna el resultado con success=False."""
        db = _make_db()
        etl = MacroContextoETL(db)

        with patch("requests.get", side_effect=Exception("red caída")):
            result = await etl.run()

        assert result["success"] is False
        assert "detalle" in result
