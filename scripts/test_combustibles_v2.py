#!/usr/bin/env python3
"""
Script de prueba para validar combustibles_v2 manualmente.

Uso:
    python scripts/test_combustibles_v2.py

Propósito:
    - Ejecutar ETL v2 sin depender del scheduler
    - Validar deduplicación
    - Mostrar métricas de carga
    - Detectar errores antes de CANARY activado
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def test_combustibles_v2():
    """
    Ejecutar prueba de combustibles_v2.
    """
    try:
        # Imports
        from app.core.database import SessionLocal
        from app.etl.combustibles_v2 import CombustiblesETLv2
        
        logger.info("=" * 80)
        logger.info("TEST: Combustibles v2 Manual Execution")
        logger.info("=" * 80)
        
        # Create DB session
        logger.info("Connecting to database...")
        db = SessionLocal()
        
        try:
            # Execute ETL
            logger.info("Initializing CombustiblesETLv2...")
            etl = CombustiblesETLv2(db=db)
            
            logger.info("Executing ETL.run()...")
            result = etl.run()
            
            # Print results
            logger.info("=" * 80)
            logger.info("ETL RESULT")
            logger.info("=" * 80)
            logger.info(json.dumps(result, indent=2, default=str))
            logger.info("=" * 80)
            
            # Validate success
            if result.get("success"):
                logger.info("✅ ETL completed successfully")
                
                # Additional validation
                records_processed = result.get("records_processed", 0)
                duration = result.get("duration_seconds", 0)
                
                logger.info(f"📊 Records processed: {records_processed}")
                logger.info(f"⏱️  Duration: {duration:.2f}s")
                
                if records_processed == 0:
                    logger.warning("⚠️  No records processed. Check if data source is available.")
                else:
                    logger.info(f"✅ Successfully processed {records_processed} records")
                
                return 0  # Success
            else:
                logger.error("❌ ETL failed")
                errors = result.get("errors", [])
                if errors:
                    logger.error(f"Errors: {errors}")
                return 1  # Failure
                
        finally:
            db.close()
            logger.info("Database connection closed")
            
    except Exception as e:
        logger.error(f"❌ Exception during test: {e}", exc_info=True)
        return 1

def test_database_connection():
    """
    Test simple database connection.
    """
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        logger.info("Testing database connection...")
        db = SessionLocal()
        
        try:
            result = db.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def main():
    """
    Main test suite.
    """
    logger.info("Starting Combustibles v2 Test Suite")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test 1: Database connection
    if not test_database_connection():
        logger.error("❌ Database test failed. Cannot continue.")
        return 1
    
    # Test 2: Combustibles v2 ETL
    exit_code = test_combustibles_v2()
    
    logger.info("=" * 80)
    logger.info("Test suite completed")
    logger.info("=" * 80)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

