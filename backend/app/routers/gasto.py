"""
Router para endpoints de gasto público (ejecución presupuestal MEF).

Endpoints:
  GET  /api/v1/gasto/organismos           - lista de organismos con datos
  GET  /api/v1/gasto/ejecucion            - ejecución filtrable por año/inciso
  GET  /api/v1/gasto/comparacion-anual    - comparación YoY para un inciso
  GET  /api/v1/gasto/narrativa            - resumen narrativo determinista del año
  GET  /api/v1/gasto/anomalias            - señales de anomalías detectadas
  POST /api/v1/gasto/anomalias/detectar   - ejecuta detección manual
"""

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AnomaliaPresupuestal, EjecucionPresupuestal
from app.services.analytics import run_deteccion
from app.services.narrativa import construir_narrativa

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


@router.get("/narrativa")
async def narrativa_gasto(
    anio: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Resumen narrativo determinista del gasto publico para un anio.
    Si no se especifica anio, usa el mas reciente disponible.
    """
    if anio is None:
        resultado = db.query(func.max(EjecucionPresupuestal.anio)).scalar()
        if resultado is None:
            raise HTTPException(status_code=404, detail="Sin datos de gasto")
        anio = resultado

    narrativa = construir_narrativa(db, anio)
    if narrativa.get("sin_datos"):
        raise HTTPException(status_code=404, detail=f"Sin datos para el año {anio}")
    return narrativa


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


# --------------------------------------------------------------------------
# Anomalías presupuestales
# --------------------------------------------------------------------------


def _anomalia_to_dict(a: AnomaliaPresupuestal) -> dict:
    return {
        "id": a.id,
        "anio": a.anio,
        "mes": a.mes,
        "inciso": a.inciso,
        "nombre_organismo": a.nombre_organismo,
        "tipo": a.tipo,
        "severidad": a.severidad,
        "descripcion": a.descripcion,
        "valor_observado": float(a.valor_observado) if a.valor_observado is not None else None,
        "valor_umbral": float(a.valor_umbral) if a.valor_umbral is not None else None,
        "detectado_en": a.detectado_en.isoformat() if a.detectado_en else None,
    }


@router.get("/anomalias")
async def listar_anomalias(
    anio: Optional[int] = None,
    mes: Optional[int] = None,
    severidad: Optional[str] = None,
    tipo: Optional[str] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """
    Retorna señales de anomalías detectadas.
    Filtrable por año, mes, severidad (CRITICA/ALTA/MEDIA/BAJA) y tipo.
    """
    query = db.query(AnomaliaPresupuestal)

    if anio:
        query = query.filter(AnomaliaPresupuestal.anio == anio)
    if mes is not None:
        query = query.filter(AnomaliaPresupuestal.mes == mes)
    if severidad:
        query = query.filter(AnomaliaPresupuestal.severidad == severidad.upper())
    if tipo:
        query = query.filter(AnomaliaPresupuestal.tipo == tipo)

    rows = (
        query.order_by(
            AnomaliaPresupuestal.detectado_en.desc(),
            AnomaliaPresupuestal.severidad,
        )
        .limit(limit)
        .all()
    )

    return [_anomalia_to_dict(r) for r in rows]


@router.post("/anomalias/detectar")
async def ejecutar_deteccion(
    anio: Optional[int] = None,
    mes: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Ejecuta la detección de anomalías manualmente para el año/mes indicados.
    Si no se especifica año usa el más reciente en DB.
    """
    resultado = run_deteccion(db, anio=anio, mes=mes)
    if resultado.get("error"):
        raise HTTPException(status_code=404, detail="Sin datos de ejecución presupuestal")
    return resultado


# --------------------------------------------------------------------------
# Exportación CSV
# --------------------------------------------------------------------------


def _csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    """Genera un StreamingResponse CSV a partir de una lista de dicts."""
    if not rows:
        raise HTTPException(status_code=404, detail="Sin datos para exportar")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/ejecucion/export.csv")
async def exportar_ejecucion_csv(
    anio: Optional[int] = None,
    inciso: Optional[str] = None,
    mes: Optional[int] = None,
    limit: int = Query(5000, le=20000),
    db: Session = Depends(get_db),
):
    """
    Exporta ejecución presupuestal como CSV descargable.
    Mismos filtros que /ejecucion.
    """
    query = db.query(EjecucionPresupuestal)
    if anio:
        query = query.filter(EjecucionPresupuestal.anio == anio)
    if inciso:
        query = query.filter(EjecucionPresupuestal.inciso == inciso)
    if mes is not None:
        query = query.filter(EjecucionPresupuestal.mes == mes)

    rows = query.order_by(EjecucionPresupuestal.anio.desc(), EjecucionPresupuestal.inciso).limit(limit).all()

    data = [
        {
            "anio": r.anio,
            "mes": r.mes if r.mes is not None else "",
            "inciso": r.inciso,
            "organismo": r.nombre_organismo,
            "credito_vigente_uyu": float(r.credito_vigente),
            "ejecutado_uyu": float(r.ejecutado),
            "porcentaje_ejecucion": r.porcentaje_ejecucion if r.porcentaje_ejecucion is not None else "",
            "fuente": r.fuente or "",
        }
        for r in rows
    ]
    fname = f"ejecucion_presupuestal_{anio or 'todos'}.csv"
    return _csv_response(data, fname)


@router.get("/anomalias/export.csv")
async def exportar_anomalias_csv(
    anio: Optional[int] = None,
    severidad: Optional[str] = None,
    tipo: Optional[str] = None,
    limit: int = Query(1000, le=5000),
    db: Session = Depends(get_db),
):
    """
    Exporta señales de anomalías detectadas como CSV descargable.
    """
    query = db.query(AnomaliaPresupuestal)
    if anio:
        query = query.filter(AnomaliaPresupuestal.anio == anio)
    if severidad:
        query = query.filter(AnomaliaPresupuestal.severidad == severidad.upper())
    if tipo:
        query = query.filter(AnomaliaPresupuestal.tipo == tipo)

    rows = query.order_by(AnomaliaPresupuestal.detectado_en.desc()).limit(limit).all()

    data = [
        {
            "anio": r.anio,
            "mes": r.mes if r.mes is not None else "",
            "inciso": r.inciso,
            "organismo": r.nombre_organismo,
            "tipo": r.tipo,
            "severidad": r.severidad,
            "descripcion": r.descripcion,
            "valor_observado": float(r.valor_observado) if r.valor_observado is not None else "",
            "valor_umbral": float(r.valor_umbral) if r.valor_umbral is not None else "",
            "detectado_en": r.detectado_en.isoformat() if r.detectado_en else "",
        }
        for r in rows
    ]
    fname = f"anomalias_presupuestales_{anio or 'todos'}.csv"
    return _csv_response(data, fname)
