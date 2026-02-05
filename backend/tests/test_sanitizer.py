"""Tests for PII sanitization of bill text."""

from app.bill_parsers.sanitizer import sanitize_text


class TestSanitizeText:
    def test_redacts_ci_uruguaya(self):
        text = "Titular CI: 4.567.890-1 factura"
        result = sanitize_text(text)
        assert "4.567.890-1" not in result
        assert "[CI_REDACTED]" in result

    def test_redacts_ci_short_format(self):
        text = "CI 1.234.567-8 del cliente"
        result = sanitize_text(text)
        assert "1.234.567-8" not in result
        assert "[CI_REDACTED]" in result

    def test_redacts_nombre_titular(self):
        text = "Titular: Juan Carlos Pérez González"
        result = sanitize_text(text)
        assert "Juan Carlos" not in result
        assert "[NOMBRE_REDACTED]" in result

    def test_redacts_direccion(self):
        text = "Dirección: Av. 18 de Julio 1234 Apto 5"
        result = sanitize_text(text)
        assert "18 de Julio" not in result
        assert "[DIRECCION_REDACTED]" in result

    def test_redacts_cuenta(self):
        text = "Número de cuenta: 12345678"
        result = sanitize_text(text)
        assert "12345678" not in result
        assert "[CUENTA_REDACTED]" in result

    def test_redacts_rut(self):
        text = "RUT: 219876543210"
        result = sanitize_text(text)
        assert "219876543210" not in result
        assert "[RUT_REDACTED]" in result

    def test_redacts_email(self):
        text = "Email: juan.perez@gmail.com para notificaciones"
        result = sanitize_text(text)
        assert "juan.perez@gmail.com" not in result
        assert "[EMAIL_REDACTED]" in result

    def test_preserves_numeric_data(self):
        text = "Consumo activo (kWh): 280 Cargo fijo: $150,00 Total: $2.110,00"
        result = sanitize_text(text)
        assert "280" in result
        assert "150,00" in result
        assert "2.110,00" in result

    def test_preserves_tariff_info(self):
        text = "Tarifa aplicada: Residencial Simple Período: 01/12/2025 a 31/12/2025"
        result = sanitize_text(text)
        assert "Residencial Simple" in result
        assert "01/12/2025" in result

    def test_handles_empty_string(self):
        assert sanitize_text("") == ""

    def test_handles_text_without_pii(self):
        text = "UTE factura kWh consumo energia total"
        assert sanitize_text(text) == text
