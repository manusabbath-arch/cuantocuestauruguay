"""
Router para indicadores macroeconómicos de contexto.

Endpoints:
  GET  /api/v1/macro/indicadores   - serie histórica filtrable por código
  GET  /api/v1/macro/codigos       - lista de indicadores disponibles
  POST /api/v1/macro/etl/run       - ejecuta el ETL manualmente
"""

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import IndicadorMacro

router = APIRouter(prefix="/api/v1/macro", tags=["macro"])


@router.get("/codigos")
async def listar_codigos(db: Session = Depends(get_db)):
    """Lista los indicadores disponibles con su nombre, unidad y rango de años."""
    rows = (
        db.query(
            IndicadorMacro.codigo,
            IndicadorMacro.nombre,
            IndicadorMacro.unidad,
        )
        .distinct(IndicadorMacro.codigo)
        .order_by(IndicadorMacro.codigo)
        .all()
    )
    if not rows:
        return []

    from sqlalchemy import func

    rangos = (
        db.query(
            IndicadorMacro.codigo,
            func.min(IndicadorMacro.anio).label("anio_desde"),
            func.max(IndicadorMacro.anio).label("anio_hasta"),
        )
        .group_by(IndicadorMacro.codigo)
        .all()
    )
    rango_map = {r.codigo: (r.anio_desde, r.anio_hasta) for r in rangos}

    return [
        {
            "codigo": r.codigo,
            "nombre": r.nombre,
            "unidad": r.unidad,
            "anio_desde": rango_map.get(r.codigo, (None, None))[0],
            "anio_hasta": rango_map.get(r.codigo, (None, None))[1],
        }
        for r in rows
    ]


@router.get("/indicadores")
async def obtener_indicadores(
    codigo: Optional[str] = None,
    anio_desde: Optional[int] = None,
    anio_hasta: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Serie histórica de indicadores macro.
    Sin filtros retorna todos los indicadores disponibles.
    """
    query = db.query(IndicadorMacro)
    if codigo:
        query = query.filter(IndicadorMacro.codigo == codigo)
    if anio_desde:
        query = query.filter(IndicadorMacro.anio >= anio_desde)
    if anio_hasta:
        query = query.filter(IndicadorMacro.anio <= anio_hasta)

    rows = query.order_by(IndicadorMacro.codigo, IndicadorMacro.anio).all()

    if not rows:
        raise HTTPException(status_code=404, detail="Sin datos para los filtros indicados")

    return [
        {
            "codigo": r.codigo,
            "nombre": r.nombre,
            "anio": r.anio,
            "valor": float(r.valor),
            "unidad": r.unidad,
            "fuente": r.fuente,
        }
        for r in rows
    ]


@router.get("/indicadores/export.csv")
async def exportar_indicadores_csv(
    codigo: Optional[str] = None,
    anio_desde: Optional[int] = None,
    anio_hasta: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Exporta indicadores macro como CSV descargable."""
    query = db.query(IndicadorMacro)
    if codigo:
        query = query.filter(IndicadorMacro.codigo == codigo)
    if anio_desde:
        query = query.filter(IndicadorMacro.anio >= anio_desde)
    if anio_hasta:
        query = query.filter(IndicadorMacro.anio <= anio_hasta)

    rows = query.order_by(IndicadorMacro.codigo, IndicadorMacro.anio).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Sin datos para exportar")

    data = [
        {
            "codigo": r.codigo,
            "nombre": r.nombre,
            "anio": r.anio,
            "valor": float(r.valor),
            "unidad": r.unidad,
            "fuente": r.fuente or "",
        }
        for r in rows
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)
    tag = codigo or "todos"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=indicadores_macro_{tag}.csv"},
    )


@router.post("/etl/run")
async def run_macro_etl(db: Session = Depends(get_db)):
    """Ejecuta el ETL de indicadores macro manualmente."""
    from app.etl.macro_contexto import MacroContextoETL

    etl = MacroContextoETL(db)
    result = await etl.run()
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result)
    return result
