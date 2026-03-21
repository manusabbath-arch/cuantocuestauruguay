"""
Router para endpoints de gasto público (ejecución presupuestal MEF).

Endpoints:
  GET  /api/v1/gasto/organismos           - lista de organismos con datos
  GET  /api/v1/gasto/ejecucion            - ejecución filtrable por año/inciso
  GET  /api/v1/gasto/comparacion-anual    - comparación YoY para un inciso
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import EjecucionPresupuestal

router = APIRouter(prefix="/api/v1/gasto", tags=["gasto"])


# --------------------------------------------------------------------------
# Schemas de respuesta (inline; si crece pasar a schemas.py)
# --------------------------------------------------------------------------


def _row_to_dict(row: EjecucionPresupuestal) -> dict:
    return {
        "id": row.id,
        "anio": row.anio,
        "mes": row.mes,
        "inciso": row.inciso,
        "nombre_organismo": row.nombre_organismo,
        "credito_vigente": float(row.credito_vigente),
        "ejecutado": float(row.ejecutado),
        "porcentaje_ejecucion": row.porcentaje_ejecucion,
        "fuente": row.fuente,
    }


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------


@router.get("/organismos")
async def listar_organismos(
    anio: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Lista organismos (incisos) disponibles con datos de ejecución presupuestal.
    Opcionalmente filtrar por año.
    """
    query = db.query(
        EjecucionPresupuestal.inciso,
        EjecucionPresupuestal.nombre_organismo,
        func.max(EjecucionPresupuestal.anio).label("ultimo_anio"),
    ).group_by(
        EjecucionPresupuestal.inciso,
        EjecucionPresupuestal.nombre_organismo,
    )

    if anio:
        query = query.filter(EjecucionPresupuestal.anio == anio)

    rows = query.order_by(EjecucionPresupuestal.inciso).all()

    return [{"inciso": r.inciso, "nombre_organismo": r.nombre_organismo, "ultimo_anio": r.ultimo_anio} for r in rows]


@router.get("/ejecucion")
async def obtener_ejecucion(
    anio: Optional[int] = None,
    inciso: Optional[str] = None,
    mes: Optional[int] = None,
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
):
    """
    Retorna datos de ejecución presupuestal filtrable por año, inciso y mes.
    Sin filtros retorna todos los registros (limitado a `limit`).
    """
    query = db.query(EjecucionPresupuestal)

    if anio:
        query = query.filter(EjecucionPresupuestal.anio == anio)
    if inciso:
        query = query.filter(EjecucionPresupuestal.inciso == inciso)
    if mes is not None:
        query = query.filter(EjecucionPresupuestal.mes == mes)

    rows = (
        query.order_by(
            EjecucionPresupuestal.anio.desc(),
            EjecucionPresupuestal.inciso,
        )
        .limit(limit)
        .all()
    )

    return [_row_to_dict(r) for r in rows]


@router.get("/comparacion-anual")
async def comparacion_anual(
    inciso: str = Query(..., description="Código de inciso (ej. '02')"),
    anio_base: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Comparación YoY para un inciso dado.
    Retorna los últimos dos años disponibles con diferencia absoluta y porcentual de ejecución.
    Si anio_base se especifica, compara ese año con el anterior.
    """
    query = (
        db.query(EjecucionPresupuestal)
        .filter(
            EjecucionPresupuestal.inciso == inciso,
            EjecucionPresupuestal.mes.is_(None),  # totales anuales
        )
        .order_by(EjecucionPresupuestal.anio.desc())
    )

    if anio_base:
        query = query.filter(EjecucionPresupuestal.anio.in_([anio_base, anio_base - 1]))

    rows = query.limit(2).all()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No hay datos anuales para inciso '{inciso}'")

    if len(rows) < 2:
        return {
            "inciso": inciso,
            "nombre_organismo": rows[0].nombre_organismo,
            "anio_actual": rows[0].anio,
            "ejecutado_actual": float(rows[0].ejecutado),
            "porcentaje_actual": rows[0].porcentaje_ejecucion,
            "anio_anterior": None,
            "ejecutado_anterior": None,
            "variacion_absoluta": None,
            "variacion_porcentual": None,
        }

    actual, anterior = rows[0], rows[1]
    variacion_abs = float(actual.ejecutado) - float(anterior.ejecutado)
    variacion_pct = (
        round(variacion_abs / float(anterior.ejecutado) * 100, 2)
        if anterior.ejecutado and float(anterior.ejecutado) != 0
        else None
    )

    return {
        "inciso": inciso,
        "nombre_organismo": actual.nombre_organismo,
        "anio_actual": actual.anio,
        "ejecutado_actual": float(actual.ejecutado),
        "porcentaje_actual": actual.porcentaje_ejecucion,
        "anio_anterior": anterior.anio,
        "ejecutado_anterior": float(anterior.ejecutado),
        "variacion_absoluta": round(variacion_abs, 2),
        "variacion_porcentual": variacion_pct,
    }
