import pytest
from sqlalchemy.orm import Session
from app.etl.utilities import UtilitiesETL
from app.models.models import Producto, Precio
from datetime import date


@pytest.mark.asyncio
async def test_extract_ute_tarifas(db_session: Session):
    """Test extraction of UTE tariffs"""
    etl = UtilitiesETL(db_session)
    df = await etl.extract_ute_tarifas()
    
    assert df is not None
    assert len(df) > 0
    assert 'producto' in df.columns
    assert 'fecha' in df.columns
    assert 'valor' in df.columns


@pytest.mark.asyncio
async def test_extract_ose_tarifas(db_session: Session):
    """Test extraction of OSE tariffs"""
    etl = UtilitiesETL(db_session)
    df = await etl.extract_ose_tarifas()
    
    assert df is not None
    assert len(df) > 0
    assert 'producto' in df.columns


@pytest.mark.asyncio
async def test_extract_antel_tarifas(db_session: Session):
    """Test extraction of Antel tariffs"""
    etl = UtilitiesETL(db_session)
    df = await etl.extract_antel_tarifas()
    
    assert df is not None
    assert len(df) > 0
    assert 'producto' in df.columns


@pytest.mark.asyncio
async def test_utilities_etl_run_ute(db_session: Session):
    """Test full UTE ETL process"""
    etl = UtilitiesETL(db_session)
    result = await etl.run_ute()
    
    assert result['success'] == True
    assert result['service'] == 'UTE'
    assert 'records_loaded' in result


@pytest.mark.asyncio
async def test_utilities_etl_run_all(db_session: Session):
    """Test running all utilities ETL"""
    etl = UtilitiesETL(db_session)
    result = await etl.run_all()
    
    assert result['success'] == True
    assert 'results' in result
    assert 'ute' in result['results']
    assert 'ose' in result['results']
    assert 'antel' in result['results']


@pytest.mark.asyncio
async def test_ensure_productos(db_session: Session):
    """Test that utility products are created"""
    etl = UtilitiesETL(db_session)
    await etl._ensure_productos('electricidad')
    
    # Check that UTE products were created
    ute_product = db_session.query(Producto).filter(
        Producto.nombre.like('UTE%')
    ).first()
    
    assert ute_product is not None
    assert ute_product.categoria in ['electricidad', 'agua', 'telecomunicaciones']
