#!/usr/bin/env python3
"""
Script para ejecutar todos los ETL y poblar la base de datos.

Ejecuta:
1. Combustibles (ANCAP)
2. UTE (Electricidad)
3. OSE (Agua)
4. Antel (Telecomunicaciones)
"""

import sys
import logging
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_all_etls():
    """Ejecutar todos los ETL."""
    from app.core.database import SessionLocal, engine
    from app.etl.combustibles import CombustiblesETL
    from app.etl.utilities import UtilitiesETL
    import asyncio
    
    db = SessionLocal()
    
    results = {
        "combustibles": None,
        "ute": None,
        "ose": None,
        "antel": None
    }
    
    try:
        # Combustibles
        print("\n" + "="*60)
        print("⛽ EJECUTANDO ETL DE COMBUSTIBLES")
        print("="*60)
        
        etl_combustibles = CombustiblesETL(db)
        result = asyncio.run(etl_combustibles.run())
        results["combustibles"] = result
        
        print(f"✅ Combustibles: {result}")
        
        # Utilities (UTE, OSE, Antel)
        etl_utilities = UtilitiesETL(db)
        
        # UTE
        print("\n" + "="*60)
        print("⚡ EJECUTANDO ETL DE UTE (Electricidad)")
        print("="*60)
        
        result = asyncio.run(etl_utilities.run_ute())
        results["ute"] = result
        print(f"✅ UTE: {result}")
        
        # OSE
        print("\n" + "="*60)
        print("💧 EJECUTANDO ETL DE OSE (Agua)")
        print("="*60)
        
        result = asyncio.run(etl_utilities.run_ose())
        results["ose"] = result
        print(f"✅ OSE: {result}")
        
        # Antel
        print("\n" + "="*60)
        print("📱 EJECUTANDO ETL DE ANTEL (Telecomunicaciones)")
        print("="*60)
        
        result = asyncio.run(etl_utilities.run_antel())
        results["antel"] = result
        print(f"✅ Antel: {result}")
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando ETL: {e}", exc_info=True)
        return False
    
    finally:
        db.close()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE EJECUCIÓN")
    print("="*60)
    
    for name, result in results.items():
        if result:
            status = "✅" if result.get("success") else "❌"
            records = result.get("records_processed", 0)
            duration = result.get("duration_seconds", 0)
            print(f"{status} {name.upper()}: {records} registros en {duration:.2f}s")
        else:
            print(f"⏭️ {name.upper()}: No ejecutado")
    
    return True

if __name__ == "__main__":
    print("\n" + "🚀 "*10)
    print("EJECUTANDO TODOS LOS ETL - POBLANDO BASE DE DATOS")
    print("🚀 "*10)
    
    success = run_all_etls()
    
    if success:
        print("\n✅ TODOS LOS ETL EJECUTADOS EXITOSAMENTE\n")
        sys.exit(0)
    else:
        print("\n❌ HUBO ERRORES EN LA EJECUCIÓN\n")
        sys.exit(1)
