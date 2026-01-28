"""
Pytest fixtures compartidas para todos los tests.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Agregar backend al path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.models.models import Base, Precio, Producto


@pytest.fixture(scope="function")
def db_session():
    """Crear una sesión de BD en memoria para tests."""
    # SQLite en memoria
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_producto(db_session):
    """Crear un producto de ejemplo en la BD."""
    producto = Producto(
        nombre="Test Producto",
        categoria="Test Categoria",
        unidad="$/unidad"
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)
    return producto


@pytest.fixture
def sample_precio(db_session, sample_producto):
    """Crear un precio de ejemplo en la BD."""
    from datetime import date
    precio = Precio(
        producto_id=sample_producto.id,
        valor=100.0,
        fecha=date.today(),
        fuente="Test"
    )
    db_session.add(precio)
    db_session.commit()
    db_session.refresh(precio)
    return precio


@pytest.fixture
def sample_ute_dataframe():
    """DataFrame de ejemplo para tests de UTE."""
    from datetime import date
    return pd.DataFrame({
        'nombre': ['MC1', 'GC1', 'TZ1'],
        'valor_str': ['2,632', '2,544', '3,717'],
        'fecha': [date.today(), date.today(), date.today()],
        'fuente': ['PDF: test.pdf', 'PDF: test.pdf', 'PDF: test.pdf']
    })


@pytest.fixture
def sample_antel_dataframe():
    """DataFrame de ejemplo para tests de Antel."""
    from datetime import date
    return pd.DataFrame({
        'producto': ['ANTEL_FIBRA_BASICO', 'ANTEL_FIBRA_PLUS', 'ANTEL_FIBRA_ULTRA'],
        'fecha': [date.today(), date.today(), date.today()],
        'valor': [1650.0, 2138.0, 4342.0],
        'fuente': ['Antel Portal (Verificado)', 'Antel Portal (Verificado)', 'Antel Portal (Verificado)']
    })
