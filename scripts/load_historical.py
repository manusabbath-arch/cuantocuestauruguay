#!/usr/bin/env python
"""
Script para cargar datos históricos de servicios directamente
"""
import sys
from pathlib import Path
from datetime import date

# Add backend to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.models.models import Producto, Precio
from app.etl.utilities import TARIFF_HISTORY


def load_historical_data():
    """Load historical tariff data directly"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("  Cargando Datos Históricos de Servicios")
        print("=" * 60)
        print()
        
        today = date.today()
        total_loaded = 0
        
        # Product mapping
        product_mapping = {
            # UTE
            "UTE_RESIDENCIAL_BT1": ("UTE Tarifa Residencial BT1", "electricidad", "$/kWh"),
            "UTE_RESIDENCIAL_BT2": ("UTE Tarifa Residencial BT2", "electricidad", "$/kWh"),
            "UTE_GENERAL_BT3": ("UTE Tarifa General BT3", "electricidad", "$/kWh"),
            "UTE_INDUSTRIAL": ("UTE Tarifa Industrial", "electricidad", "$/kWh"),
            # OSE
            "OSE_RESIDENCIAL": ("OSE Tarifa Residencial", "agua", "$/m³"),
            "OSE_COMERCIAL": ("OSE Tarifa Comercial", "agua", "$/m³"),
            # Antel
            "ANTEL_FIBRA_100": ("Antel Fibra 100 Mbps", "telecomunicaciones", "$/mes"),
            "ANTEL_FIBRA_200": ("Antel Fibra 200 Mbps", "telecomunicaciones", "$/mes"),
            "ANTEL_FIBRA_500": ("Antel Fibra 500 Mbps", "telecomunicaciones", "$/mes"),
        }
        
        # Load data for each product
        for product_key, (nombre, categoria, unidad) in product_mapping.items():
            # Ensure product exists
            producto = db.query(Producto).filter_by(nombre=nombre).first()
            if not producto:
                producto = Producto(
                    nombre=nombre,
                    categoria=categoria,
                    unidad=unidad,
                    activo=True
                )
                db.add(producto)
                db.flush()
                print(f"✅ Creado producto: {nombre}")
            
            # Get latest tariff from history
            if product_key in TARIFF_HISTORY:
                history = TARIFF_HISTORY[product_key]
                latest = history[-1]
                
                # Check if price already exists
                existing = db.query(Precio).filter_by(
                    producto_id=producto.id,
                    fecha=today
                ).first()
                
                if not existing:
                    precio = Precio(
                        producto_id=producto.id,
                        valor=latest["valor"],
                        fecha=today,
                        fuente="Histórico URSEA (Verificado)"
                    )
                    db.add(precio)
                    total_loaded += 1
        
        db.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Total: {total_loaded} registros cargados")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_historical_data()
