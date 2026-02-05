"""Integration tests for the /api/v1/facturas/analyze endpoint."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestFacturasEndpoint:
    def test_rejects_non_pdf_file(self):
        response = client.post(
            "/api/v1/facturas/analyze",
            files={"file": ("factura.txt", b"not a pdf", "text/plain")},
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_rejects_empty_file(self):
        response = client.post(
            "/api/v1/facturas/analyze",
            files={"file": ("factura.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400
        assert "vacío" in response.json()["detail"]

    def test_rejects_oversized_file(self):
        big_content = b"x" * (6 * 1024 * 1024)  # 6 MB
        response = client.post(
            "/api/v1/facturas/analyze",
            files={"file": ("factura.pdf", big_content, "application/pdf")},
        )
        assert response.status_code == 400
        assert "5MB" in response.json()["detail"]

    @patch("app.routers.facturas.parse_ute_bill")
    def test_returns_422_when_parsing_fails(self, mock_parse):
        mock_parse.return_value = None
        response = client.post(
            "/api/v1/facturas/analyze",
            files={"file": ("factura.pdf", b"%PDF-1.4 fake content", "application/pdf")},
        )
        assert response.status_code == 422
        assert "No se pudo procesar" in response.json()["detail"]

    @patch("app.routers.facturas.BillAnalyzer")
    @patch("app.routers.facturas.parse_ute_bill")
    def test_returns_analysis_for_valid_bill(self, mock_parse, mock_analyzer_cls):
        from datetime import date
        from app.bill_parsers.base import BillAnalysis, BillData, Recomendacion

        bill = BillData(
            servicio="UTE",
            periodo_desde=date(2026, 1, 1),
            periodo_hasta=date(2026, 1, 31),
            consumo=280.0,
            consumo_unidad="kWh",
            cargo_fijo=150.0,
            cargo_variable=1960.0,
            total=2110.0,
            tarifa_tipo="Residencial Simple",
            precio_unitario=7.0,
            costo_diario=70.33,
            detalles={"dias_facturados": 30, "consumo_diario_kwh": 9.3},
        )
        mock_parse.return_value = bill
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_ute.return_value = BillAnalysis(
            bill=bill,
            comparacion_tarifa_oficial={"tu_precio_kwh": 7.0, "tarifas_oficiales": {}, "tu_tarifa": "Residencial Simple"},
            percentil_consumo=50,
            recomendaciones=[Recomendacion(tipo="informativo", titulo="Test", descripcion="Desc")],
            ahorro_potencial=0,
        )
        mock_analyzer_cls.return_value = mock_analyzer

        response = client.post(
            "/api/v1/facturas/analyze",
            files={"file": ("factura.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["servicio"] == "UTE"
        assert data["consumo"]["valor"] == 280.0
        assert data["consumo"]["unidad"] == "kWh"
        assert data["cargos"]["fijo"] == 150.0
        assert data["cargos"]["variable"] == 1960.0
        assert data["cargos"]["total"] == 2110.0
        assert data["metricas"]["precio_unitario"] == 7.0
        assert data["metricas"]["costo_diario"] == 70.33
        assert "recomendaciones" in data
        assert isinstance(data["recomendaciones"], list)
        assert "ahorro_potencial" in data

    @patch("app.routers.facturas.BillAnalyzer")
    @patch("app.routers.facturas.parse_ute_bill")
    def test_response_does_not_contain_pii(self, mock_parse, mock_analyzer_cls):
        from datetime import date
        from app.bill_parsers.base import BillAnalysis, BillData, Recomendacion

        bill = BillData(
            servicio="UTE",
            periodo_desde=date(2026, 1, 1),
            periodo_hasta=date(2026, 1, 31),
            consumo=200.0,
            consumo_unidad="kWh",
            cargo_fijo=100.0,
            cargo_variable=1400.0,
            total=1500.0,
            tarifa_tipo="Residencial Simple",
            precio_unitario=7.0,
            costo_diario=50.0,
            detalles={"dias_facturados": 30, "consumo_diario_kwh": 6.7},
        )
        mock_parse.return_value = bill
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_ute.return_value = BillAnalysis(
            bill=bill,
            comparacion_tarifa_oficial={"tu_precio_kwh": 7.0, "tarifas_oficiales": {}, "tu_tarifa": "Residencial Simple"},
            percentil_consumo=50,
            recomendaciones=[Recomendacion(tipo="informativo", titulo="Info", descripcion="Desc")],
            ahorro_potencial=0,
        )
        mock_analyzer_cls.return_value = mock_analyzer

        response = client.post(
            "/api/v1/facturas/analyze",
            files={"file": ("factura.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        response_text = response.text

        assert "direccion" not in response_text.lower() and "dirección" not in response_text.lower()
        assert "titular" not in response_text.lower()

    @patch("app.routers.facturas.BillAnalyzer")
    @patch("app.routers.facturas.parse_ute_bill")
    def test_recommendations_have_required_fields(self, mock_parse, mock_analyzer_cls):
        from datetime import date
        from app.bill_parsers.base import BillAnalysis, BillData, Recomendacion

        bill = BillData(
            servicio="UTE",
            periodo_desde=date(2026, 1, 1),
            periodo_hasta=date(2026, 1, 31),
            consumo=400.0,
            consumo_unidad="kWh",
            cargo_fijo=200.0,
            cargo_variable=3200.0,
            total=3400.0,
            tarifa_tipo="Residencial Simple",
            precio_unitario=8.0,
            costo_diario=113.33,
            detalles={"dias_facturados": 30, "consumo_diario_kwh": 13.3},
        )
        mock_parse.return_value = bill
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_ute.return_value = BillAnalysis(
            bill=bill,
            comparacion_tarifa_oficial={"tu_precio_kwh": 8.0, "tarifas_oficiales": {}, "tu_tarifa": "Residencial Simple"},
            percentil_consumo=75,
            recomendaciones=[
                Recomendacion(tipo="cambio_tarifa", titulo="Doble Horario", descripcion="Desc", ahorro_estimado=408.0),
                Recomendacion(tipo="informativo", titulo="Costo", descripcion="Desc"),
            ],
            ahorro_potencial=408.0,
        )
        mock_analyzer_cls.return_value = mock_analyzer

        response = client.post(
            "/api/v1/facturas/analyze",
            files={"file": ("factura.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )
        data = response.json()

        for rec in data["recomendaciones"]:
            assert "tipo" in rec
            assert "titulo" in rec
            assert "descripcion" in rec
            assert "ahorro_estimado" in rec
