"""
Unit tests for UTEETLv2.

Tests extract, transform, and load methods.
"""

import sys
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.etl.ute_v2 import UTEETLv2
from app.models.models import Precio, Producto


class TestUTEETLv2Initialization:
    """Test initialization of UTEETLv2."""

    def test_init_with_valid_session(self, db_session):
        """Verify UTEETLv2 initializes correctly."""
        etl = UTEETLv2(db=db_session)

        assert etl.name == "ute_tarifas"
        assert etl.db_session == db_session

    def test_productos_map_defined(self, db_session):
        """Verify PRODUCTOS_MAP is defined."""
        etl = UTEETLv2(db=db_session)

        assert hasattr(etl, 'PRODUCTOS_MAP')
        assert 'UTE_RESIDENCIAL_BT1' in etl.PRODUCTOS_MAP


class TestUTEETLv2Transform:
    """Test transform functionality."""

    def test_transform_maps_nombre_to_producto(self, db_session, sample_ute_dataframe):
        """Test that 'nombre' column is mapped to 'producto'."""
        etl = UTEETLv2(db=db_session)

        result = etl.transform(sample_ute_dataframe)

        assert 'producto' in result.columns
        assert 'MC1' in result['producto'].values

    def test_transform_parses_valor_str(self, db_session, sample_ute_dataframe):
        """Test that 'valor_str' is parsed to numeric 'valor'."""
        etl = UTEETLv2(db=db_session)

        result = etl.transform(sample_ute_dataframe)

        assert 'valor' in result.columns
        assert result['valor'].dtype in ['float64', 'float32']
        assert result['valor'].iloc[0] == pytest.approx(2.632, abs=0.001)

    def test_transform_converts_comma_to_dot(self, db_session):
        """Test that comma decimals are converted to dot."""
        df = pd.DataFrame({
            'nombre': ['MC1'],
            'valor_str': ['2,632'],
            'fecha': [date.today()],
            'fuente': ['PDF: test.pdf']
        })

        etl = UTEETLv2(db=db_session)
        result = etl.transform(df)

        assert result['valor'].iloc[0] == pytest.approx(2.632)

    def test_transform_removes_invalid_values(self, db_session):
        """Test that invalid/negative values are removed."""
        df = pd.DataFrame({
            'nombre': ['MC1', 'MC2', 'MC3'],
            'valor_str': ['2,632', '-5,0', 'invalid'],
            'fecha': [date.today(), date.today(), date.today()],
            'fuente': ['PDF: test.pdf', 'PDF: test.pdf', 'PDF: test.pdf']
        })

        etl = UTEETLv2(db=db_session)
        result = etl.transform(df)

        # Solo MC1 debe quedar (positivo y válido)
        assert len(result) == 1
        assert result['producto'].iloc[0] == 'MC1'

    def test_transform_raises_on_missing_columns(self, db_session):
        """Test that transform raises error if required columns are missing."""
        df = pd.DataFrame({
            'nombre': ['MC1']
            # Falta valor_str, fecha
        })

        etl = UTEETLv2(db=db_session)

        with pytest.raises(ValueError, match="Missing required columns"):
            etl.transform(df)


class TestUTEETLv2Load:
    """Test load functionality."""

    def test_load_creates_producto_if_not_exists(self, db_session):
        """Test that load creates Producto if it doesn't exist."""
        df = pd.DataFrame({
            'producto': ['MC1'],
            'valor': [2.632],
            'fecha': [date.today()],
            'fuente': ['PDF: test.pdf']
        })

        etl = UTEETLv2(db=db_session)
        etl.load(df)

        # Verificar que el producto fue creado
        producto = db_session.query(Producto).filter(Producto.nombre == 'MC1').first()
        assert producto is not None
        assert producto.categoria == "Servicios Públicos - Electricidad"
        assert producto.unidad == "$/kWh"

    def test_load_inserts_precio(self, db_session):
        """Test that load inserts Precio record."""
        df = pd.DataFrame({
            'producto': ['MC1'],
            'valor': [2.632],
            'fecha': [date.today()],
            'fuente': ['PDF: test.pdf']
        })

        etl = UTEETLv2(db=db_session)
        etl.load(df)

        # Verificar que el precio fue insertado
        precio = db_session.query(Precio).first()
        assert precio is not None
        assert float(precio.valor) == pytest.approx(2.632, abs=0.01)  # Modelo redondea a 2 decimales
        assert precio.fecha == date.today()

    def test_load_deduplicates_existing_precio(self, db_session):
        """Test that load doesn't insert duplicate prices."""
        # Insertar precio inicial
        producto = Producto(nombre="MC1", categoria="Electricidad", unidad="$/kWh")
        db_session.add(producto)
        db_session.commit()

        precio = Precio(producto_id=producto.id, valor=2.5, fecha=date.today(), fuente="Initial")
        db_session.add(precio)
        db_session.commit()

        # Intentar cargar mismo precio con valor diferente
        df = pd.DataFrame({
            'producto': ['MC1'],
            'valor': [2.632],
            'fecha': [date.today()],
            'fuente': ['PDF: test.pdf']
        })

        etl = UTEETLv2(db=db_session)
        etl.load(df)

        # Debe haber solo 1 precio (actualizado)
        precios = db_session.query(Precio).filter(Precio.producto_id == producto.id).all()
        assert len(precios) == 1
        assert float(precios[0].valor) == pytest.approx(2.632, abs=0.01)  # Modelo redondea a 2 decimales
