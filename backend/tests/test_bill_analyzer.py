"""Tests for the bill analysis engine."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.bill_parsers.base import BillData
from app.core.database import Base
from app.models.models import Precio, Producto
from app.services.bill_analyzer import BillAnalyzer, UMBRAL_DOBLE_HORARIO_KWH


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed with UTE tariff data
    producto = Producto(
        nombre="UTE Residencial BT1",
        categoria="Servicios Públicos - Electricidad",
        unidad="$/kWh",
        activo=True,
    )
    session.add(producto)
    session.flush()

    precio = Precio(
        producto_id=producto.id,
        fecha=date(2026, 1, 1),
        valor=8.40,
        fuente="Test",
    )
    session.add(precio)
    session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(engine)


def _make_bill(**kwargs) -> BillData:
    """Helper to create a BillData with sensible defaults."""
    defaults = {
        "servicio": "UTE",
        "periodo_desde": date(2026, 1, 1),
        "periodo_hasta": date(2026, 1, 31),
        "consumo": 250.0,
        "consumo_unidad": "kWh",
        "cargo_fijo": 150.0,
        "cargo_variable": 2000.0,
        "total": 2150.0,
        "tarifa_tipo": "Residencial Simple",
        "precio_unitario": 8.0,
        "costo_diario": 71.67,
        "detalles": {"dias_facturados": 30, "consumo_diario_kwh": 8.3},
    }
    defaults.update(kwargs)
    return BillData(**defaults)


class TestBillAnalyzer:
    def test_analyze_returns_bill_analysis(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill()
        result = analyzer.analyze_ute(bill)

        assert result.bill is bill
        assert result.percentil_consumo is not None
        assert isinstance(result.recomendaciones, list)
        assert result.ahorro_potencial >= 0

    def test_comparacion_includes_tarifa_oficial(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill()
        result = analyzer.analyze_ute(bill)

        assert "tu_precio_kwh" in result.comparacion_tarifa_oficial
        assert "tarifas_oficiales" in result.comparacion_tarifa_oficial
        assert "UTE Residencial BT1" in result.comparacion_tarifa_oficial["tarifas_oficiales"]

    def test_percentil_bajo_para_consumo_bajo(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill(consumo=100.0)
        result = analyzer.analyze_ute(bill)
        assert result.percentil_consumo <= 25

    def test_percentil_alto_para_consumo_alto(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill(consumo=500.0)
        result = analyzer.analyze_ute(bill)
        assert result.percentil_consumo >= 75

    def test_recomienda_doble_horario_para_consumo_alto(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill(
            consumo=400.0,
            tarifa_tipo="Residencial Simple",
            total=3200.0,
        )
        result = analyzer.analyze_ute(bill)

        tipos = [r.tipo for r in result.recomendaciones]
        assert "cambio_tarifa" in tipos

        cambio = next(r for r in result.recomendaciones if r.tipo == "cambio_tarifa")
        assert "Doble Horario" in cambio.titulo
        assert cambio.ahorro_estimado is not None
        assert cambio.ahorro_estimado > 0

    def test_no_recomienda_doble_horario_para_consumo_bajo(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill(
            consumo=150.0,
            tarifa_tipo="Residencial Simple",
        )
        result = analyzer.analyze_ute(bill)

        cambios = [r for r in result.recomendaciones if r.tipo == "cambio_tarifa"]
        assert len(cambios) == 0

    def test_recomienda_volver_simple_si_doble_horario_bajo_consumo(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill(
            consumo=100.0,
            tarifa_tipo="Doble Horario",
        )
        result = analyzer.analyze_ute(bill)

        cambios = [r for r in result.recomendaciones if r.tipo == "cambio_tarifa"]
        assert len(cambios) >= 1
        assert any("Simple" in r.descripcion for r in cambios)

    def test_siempre_incluye_costo_diario(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill()
        result = analyzer.analyze_ute(bill)

        informativos = [r for r in result.recomendaciones if r.tipo == "informativo"]
        assert len(informativos) >= 1
        assert any("diario" in r.titulo.lower() for r in informativos)

    def test_ahorro_potencial_es_suma_de_recomendaciones(self, db_session):
        analyzer = BillAnalyzer(db_session)
        bill = _make_bill(consumo=400.0, tarifa_tipo="Residencial Simple", total=3200.0)
        result = analyzer.analyze_ute(bill)

        suma = sum(r.ahorro_estimado or 0 for r in result.recomendaciones)
        assert result.ahorro_potencial == pytest.approx(suma, abs=0.01)

    def test_works_with_empty_db(self):
        """Should work even if no tariff data exists in DB."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        analyzer = BillAnalyzer(session)
        bill = _make_bill()
        result = analyzer.analyze_ute(bill)

        assert result is not None
        assert result.comparacion_tarifa_oficial["tarifas_oficiales"] == {}
        session.close()
        Base.metadata.drop_all(engine)
