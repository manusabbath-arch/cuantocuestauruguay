#!/usr/bin/env python3
"""
CANARY 10% Monitoring Script
Monitoreo automático del rollout gradual de ETL v2

Uso:
    python3 scripts/monitor_canary.py --etl combustibles
    python3 scripts/monitor_canary.py --all
    python3 scripts/monitor_canary.py --compare v1 v2
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import SessionLocal
from app.models.models import Producto, Precio
from sqlalchemy import func, desc, distinct


class CANARYMonitor:
    """Monitor para CANARY 10% rollout"""

    def __init__(self):
        self.db = SessionLocal()
        self.timestamp = datetime.now()
        self.config = self._load_config()

    def _load_config(self):
        """Cargar configuración de feature flags"""
        config_path = Path(__file__).parent.parent / "backend" / "feature_flags_config.json"
        with open(config_path) as f:
            return json.load(f)

    def health_check(self):
        """Verificar salud general del sistema"""
        print("\n🏥 HEALTH CHECK CANARY 10%")
        print("=" * 70)
        
        total_productos = self.db.query(func.count(Producto.id)).scalar()
        total_precios = self.db.query(func.count(Precio.id)).scalar()
        
        print(f"⏱️  Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        print(f"✅ Productos totales: {total_productos}")
        print(f"✅ Precios totales: {total_precios}")
        
        if total_productos > 0:
            print(f"✅ Promedio precios/producto: {total_precios/total_productos:.2f}")
        
        # Categorías
        categorias = self.db.query(
            Producto.categoria,
            func.count(Producto.id).label('count')
        ).group_by(Producto.categoria).all()
        
        print(f"\n📂 Productos por categoría:")
        for cat, count in categorias:
            print(f"   • {cat}: {count}")

    def feature_flags_status(self):
        """Mostrar estado de feature flags"""
        print("\n🚩 FEATURE FLAGS STATUS")
        print("=" * 70)
        
        for etl_name, config in self.config.items():
            phase = config.get('phase', 'unknown').upper()
            enabled = "✅" if config.get('enabled') else "❌"
            v2_pct = config.get('v2_percentage', 0)
            
            print(f"{enabled} {etl_name:20} | Phase: {phase:10} | Traffic: {v2_pct}%")

    def data_source_analysis(self, etl_name='all'):
        """Analizar fuentes de datos (v1 vs v2)"""
        print(f"\n📊 DATA SOURCE ANALYSIS - {etl_name.upper()}")
        print("=" * 70)
        
        v2_count = self.db.query(func.count(Precio.id)).filter(
            Precio.fuente.like('%CKAN%')
        ).scalar()
        
        v1_count = self.db.query(func.count(Precio.id)).filter(
            ~Precio.fuente.like('%CKAN%')
        ).scalar()
        
        total = v2_count + v1_count
        
        if total > 0:
            v2_pct = (v2_count / total) * 100
            v1_pct = (v1_count / total) * 100
            
            print(f"V2 (CKAN):        {v2_count:5} registros ({v2_pct:5.1f}%) {'█' * int(v2_pct/5)}")
            print(f"V1 (Otra fuente): {v1_count:5} registros ({v1_pct:5.1f}%) {'█' * int(v1_pct/5)}")
            print(f"{'─' * 60}")
            print(f"Total:            {total:5} registros (100.0%)")
        else:
            print("⚠️  No hay datos para analizar")

    def latest_updates(self):
        """Mostrar últimas actualizaciones por categoría"""
        print("\n⏰ LATEST UPDATES BY CATEGORY")
        print("=" * 70)
        
        latest = self.db.query(
            Producto.categoria,
            func.max(Precio.fecha).label('ultima_fecha'),
            func.count(Precio.id).label('registros')
        ).join(Precio, Producto.id == Precio.producto_id).group_by(
            Producto.categoria
        ).order_by(desc('ultima_fecha')).all()
        
        for categoria, fecha, count in latest:
            days_ago = (datetime.now().date() - fecha).days if fecha else 'N/A'
            status = "🟢" if days_ago < 7 else "🟡" if days_ago < 30 else "🔴"
            print(f"{status} {categoria:25} | {fecha} ({days_ago} días ago) | {count} reg")

    def top_products(self, limit=10):
        """Top 10 productos con más registros de precios"""
        print(f"\n⭐ TOP {limit} PRODUCTOS POR PRECIOS")
        print("=" * 70)
        
        tops = self.db.query(
            Producto.nombre,
            Producto.categoria,
            func.count(Precio.id).label('precio_count')
        ).outerjoin(Precio).group_by(Producto.nombre, Producto.categoria).order_by(
            desc('precio_count')
        ).limit(limit).all()
        
        for i, (nombre, cat, count) in enumerate(tops, 1):
            print(f"{i:2}. {nombre:40} | {cat:20} | {count:3} precios")

    def data_quality_report(self):
        """Reporte de calidad de datos"""
        print("\n✨ DATA QUALITY REPORT")
        print("=" * 70)
        
        # Verificar integridad referencial
        huerfanos = self.db.query(func.count(Precio.id)).filter(
            Precio.producto_id.notin_(
                self.db.query(Producto.id)
            )
        ).scalar()
        
        print(f"Registros huérfanos: {huerfanos} {'✅' if huerfanos == 0 else '❌'}")
        
        # Verificar duplicados
        duplicados = self.db.query(
            Precio.producto_id,
            Precio.fecha
        ).group_by(Precio.producto_id, Precio.fecha).having(
            func.count() > 1
        ).count()
        
        print(f"Duplicados detectados: {duplicados} {'✅' if duplicados == 0 else '❌'}")
        
        # Precios con valores nulos
        nulos = self.db.query(func.count(Precio.id)).filter(
            Precio.valor.is_(None)
        ).scalar()
        
        print(f"Precios con valor nulo: {nulos} {'✅' if nulos == 0 else '❌'}")
        
        # Productos sin precios
        sin_precios = self.db.query(func.count(Producto.id)).filter(
            Producto.id.notin_(
                self.db.query(distinct(Precio.producto_id))
            )
        ).scalar()
        
        print(f"Productos sin precios: {sin_precios}")

    def close(self):
        """Cerrar conexión a BD"""
        self.db.close()

    def full_report(self):
        """Reporte completo"""
        try:
            self.health_check()
            self.feature_flags_status()
            self.data_source_analysis()
            self.latest_updates()
            self.top_products()
            self.data_quality_report()
            
            print("\n" + "=" * 70)
            print("✅ Monitoreo completado exitosamente")
            print("=" * 70 + "\n")
            
        finally:
            self.close()


def main():
    parser = argparse.ArgumentParser(description='CANARY 10% Monitoring Script')
    parser.add_argument('--full', action='store_true', help='Reporte completo')
    parser.add_argument('--health', action='store_true', help='Solo health check')
    parser.add_argument('--flags', action='store_true', help='Estado de flags')
    parser.add_argument('--sources', action='store_true', help='Análisis de fuentes')
    parser.add_argument('--updates', action='store_true', help='Últimas actualizaciones')
    parser.add_argument('--quality', action='store_true', help='Reporte de calidad')
    parser.add_argument('--top', type=int, default=10, help='Top N productos')
    
    args = parser.parse_args()
    
    monitor = CANARYMonitor()
    
    try:
        if args.full or (not any([args.health, args.flags, args.sources, args.updates, args.quality])):
            monitor.full_report()
        else:
            if args.health:
                monitor.health_check()
            if args.flags:
                monitor.feature_flags_status()
            if args.sources:
                monitor.data_source_analysis()
            if args.updates:
                monitor.latest_updates()
            if args.quality:
                monitor.data_quality_report()
            if args.top:
                monitor.top_products(args.top)
    finally:
        monitor.close()


if __name__ == '__main__':
    main()
