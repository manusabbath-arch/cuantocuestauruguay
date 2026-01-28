#!/usr/bin/env python
"""
Script simplificado para cargar datos de servicios
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.etl.utilities import UtilitiesETL


async def main():
    """Load utilities data"""
    db = SessionLocal()
    
    try:
        etl = UtilitiesETL(db)
        
        print("=" * 60)
        print("  Cargando Datos de Servicios Públicos")
        print("=" * 60)
        print()
        
        # UTE
        print("🔌 UTE...")
        result_ute = await etl.run_ute()
        if result_ute.get('success'):
            print(f"   ✅ {result_ute.get('records_loaded', 0)} registros")
        else:
            print(f"   ❌ Error: {result_ute.get('message')}")
        print()
        
        # OSE
        print("💧 OSE...")
        result_ose = await etl.run_ose()
        if result_ose.get('success'):
            print(f"   ✅ {result_ose.get('records_loaded', 0)} registros")
        else:
            print(f"   ❌ Error: {result_ose.get('message')}")
        print()
        
        # Antel
        print("📡 Antel...")
        result_antel = await etl.run_antel()
        if result_antel.get('success'):
            print(f"   ✅ {result_antel.get('records_loaded', 0)} registros")
        else:
            print(f"   ❌ Error: {result_antel.get('message')}")
        print()
        
        total = sum([
            result_ute.get('records_loaded', 0),
            result_ose.get('records_loaded', 0),
            result_antel.get('records_loaded', 0)
        ])
        
        print("=" * 60)
        print(f"✅ Total: {total} registros cargados")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
