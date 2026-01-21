import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.models import Producto, Precio
from datetime import date
from decimal import Decimal

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_producto(db_session):
    producto = Producto(
        nombre="Nafta Premium 97",
        categoria="combustible",
        unidad="litro",
        activo=True
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)
    return producto


@pytest.fixture
def sample_precios(db_session, sample_producto):
    precios = [
        Precio(
            producto_id=sample_producto.id,
            fecha=date(2024, 1, 1),
            valor=Decimal("75.50"),
            fuente="test"
        ),
        Precio(
            producto_id=sample_producto.id,
            fecha=date(2024, 1, 15),
            valor=Decimal("76.20"),
            fuente="test"
        ),
        Precio(
            producto_id=sample_producto.id,
            fecha=date(2024, 2, 1),
            valor=Decimal("77.00"),
            fuente="test"
        )
    ]
    for precio in precios:
        db_session.add(precio)
    db_session.commit()
    return precios


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "PreciosRegulados.uy" in response.json()["message"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_listar_productos(sample_producto):
    response = client.get("/api/v1/productos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Nafta Premium 97"


def test_obtener_producto(sample_producto):
    response = client.get(f"/api/v1/productos/{sample_producto.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Nafta Premium 97"


def test_obtener_producto_no_existe():
    response = client.get("/api/v1/productos/9999")
    assert response.status_code == 404


def test_obtener_precios(sample_producto, sample_precios):
    response = client.get(f"/api/v1/precios/{sample_producto.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_obtener_ultimo_precio(sample_producto, sample_precios):
    response = client.get(f"/api/v1/precios/{sample_producto.id}/ultimo")
    assert response.status_code == 200
    data = response.json()
    assert float(data["valor"]) == 77.00


def test_calcular_variacion(sample_producto, sample_precios):
    response = client.get(f"/api/v1/variacion/{sample_producto.id}?periodo=mes")
    assert response.status_code == 200
    data = response.json()
    assert "variacion_porcentual" in data
    assert "precio_actual" in data


def test_estadisticas(sample_producto, sample_precios):
    response = client.get(f"/api/v1/estadisticas/{sample_producto.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["minimo"] == 75.50
    assert data["maximo"] == 77.00
    assert data["cantidad_registros"] == 3
