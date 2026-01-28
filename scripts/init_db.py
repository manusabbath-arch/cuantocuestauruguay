#!/usr/bin/env python
"""
Script para inicializar la base de datos (crear tablas)
"""
import sys
from pathlib import Path

# Add backend to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import Base, engine
from app.models.models import Producto, Precio  # Import models to register them

def init_db():
    """Create all database tables"""
    print("🔧 Creando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

if __name__ == "__main__":
    init_db()
