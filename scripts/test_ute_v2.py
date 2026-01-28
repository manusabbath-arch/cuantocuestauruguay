#!/usr/bin/env python3
"""
Test manual del ETL de UTE v2.

Este script ejecuta el ETL de UTE y muestra resultados detallados.

Uso:
    python scripts/test_ute_v2.py
"""

import logging
import sys
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.etl.ute_v2 import UTEETLv2
from app.models.models import Precio, Producto


def setup_logging():
    """Configurar logging detallado."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_separator(title=""):
    """Imprimir separador visual."""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def print_db_stats(db):
    """Imprimir estadísticas de la base de datos."""
    print_separator("ESTADÍSTICAS DE BASE DE DATOS")

    # Contar productos UTE
    ute_productos = db.query(Producto).filter(
        Producto.categoria.like('%Electricidad%')
    ).all()

    print(f"\n📊 Productos de Electricidad en DB: {len(ute_productos)}")
    for producto in ute_productos:
        # Contar precios para este producto
        precio_count = db.query(Precio).filter(
            Precio.producto_id == producto.id
        ).count()
        print(f"  - {producto.nombre}: {precio_count} registros de precios")


def main():
    """Ejecutar test del ETL de UTE."""
    setup_logging()

    print_separator("TEST MANUAL ETL DE UTE v2")
    print("\n🚀 Iniciando test del ETL de UTE...")
    print("📍 Fuente: Datos de ejemplo (histórico verificado)")

    # Crear sesión de DB
    db = SessionLocal()

    try:
        # Estadísticas ANTES
        print_db_stats(db)

        # Ejecutar ETL
        print_separator("EJECUTANDO ETL")
        etl = UTEETLv2(db=db)
        result = etl.run()

        # Mostrar resultados
        print_separator("RESULTADOS DEL ETL")
        print(f"\n✅ Éxito: {result['success']}")
        print(f"📊 Registros procesados: {result['records_processed']}")
        print(f"⏱️  Duración: {result['duration_seconds']:.2f}s")

        if result['errors']:
            print(f"\n❌ Errores ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        else:
            print(f"\n✨ No se encontraron errores")

        # Estadísticas DESPUÉS
        print_db_stats(db)

        # Mostrar algunos precios de ejemplo
        print_separator("PRECIOS DE EJEMPLO")
        ute_productos = db.query(Producto).filter(
            Producto.categoria.like('%Electricidad%')
        ).limit(2).all()

        for producto in ute_productos:
            precios = db.query(Precio).filter(
                Precio.producto_id == producto.id
            ).order_by(Precio.fecha.desc()).limit(3).all()

            print(f"\n📌 {producto.nombre}:")
            for precio in precios:
                print(f"  - {precio.fecha}: ${precio.valor:.2f} ({precio.fuente})")

        # Resumen final
        print_separator("RESUMEN")
        if result['success']:
            print("\n✅ ETL DE UTE COMPLETADO EXITOSAMENTE")
            print(f"✓ {result['records_processed']} registros procesados")
            print(f"✓ Tiempo: {result['duration_seconds']:.2f}s")
            print(f"✓ Throughput: {result['records_processed'] / result['duration_seconds']:.0f} registros/s")
        else:
            print("\n❌ ETL DE UTE FALLÓ")
            print(f"✗ Errores: {len(result['errors'])}")

        print("\n")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
