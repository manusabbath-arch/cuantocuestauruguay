"""
Unit tests for AntelETLv2.

Tests extract, transform, and load methods.
"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.etl.antel_v2 import AntelETLv2
from app.models.models import Precio, Producto


class TestAntelETLv2Initialization:
    """Test initialization of AntelETLv2."""

    def test_init_with_valid_session(self, db_session):
        """Verify AntelETLv2 initializes correctly."""
        etl = AntelETLv2(db=db_session)

        assert etl.name == "antel_planes"
        assert etl.db_session == db_session

    def test_productos_map_contains_9_plans(self, db_session):
        """Verify PRODUCTOS_MAP contains 9 fiber plans."""
        etl = AntelETLv2(db=db_session)

        assert len(etl.PRODUCTOS_MAP) == 9
        assert 'ANTEL_FIBRA_BASICO' in etl.PRODUCTOS_MAP
        assert 'ANTEL_FIBRA_ULTRA' in etl.PRODUCTOS_MAP

    def test_tariff_history_contains_9_plans(self, db_session):
        """Verify TARIFF_HISTORY contains 9 plans."""
        etl = AntelETLv2(db=db_session)

        assert len(etl.TARIFF_HISTORY) == 9
        assert 'ANTEL_FIBRA_BASICO' in etl.TARIFF_HISTORY


class TestAntelETLv2Extract:
    """Test extract functionality."""

    def test_extract_returns_dataframe(self, db_session):
        """Verify extract() returns a pandas DataFrame."""
        etl = AntelETLv2(db=db_session)

        df = etl.extract()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 9  # 9 planes

    def test_extract_contains_required_columns(self, db_session):
        """Verify extracted DataFrame has required columns."""
        etl = AntelETLv2(db=db_session)

        df = etl.extract()

        assert 'producto' in df.columns
        assert 'fecha' in df.columns
        assert 'valor' in df.columns
        assert 'fuente' in df.columns

    def test_extract_uses_latest_prices(self, db_session):
        """Verify extract() uses latest prices from TARIFF_HISTORY."""
        etl = AntelETLv2(db=db_session)

        df = etl.extract()

        # Fibra Básico debe tener el precio más reciente (último del array)
        fibra_basico = df[df['producto'] == 'ANTEL_FIBRA_BASICO']
        # latest = history[-1] en el código toma el último elemento
        assert fibra_basico['valor'].iloc[0] == 1595.0  # Último elemento del array


class TestAntelETLv2Transform:
    """Test transform functionality."""

    def test_transform_normalizes_column_names(self, db_session, sample_antel_dataframe):
        """Test that column names are normalized to lowercase."""
        etl = AntelETLv2(db=db_session)

        result = etl.transform(sample_antel_dataframe)

        assert all(col == col.lower() for col in result.columns)

    def test_transform_validates_valor_is_numeric(self, db_session):
        """Test that non-numeric valores are removed."""
        df = pd.DataFrame({
            'producto': ['ANTEL_FIBRA_BASICO', 'ANTEL_FIBRA_PLUS'],
            'fecha': [date.today(), date.today()],
            'valor': [1650.0, 'invalid'],
            'fuente': ['Test', 'Test']
        })

        etl = AntelETLv2(db=db_session)
        result = etl.transform(df)

        # Solo el primer registro debe quedar
        assert len(result) == 1
        assert result['producto'].iloc[0] == 'ANTEL_FIBRA_BASICO'

    def test_transform_removes_invalid_productos(self, db_session):
        """Test that invalid product keys are filtered out."""
        df = pd.DataFrame({
            'producto': ['ANTEL_FIBRA_BASICO', 'INVALID_PRODUCT'],
            'fecha': [date.today(), date.today()],
            'valor': [1650.0, 999.0],
            'fuente': ['Test', 'Test']
        })

        etl = AntelETLv2(db=db_session)
        result = etl.transform(df)

        # Solo el producto válido debe quedar
        assert len(result) == 1
        assert result['producto'].iloc[0] == 'ANTEL_FIBRA_BASICO'


class TestAntelETLv2Load:
    """Test load functionality."""

    def test_load_creates_producto_with_correct_fields(self, db_session):
        """Test that load creates Producto with correct category and unit."""
        df = pd.DataFrame({
            'producto': ['ANTEL_FIBRA_BASICO'],
            'valor': [1650.0],
            'fecha': [date.today()],
            'fuente': ['Antel Portal (Verificado)']
        })

        etl = AntelETLv2(db=db_session)
        etl.load(df)

        # Verificar que el producto fue creado con campos correctos
        producto = db_session.query(Producto).filter(
            Producto.nombre == 'Antel Fibra Básico 400/30 Mbps'
        ).first()

        assert producto is not None
        assert producto.categoria == "Servicios Públicos - Telecomunicaciones"
        assert producto.unidad == "$/mes"

    def test_load_inserts_precio_with_correct_value(self, db_session):
        """Test that load inserts Precio with correct value."""
        df = pd.DataFrame({
            'producto': ['ANTEL_FIBRA_BASICO'],
            'valor': [1650.0],
            'fecha': [date.today()],
            'fuente': ['Antel Portal (Verificado)']
        })

        etl = AntelETLv2(db=db_session)
        etl.load(df)

        # Verificar que el precio fue insertado
        precio = db_session.query(Precio).first()
        assert precio is not None
        assert precio.valor == 1650.0
        assert precio.fuente == 'Antel Portal (Verificado)'

    def test_load_deduplicates_existing_precio(self, db_session):
        """Test that load updates existing prices instead of duplicating."""
        # Crear producto y precio inicial
        producto = Producto(
            nombre="Antel Fibra Básico 400/30 Mbps",
            categoria="Servicios Públicos - Telecomunicaciones",
            unidad="$/mes"
        )
        db_session.add(producto)
        db_session.commit()

        precio = Precio(
            producto_id=producto.id,
            valor=1595.0,
            fecha=date.today(),
            fuente="Initial"
        )
        db_session.add(precio)
        db_session.commit()

        # Intentar cargar precio actualizado
        df = pd.DataFrame({
            'producto': ['ANTEL_FIBRA_BASICO'],
            'valor': [1650.0],
            'fecha': [date.today()],
            'fuente': ['Antel Portal (Verificado)']
        })

        etl = AntelETLv2(db=db_session)
        etl.load(df)

        # Debe haber solo 1 precio (actualizado)
        precios = db_session.query(Precio).filter(Precio.producto_id == producto.id).all()
        assert len(precios) == 1
        assert precios[0].valor == 1650.0

    def test_load_handles_multiple_plans(self, db_session, sample_antel_dataframe):
        """Test that load handles multiple plans correctly."""
        etl = AntelETLv2(db=db_session)
        etl.load(sample_antel_dataframe)

        # Deben haberse creado 3 productos
        productos = db_session.query(Producto).all()
        assert len(productos) == 3

        # Deben haberse insertado 3 precios
        precios = db_session.query(Precio).all()
        assert len(precios) == 3
