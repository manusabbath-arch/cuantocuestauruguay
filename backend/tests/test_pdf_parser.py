"""
Unit tests for PDF parser utilities.

Tests parse_ute_tariff_pdf and parse_ose_tariff_pdf functions.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.etl.pdf_parser import parse_ute_tariff_pdf, parse_ose_tariff_pdf, _parse_decimal


class TestParseDecimal:
    """Test _parse_decimal helper function."""

    def test_parse_decimal_with_comma(self):
        """Test parsing decimal with comma (Uruguayan format)."""
        result = _parse_decimal("1.234,56")
        assert result == 1234.56

    def test_parse_decimal_with_dollar_sign(self):
        """Test parsing decimal with $ sign (Uruguayan format)."""
        result = _parse_decimal("$1.234,56")
        assert result == 1234.56

    def test_parse_decimal_with_spaces(self):
        """Test parsing decimal with spaces."""
        result = _parse_decimal("$ 1 234,56 UYU")
        assert result == 1234.56

    def test_parse_decimal_with_none(self):
        """Test parsing None returns None."""
        result = _parse_decimal(None)
        assert result is None

    def test_parse_decimal_with_invalid_string(self):
        """Test parsing invalid string returns None."""
        result = _parse_decimal("invalid")
        assert result is None


class TestParseUTETariffPDF:
    """Test parse_ute_tariff_pdf function."""

    @patch('app.etl.pdf_parser.pdfplumber.open')
    def test_parse_ute_rejects_financial_tables(self, mock_pdf_open):
        """Test that financial tables are rejected."""
        # Mock PDF con tabla financiera
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [[
            ['', 'TOTALES'],
            ['A - INGRESOS CORRIENTES', '1.766.745'],
            ['Venta de Bienes y Servs.', '1.709.467']
        ]]

        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        result = parse_ute_tariff_pdf("test.pdf")

        # Debe retornar None porque rechaza tablas financieras
        assert result is None

    @patch('app.etl.pdf_parser.pdfplumber.open')
    def test_parse_ute_extracts_valid_tariffs(self, mock_pdf_open):
        """Test that valid tariff tables are extracted."""
        # Mock PDF con tabla de tarifas válida
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [[
            ['Tarifa', 'Nivel de tensión kV', 'Precio de energía $/kWh', 'Valle', 'Llano', 'Punta'],
            ['MC1', '0,230 - 0,400', '2,632', '5,794', '13,182'],
            ['MC2', '6,4 - 15 - 22', '2,498', '5,377', '6,880']
        ]]

        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        result = parse_ute_tariff_pdf("test.pdf")

        # Debe extraer 2 registros
        assert result is not None
        assert len(result) == 2
        assert result[0]['nombre'] == 'MC1'
        assert result[0]['valor_str'] == '2,632'

    @patch('app.etl.pdf_parser.pdfplumber.open')
    def test_parse_ute_skips_horarios(self, mock_pdf_open):
        """Test that schedule rows (Lunes, Martes, etc.) are skipped."""
        # Mock PDF con horarios
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [[
            ['Días de la semana', 'Precio de energía $/kWh', 'Fuera de punta', 'Punta'],
            ['Lunes a Viernes', '4,771', '12,034'],
            ['Sábado, Domingo y Feriado', '4,771', '4,771']
        ]]

        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        result = parse_ute_tariff_pdf("test.pdf")

        # Debe retornar None o lista vacía porque rechaza horarios
        assert result is None or len(result) == 0


class TestParseOSETariffPDF:
    """Test parse_ose_tariff_pdf function."""

    @patch('app.etl.pdf_parser.pdfplumber.open')
    def test_parse_ose_extracts_residencial(self, mock_pdf_open):
        """Test extraction of residential tariff."""
        # Mock PDF con tarifa residencial
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = [[
            ['Categoría', 'Precio $/m³'],
            ['Residencial', '45,50'],
            ['Comercial', '60,00']
        ]]

        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        result = parse_ose_tariff_pdf("test.pdf")

        assert result is not None
        assert len(result) == 2
        assert result[0]['producto'] == 'OSE_RESIDENCIAL'
        assert result[0]['valor_str'] == '45,50'
        assert result[1]['producto'] == 'OSE_COMERCIAL'

    @patch('app.etl.pdf_parser.pdfplumber.open')
    def test_parse_ose_fallback_to_text(self, mock_pdf_open):
        """Test fallback to text parsing when tables fail."""
        # Mock PDF sin tablas pero con texto
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_tables.return_value = []
        mock_page.extract_text.return_value = "Tarifa Residencial: 45,50 $/m³\nTarifa Comercial: 60,00 $/m³"

        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf_open.return_value = mock_pdf

        result = parse_ose_tariff_pdf("test.pdf")

        assert result is not None
        assert len(result) == 2
        assert any(r['producto'] == 'OSE_RESIDENCIAL' for r in result)
        assert any(r['producto'] == 'OSE_COMERCIAL' for r in result)
