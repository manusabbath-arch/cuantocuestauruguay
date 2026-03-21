from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.etl.alerts import alert_manager
from app.etl.combustibles import CombustiblesETL
from app.etl.gasto_publico import GastoPublicoETL, PresupuestoAbiertoETL
from app.etl.indices import IndicesETL
from app.etl.utilities import TARIFF_HISTORY, UtilitiesETL
from app.models.models import Precio, Producto
from app.services.watchdog import run_watchdog

router = APIRouter(prefix="/api/v1/etl", tags=["etl"])


async def verify_etl_api_key(x_api_key: Optional[str] = Header(None)):
    """Protect write endpoints with API key when configured."""
    if settings.ETL_API_KEY and x_api_key != settings.ETL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


@router.post("/run", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_etl(db: Session = Depends(get_db)):
    """Ejecuta el proceso ETL de combustibles manualmente."""
    try:
        etl = CombustiblesETL(db)
        result = await etl.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ETL: {str(e)}")


@router.post("/utilities/run", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_utilities_etl(
    service: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Ejecuta el proceso ETL de servicios públicos (UTE, OSE, Antel)."""
    try:
        util = UtilitiesETL(db)

        if service:
            service = service.lower()
            if service not in {"ute", "ose", "antel"}:
                raise HTTPException(
                    status_code=400,
                    detail=f"Servicio no válido: {service}. Opciones: ute, ose, antel",
                )
            if service == "ute":
                result = await util.run_ute()
            elif service == "ose":
                result = await util.run_ose()
            elif service == "antel":
                result = await util.run_antel()
            return result
        else:
            return await util.run_all()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando utilities ETL: {str(e)}")


@router.post("/indices/run", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_indices_etl(db: Session = Depends(get_db)):
    """Ejecuta el proceso ETL de índices económicos."""
    try:
        etl = IndicesETL(db)
        return await etl.run()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando índices ETL: {str(e)}")


@router.post("/gasto/run", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_gasto_etl(db: Session = Depends(get_db)):
    """Ejecuta el proceso ETL de ejecución presupuestal del MEF."""
    try:
        etl = GastoPublicoETL(db)
        return await etl.run()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando gasto público ETL: {str(e)}")


@router.post("/gasto/opp/run", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_presupuesto_abierto_etl(
    anio: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Ejecuta el ETL complementario usando el dataset OPP (Portal Presupuesto Abierto).

    Parametro opcional `anio` para descargar datos de un anio especifico.
    Sin parametro usa el recurso mas reciente disponible en CKAN OPP.
    """
    try:
        etl = PresupuestoAbiertoETL(db)
        return await etl.run(anio=anio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando OPP ETL: {str(e)}")


@router.post("/run-all", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_todo_etl(db: Session = Depends(get_db)):
    """Ejecuta todos los procesos ETL (combustibles + utilities)"""
    try:
        results = {}

        combustibles_etl = CombustiblesETL(db)
        results["combustibles"] = await combustibles_etl.run()

        utilities_etl = UtilitiesETL(db)
        results["utilities"] = await utilities_etl.run_all()

        indices_etl = IndicesETL(db)
        results["indices"] = await indices_etl.run()

        gasto_etl = GastoPublicoETL(db)
        results["gasto_publico"] = await gasto_etl.run()

        return {"success": True, "message": "All ETL processes completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ETL completo: {str(e)}")


@router.get("/status")
async def obtener_estado():
    """Obtiene el estado del scheduler y próximas ejecuciones programadas"""
    from app.services.scheduler import scheduler

    try:
        sched = scheduler.scheduler
        if not sched.running:
            return {"scheduler_running": False, "message": "Scheduler is not running"}

        jobs = sched.get_jobs()
        jobs_info = [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]

        return {
            "scheduler_running": True,
            "jobs": jobs_info,
            "available_services": ["combustibles", "indices", "ute", "ose", "antel", "gasto_publico"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.get("/debug/db-stats")
async def obtener_estadisticas_bd(db: Session = Depends(get_db)):
    """Obtiene estadísticas de la base de datos para debugging"""
    try:
        productos_count = db.query(Producto.categoria, func.count(Producto.id)).group_by(Producto.categoria).all()
        precios_total = db.query(func.count(Precio.id)).scalar()
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


@router.get("/watchdog")
async def obtener_watchdog(db: Session = Depends(get_db)):
    """
    Ejecuta checks de salud sobre todas las fuentes ETL y retorna estado consolidado.
    Checks: silencio (N dias sin datos), rango (valor fuera de historico), tariff_stale.
    """
    try:
        return run_watchdog(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando watchdog: {str(e)}")


@router.get("/alerts")
async def obtener_alertas_etl():
    """Obtiene alertas recientes del sistema de ETL"""
    try:
        summary = alert_manager.get_alert_summary()
        recent = alert_manager.get_recent_alerts(limit=20)
        return {"summary": summary, "recent_alerts": recent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo alertas: {str(e)}")


@router.get("/utilities/history")
async def obtener_historico_tarifas():
    """Obtiene el histórico completo de tarifas de servicios públicos"""
    return {
        "data": TARIFF_HISTORY,
        "ultima_actualizacion": "2026-01-26",
        "fuentes": {
            "UTE": "URSEA - Régimen Tarifario para Distribuidoras",
            "OSE": "URSEA - Régimen Tarifario para Aguas",
            "ANTEL": "Antel Personas - Planes activos",
        },
    }


@router.get("/utilities/variations")
async def obtener_variaciones_tarifas():
    """Calcula y retorna variaciones de tarifas"""
    etl = UtilitiesETL(None)
    variations = {}

    for producto_key in TARIFF_HISTORY.keys():
        var = etl.calculate_variation(producto_key)
        if var:
            variations[producto_key] = var

    return {
        "variations": variations,
        "timestamp": str(__import__("datetime").datetime.now().isoformat()),
    }


@router.get("/utilities/history/{producto_key}")
async def obtener_historico_producto(producto_key: str):
    """Obtiene el histórico de un producto específico"""
    if producto_key not in TARIFF_HISTORY:
        raise HTTPException(status_code=404, detail=f"Producto '{producto_key}' no encontrado en histórico")

    etl = UtilitiesETL(None)
    variation = etl.calculate_variation(producto_key)

    return {
        "producto": producto_key,
        "historia": TARIFF_HISTORY[producto_key],
        "variacion": variation,
    }
