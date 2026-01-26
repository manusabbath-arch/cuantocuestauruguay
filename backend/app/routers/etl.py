from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.etl.combustibles import CombustiblesETL
from app.etl.utilities import UtilitiesETL
from app.models.models import Precio, Producto

router = APIRouter(prefix="/api/v1/etl", tags=["etl"])


@router.post("/run")
async def ejecutar_etl(db: Session = Depends(get_db)):
    """Ejecuta el proceso ETL de combustibles manualmente"""
    try:
        etl = CombustiblesETL(db)
        result = await etl.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ETL: {str(e)}")


@router.post("/utilities/run")
async def ejecutar_utilities_etl(service: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Ejecuta el proceso ETL de servicios públicos (UTE, OSE, Antel)

    Args:
        service: Opcional - específica el servicio ('ute', 'ose', 'antel').
                 Si no se especifica, ejecuta todos.
    """
    try:
        etl = UtilitiesETL(db)

        if service:
            service = service.lower()
            if service == "ute":
                result = await etl.run_ute()
            elif service == "ose":
                result = await etl.run_ose()
            elif service == "antel":
                result = await etl.run_antel()
            else:
                raise HTTPException(status_code=400, detail=f"Servicio no válido: {service}. Opciones: ute, ose, antel")
        else:
            result = await etl.run_all()

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando utilities ETL: {str(e)}")


@router.post("/run-all")
async def ejecutar_todo_etl(db: Session = Depends(get_db)):
    """Ejecuta todos los procesos ETL (combustibles + utilities)"""
    try:
        results = {}

        # Ejecutar ETL de combustibles
        combustibles_etl = CombustiblesETL(db)
        results["combustibles"] = await combustibles_etl.run()

        # Ejecutar ETL de utilities
        utilities_etl = UtilitiesETL(db)
        results["utilities"] = await utilities_etl.run_all()

        return {"success": True, "message": "All ETL processes completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ETL completo: {str(e)}")


@router.get("/status")
async def obtener_estado():
    """Obtiene el estado del último proceso ETL"""
    # TODO: Implementar tracking de ejecuciones ETL
    return {
        "message": "ETL status endpoint - to be implemented",
        "last_run": None,
        "available_services": ["combustibles", "ute", "ose", "antel"],
    }


@router.get("/debug/db-stats")
async def obtener_estadisticas_bd(db: Session = Depends(get_db)):
    """Obtiene estadísticas de la base de datos para debugging"""
    try:
        # Contar productos por categoría
        productos_count = db.query(Producto.categoria, func.count(Producto.id)).group_by(Producto.categoria).all()
        
        # Contar precios totales
        precios_total = db.query(func.count(Precio.id)).scalar()
        
        # Contar precios por producto (top 10)
        precios_por_producto = (
            db.query(Producto.nombre, func.count(Precio.id))
            .join(Precio, Producto.id == Precio.producto_id, isouter=True)
            .group_by(Producto.nombre)
            .limit(10)
            .all()
        )
        
        return {
            "productos_por_categoria": dict(productos_count),
            "total_precios": precios_total,
            "precios_por_producto": {nombre: count for nombre, count in precios_por_producto},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@router.post("/debug/test-combustibles")
async def test_combustibles_etl(db: Session = Depends(get_db)):
    """Endpoint de test para debugging del ETL de combustibles"""
    try:
        etl = CombustiblesETL(db)
        
        # Extract
        df = await etl.extract()
        extract_count = len(df) if df is not None else 0
        
        # Transform
        df_transformed = await etl.transform(df) if df is not None else None
        transform_count = len(df_transformed) if df_transformed is not None else 0
        
        # Load
        load_count = await etl.load(df_transformed) if df_transformed is not None else 0
        
        return {
            "extract": extract_count,
            "transform": transform_count,
            "load": load_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")
