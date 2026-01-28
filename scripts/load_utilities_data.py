#!/usr/bin/env python
"""
Script para cargar datos de utilidades usando ETL v1 (UtilitiesETL)
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
    """Run all utilities ETL using v1"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("  Cargando Datos de Servicios Públicos (ETL v1)")
        print("=" * 60)
        print()
        
        etl = UtilitiesETL(db)
        
        # Run all utilities
        print("⚡ Ejecutando ETL completo de servicios...")
        result = await etl.run_all()
        
        print()
        print("=" * 60)
        print("✅ Carga completa")
        print("=" * 60)
        print()
        print("📊 Resultados:")
        
        if result.get('success'):
            print(f"   Total: {result.get('total_records_loaded', 0)} registros")
            print()
            if 'results' in result:
                for service, data in result['results'].items():
                    if isinstance(data, dict):
                        status = "✅" if data.get('success') else "❌"
                        records = data.get('records_loaded', 0)
                        print(f"   {status} {service.upper()}: {records} registros")
        else:
            print("   ❌ Error en la carga")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
