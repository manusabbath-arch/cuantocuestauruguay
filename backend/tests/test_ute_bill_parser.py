"""Tests for UTE bill PDF parser."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.bill_parsers.ute_bill import parse_ute_bill, _detect_ute_bill, _extract_field, PATTERNS


# --- Detection tests ---

class TestDetectUteBill:
    def test_detects_ute_bill_with_standard_text(self):
        text = "UTE - Administración Nacional de Usinas y Transmisiones Eléctricas\nConsumo activo (kWh): 280"
        assert _detect_ute_bill(text) is True

    def test_detects_ute_with_minimal_indicators(self):
        text = "UTE factura consumo eléctrico 200 kWh"
        assert _detect_ute_bill(text) is True

    def test_rejects_non_ute_text(self):
        text = "OSE factura agua consumo metros cúbicos"
        assert _detect_ute_bill(text) is False

    def test_rejects_empty_text(self):
        assert _detect_ute_bill("") is False


# --- Field extraction tests ---

class TestExtractField:
    def test_extracts_consumo_kwh(self):
        text = "Consumo activo (kWh): 280"
        result = _extract_field(text, PATTERNS["consumo_kwh"])
        assert result == "280"

    def test_extracts_consumo_with_decimals(self):
        text = "Consumo: 1.234,5 kWh"
        result = _extract_field(text, PATTERNS["consumo_kwh"])
        assert result is not None
        assert "1.234" in result or "1234" in result

    def test_extracts_tarifa_residencial_simple(self):
        text = "Tarifa aplicada: Residencial Simple\nOtro texto"
        result = _extract_field(text, PATTERNS["tarifa_tipo"])
        assert result is not None
        assert "Residencial" in result

    def test_extracts_tarifa_doble_horario(self):
        text = "Tarifa: Doble Horario categoria"
        result = _extract_field(text, PATTERNS["tarifa_tipo"])
        assert result is not None
        assert "Doble Horario" in result

    def test_extracts_cargo_fijo(self):
        text = "Cargo fijo: $150,00"
        result = _extract_field(text, PATTERNS["cargo_fijo"])
        assert result is not None
        assert "150" in result

    def test_extracts_cargo_variable(self):
        text = "Cargo por energía: $1.960,00"
        result = _extract_field(text, PATTERNS["cargo_variable"])
        assert result is not None

    def test_extracts_total_cargos(self):
        text = "Total cargos del mes: $2.110,00"
        result = _extract_field(text, PATTERNS["total"])
        assert result is not None

    def test_extracts_importe_total(self):
        text = "Importe total: $2.500,00"
        result = _extract_field(text, PATTERNS["total"])
        assert result is not None

    def test_returns_none_for_no_match(self):
        text = "texto sin datos relevantes"
        result = _extract_field(text, PATTERNS["consumo_kwh"])
        assert result is None


# --- Full parser tests ---

class TestParseUteBill:
    @patch("app.bill_parsers.ute_bill.pdfplumber.open")
    def test_parses_complete_ute_bill(self, mock_open):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = (
            "UTE - Administración Nacional de Usinas y Transmisiones Eléctricas\n"
            "Factura de Consumo\n"
            "Tarifa aplicada: Residencial Simple\n"
            "Período de consumo eléctrico: 01/12/2025 a 31/12/2025\n"
            "Consumo activo (kWh): 280\n"
            "Cargo fijo: $150,00\n"
            "Cargo por energía: $1.960,00\n"
            "Total cargos del mes: $2.110,00\n"
        )
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_pdf

        result = parse_ute_bill(b"fake pdf bytes")

        assert result is not None
        assert result.servicio == "UTE"
        assert result.consumo == 280.0
        assert result.consumo_unidad == "kWh"
        assert result.cargo_fijo == 150.0
        assert result.cargo_variable == 1960.0
        assert result.total == 2110.0
        assert "Residencial" in result.tarifa_tipo
        assert result.periodo_desde == date(2025, 12, 1)
        assert result.periodo_hasta == date(2025, 12, 31)

    @patch("app.bill_parsers.ute_bill.pdfplumber.open")
    def test_parses_bill_with_minimal_fields(self, mock_open):
        """Should succeed with just consumo and total (minimum required)."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = (
            "UTE consumo eléctrico\n"
            "Consumo: 200 kWh\n"
            "Importe total: $1.500,00\n"
        )
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_pdf

        result = parse_ute_bill(b"fake pdf bytes")

        assert result is not None
        assert result.consumo == 200.0
        assert result.total == 1500.0
        assert result.tarifa_tipo == "No identificada"

    @patch("app.bill_parsers.ute_bill.pdfplumber.open")
    def test_returns_none_for_non_ute_pdf(self, mock_open):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "OSE factura agua consumo metros cúbicos total $500"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_pdf

        result = parse_ute_bill(b"fake pdf bytes")
        assert result is None

    @patch("app.bill_parsers.ute_bill.pdfplumber.open")
    def test_returns_none_for_empty_pdf(self, mock_open):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_pdf

        result = parse_ute_bill(b"fake pdf bytes")
        assert result is None

    @patch("app.bill_parsers.ute_bill.pdfplumber.open")
    def test_returns_none_when_missing_consumo(self, mock_open):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = (
            "UTE consumo eléctrico\n"
            "Importe total: $1.500,00\n"
            # No consumo kWh field
        )
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_pdf

        result = parse_ute_bill(b"fake pdf bytes")
        assert result is None

    @patch("app.bill_parsers.ute_bill.pdfplumber.open")
    def test_computes_derived_metrics(self, mock_open):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = (
            "UTE Usinas Transmisiones Eléctricas\n"
            "Período: 01/01/2026 a 31/01/2026\n"
            "Consumo activo (kWh): 300\n"
            "Cargo fijo: $200,00\n"
            "Cargo por energía: $2.400,00\n"
            "Total cargos del mes: $2.600,00\n"
        )
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_pdf

        result = parse_ute_bill(b"fake pdf bytes")

        assert result is not None
        # precio_unitario = cargo_variable / consumo = 2400 / 300 = 8.0
        assert result.precio_unitario == 8.0
        # costo_diario = total / dias = 2600 / 30 = 86.67
        assert result.costo_diario == pytest.approx(86.67, abs=0.01)
        assert result.detalles["dias_facturados"] == 30
        assert result.detalles["consumo_diario_kwh"] == 10.0

    @patch("app.bill_parsers.ute_bill.pdfplumber.open")
    def test_handles_pdfplumber_exception(self, mock_open):
        mock_open.side_effect = Exception("Corrupt PDF")
        result = parse_ute_bill(b"corrupt data")
        assert result is None
