from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.database import get_db
from app.core.feature_flags import RolloutPhase, feature_flags
from app.etl.alerts import alert_manager
from app.etl.antel_v2 import AntelETLv2
from app.etl.combustibles_v2 import CombustiblesETLv2
from app.etl.ose_v2 import OSEETLv2
from app.etl.ute_v2 import UTEETLv2
from app.etl.utilities import TARIFF_HISTORY, UtilitiesETL
from app.models.models import Precio, Producto
from app.scheduler import scheduler
from app.services.shadow_mode import ShadowModeExecutor, shadow_log_repo

router = APIRouter(prefix="/api/v1/etl", tags=["etl"])


async def verify_etl_api_key(x_api_key: Optional[str] = Header(None)):
    """Protect write endpoints with API key when configured."""
    if settings.ETL_API_KEY and x_api_key != settings.ETL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


@router.post("/run", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_etl(shadow_mode: bool = False, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Ejecuta el proceso ETL de combustibles manualmente.

    Si shadow_mode=true, ejecuta v1 y v2 en paralelo.
    Si no, usa feature flags para determinar si usar v1 o v2.
    """
    try:
        flag = feature_flags.get("combustibles")

        if shadow_mode:
            executor = ShadowModeExecutor(db)
            return await executor.run_shadow("combustibles")

        # Determinar versión basada en feature flag
        use_v2 = flag.route_to_v2(user_id) if flag else False

        if use_v2:
            etl = CombustiblesETLv2(db)
            result = await run_in_threadpool(etl.run)
            return {"source": "v2", **result}

        # Fallback a v1 (CombustiblesETLv2 es el único disponible en routers)
        etl = CombustiblesETLv2(db)
        result = await run_in_threadpool(etl.run)
        return {"source": "v1", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ETL: {str(e)}")


@router.post("/utilities/run", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_utilities_etl(
    service: Optional[str] = None,
    shadow_mode: bool = False,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Ejecuta el proceso ETL de servicios públicos (UTE, OSE, Antel).

    Soporta feature flags y shadow mode.

    Args:
        service: Opcional - específica el servicio ('ute', 'ose', 'antel').
                 Si no se especifica, ejecuta todos.
        shadow_mode: Si True, ejecuta v1 y v2 en paralelo.
        user_id: Para feature flag routing (determinístico por user).
    """
    try:
        if service:
            service = service.lower()
            if service not in {"ute", "ose", "antel"}:
                raise HTTPException(status_code=400, detail=f"Servicio no válido: {service}. Opciones: ute, ose, antel")

            if shadow_mode:
                executor = ShadowModeExecutor(db)
                return await executor.run_shadow(service)

            # Feature flag routing
            flag = feature_flags.get(service)
            use_v2 = flag.route_to_v2(user_id) if flag else False

            if use_v2:
                if service == "ute":
                    etl = UTEETLv2(db)
                elif service == "ose":
                    etl = OSEETLv2(db)
                elif service == "antel":
                    etl = AntelETLv2(db)
                result = await etl.run()
                return {"source": "v2", **result}

            # V1 fallback
            util = UtilitiesETL(db)
            if service == "ute":
                result = await util.run_ute()
            elif service == "ose":
                result = await util.run_ose()
            elif service == "antel":
                result = await util.run_antel()
            return {"source": "v1", **result}
        else:
            if shadow_mode:
                executor = ShadowModeExecutor(db)
                result = {
                    "ute": await executor.run_shadow("ute"),
                    "ose": await executor.run_shadow("ose"),
                    "antel": await executor.run_shadow("antel"),
                }
                return result
            else:
                util = UtilitiesETL(db)
                result = await util.run_all()
                return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando utilities ETL: {str(e)}")


@router.post("/run-all", dependencies=[Depends(verify_etl_api_key)])
async def ejecutar_todo_etl(db: Session = Depends(get_db)):
    """Ejecuta todos los procesos ETL (combustibles + utilities)"""
    try:
        results = {}

        # Ejecutar ETL de combustibles
        combustibles_etl = CombustiblesETLv2(db)
        results["combustibles"] = await run_in_threadpool(combustibles_etl.run)

        # Ejecutar ETL de utilities
        utilities_etl = UtilitiesETL(db)
        results["utilities"] = await utilities_etl.run_all()

        return {"success": True, "message": "All ETL processes completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ETL completo: {str(e)}")


@router.get("/status")
async def obtener_estado():
    """Obtiene el estado del scheduler y próximas ejecuciones programadas"""
    try:
        if not scheduler.running:
            return {
                "scheduler_running": False,
                "message": "Scheduler is not running",
            }

        jobs = scheduler.get_jobs()
        jobs_info = []

        for job in jobs:
            jobs_info.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
            )

        return {
            "scheduler_running": True,
            "jobs": jobs_info,
            "available_services": ["combustibles", "ute", "ose", "antel"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


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


@router.get("/alerts")
async def obtener_alertas_etl():
    """Obtiene alertas recientes del sistema de ETL"""
    try:
        summary = alert_manager.get_alert_summary()
        recent = alert_manager.get_recent_alerts(limit=20)

        return {
            "summary": summary,
            "recent_alerts": recent,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo alertas: {str(e)}")


@router.post("/debug/test-combustibles", dependencies=[Depends(verify_etl_api_key)])
async def test_combustibles_etl(db: Session = Depends(get_db)):
    """Endpoint de test para debugging del ETL de combustibles"""
    try:
        etl = CombustiblesETLv2(db)

        # Versión v2 es sincrónica; ejecutar en threadpool para no bloquear
        # Extract
        df = await run_in_threadpool(etl.extract)
        extract_count = len(df) if df is not None else 0

        # Transform
        df_transformed = await run_in_threadpool(etl.transform, df) if df is not None else None
        transform_count = len(df_transformed) if df_transformed is not None else 0

        # Load
        load_result = await run_in_threadpool(etl.load, df_transformed) if df_transformed is not None else None
        load_count = len(df_transformed) if df_transformed is not None else 0

        return {
            "extract": extract_count,
            "transform": transform_count,
            "load": load_count,
            "load_result": load_result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")


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
    """
    Calcula y retorna variaciones de tarifas (porcentaje y valor absoluto)
    Útil para análisis de inflación de servicios
    """
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


@router.get("/shadow/logs")
async def obtener_shadow_logs(limit: int = 50):
    """Devuelve los logs recientes de shadow mode (v1 vs v2)."""
    logs = shadow_log_repo.list()
    sliced = logs[-limit:] if limit and limit > 0 else logs
    return {
        "count": len(logs),
        "returned": len(sliced),
        "logs": [asdict(entry) for entry in sliced],
    }


@router.get("/feature-flags")
async def obtener_feature_flags():
    """Devuelve el estado actual de todos los feature flags."""
    flags = feature_flags.list_all()
    return {
        "flags": {name: flag.dict() for name, flag in flags.items()},
        "description": "Feature flags para control de v1/v2 rollout",
    }


@router.post("/feature-flags/{etl_name}", dependencies=[Depends(verify_etl_api_key)])
async def actualizar_feature_flag(
    etl_name: str,
    phase: Optional[RolloutPhase] = None,
    percentage: Optional[int] = None,
):
    """Actualiza el feature flag de un ETL específico."""
    if etl_name not in {"combustibles", "ute", "ose", "antel"}:
        raise HTTPException(status_code=400, detail=f"ETL desconocido: {etl_name}")

    if phase:
        feature_flags.set_phase(etl_name, phase)
        if phase in (RolloutPhase.CANARY, RolloutPhase.GRADUAL):
            feature_flags.enable_v2(etl_name)
        elif phase == RolloutPhase.FULL:
            feature_flags.enable_v2(etl_name)
        elif phase == RolloutPhase.DISABLED:
            feature_flags.disable_v2(etl_name)

    if percentage is not None:
        feature_flags.set_percentage(etl_name, percentage)

    flag = feature_flags.get(etl_name)
    return {
        "etl": etl_name,
        "updated": flag.dict() if flag else None,
    }
