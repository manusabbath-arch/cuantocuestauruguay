#!/usr/bin/env python
"""
Script para ejecutar ETL de utilidades (UTE, OSE, Antel)
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
from app.etl.ute_v2 import UTEETLv2
from app.etl.ose_v2 import OSEETLv2
from app.etl.antel_v2 import AntelETLv2


async def main():
    """Run all utilities ETL"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("  Ejecutando ETL de Servicios Públicos")
        print("=" * 60)
        print()
        
        # UTE
        print("🔌 UTE...")
        ute = UTEETLv2(db)
        result_ute = await ute.run()
        print(f"   ✅ {result_ute.get('records_processed', 0)} tarifas cargadas")
        print()
        
        # OSE
        print("💧 OSE...")
        ose = OSEETLv2(db)
        result_ose = await ose.run()
        print(f"   ✅ {result_ose.get('records_processed', 0)} tarifas cargadas")
        print()
        
        # Antel
        print("📡 Antel...")
        antel = AntelETLv2(db)
        result_antel = await antel.run()
        print(f"   ✅ {result_antel.get('records_processed', 0)} planes cargados")
        print()
        
        print("=" * 60)
        print("🎉 ETL completado")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
