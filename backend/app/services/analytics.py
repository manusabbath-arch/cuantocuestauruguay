"""
Deteccion de anomalias presupuestales.

Tres reglas deterministas sobre EjecucionPresupuestal:

  1. ejecucion_baja   — organismo con % ejecucion < umbral segun mes del año
  2. variacion_atipica — variacion interanual > 2 desviaciones estandar del conjunto
  3. dato_faltante    — organismo presente en año anterior sin datos en año actual

Clasificacion de severidad (portada de metrics_calculator.py del fiscalizador):
  CRITICA  ejecucion < 15% a mitad de año, o variacion > 3 sigma
  ALTA     ejecucion < 30% a mitad de año, o variacion > 2 sigma
  MEDIA    ejecucion < 50% en Q3, o dato faltante
  BAJA     umbral informativo

Llamar a run_deteccion(db, anio, mes) luego de cada ETL mensual.
"""

import logging
import statistics
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import AnomaliaPresupuestal, EjecucionPresupuestal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Umbrales de ejecucion segun fraccion del año transcurrida
# ---------------------------------------------------------------------------

# (mes_hasta, umbral_pct): si el mes actual <= mes_hasta y pct < umbral → señal
_UMBRALES_EJECUCION = [
    (3, 15.0),  # Q1: esperamos al menos 15 %
    (6, 30.0),  # Q2 / mitad de año: al menos 30 %
    (9, 50.0),  # Q3: al menos 50 %
    (12, 70.0),  # Q4: al menos 70 %
]

_SIGMA_ALTA = 2.0
_SIGMA_CRITICA = 3.0


def _umbral_para_mes(mes: int) -> Optional[float]:
    for limite, umbral in _UMBRALES_EJECUCION:
        if mes <= limite:
            return umbral
    return None


def _severidad_ejecucion(pct: float, umbral: float) -> str:
    deficit = umbral - pct
    if deficit >= 20:
        return "CRITICA"
    if deficit >= 10:
        return "ALTA"
    return "MEDIA"


def _severidad_variacion(sigmas: float) -> str:
    if abs(sigmas) >= _SIGMA_CRITICA:
        return "CRITICA"
    return "ALTA"


# ---------------------------------------------------------------------------
# Upsert helper
# ---------------------------------------------------------------------------


def _upsert_anomalia(db: Session, **kwargs) -> None:
    """Inserta o actualiza una anomalia (clave: anio+mes+inciso+tipo)."""
    existing = (
        db.query(AnomaliaPresupuestal)
        .filter_by(
            anio=kwargs["anio"],
            mes=kwargs.get("mes"),
            inciso=kwargs["inciso"],
            tipo=kwargs["tipo"],
        )
        .first()
    )

    if existing:
        for k, v in kwargs.items():
            setattr(existing, k, v)
        existing.detectado_en = datetime.now(timezone.utc)
    else:
        db.add(AnomaliaPresupuestal(**kwargs))


# ---------------------------------------------------------------------------
# Regla 1 — ejecucion_baja
# ---------------------------------------------------------------------------


def _detectar_ejecucion_baja(
    db: Session,
    anio: int,
    mes: int,
    rows: list,
) -> int:
    umbral = _umbral_para_mes(mes)
    if umbral is None:
        return 0

    count = 0
    for row in rows:
        pct = row.porcentaje_ejecucion
        if pct is None:
            continue
        if pct < umbral:
            sev = _severidad_ejecucion(pct, umbral)
            _upsert_anomalia(
                db,
                anio=anio,
                mes=mes,
                inciso=row.inciso,
                nombre_organismo=row.nombre_organismo,
                tipo="ejecucion_baja",
                severidad=sev,
                descripcion=(
                    f"{row.nombre_organismo} ejecutó solo {pct:.1f}% de su crédito "
                    f"vigente al mes {mes} de {anio} (umbral esperado: {umbral:.0f}%)."
                ),
                valor_observado=round(pct, 4),
                valor_umbral=round(umbral, 4),
            )
            count += 1

    return count


# ---------------------------------------------------------------------------
# Regla 2 — variacion_atipica
# ---------------------------------------------------------------------------


def _detectar_variacion_atipica(
    db: Session,
    anio: int,
    mes: Optional[int],
    rows: list,
) -> int:
    anio_ant = anio - 1
    rows_ant = (
        db.query(EjecucionPresupuestal)
        .filter(
            EjecucionPresupuestal.anio == anio_ant,
            EjecucionPresupuestal.mes == mes,
        )
        .all()
    )
    if not rows_ant:
        return 0

    ejec_ant = {r.inciso: float(r.ejecutado) for r in rows_ant}

    variaciones = []
    for row in rows:
        ant = ejec_ant.get(row.inciso)
        if ant and ant > 0:
            variaciones.append((row, (float(row.ejecutado) - ant) / ant * 100))

    if len(variaciones) < 4:
        # Con menos de 4 puntos la desviacion no es estadisticamente util
        return 0

    valores = [v for _, v in variaciones]
    media = statistics.mean(valores)
    try:
        sigma = statistics.stdev(valores)
    except statistics.StatisticsError:
        return 0

    if sigma == 0:
        return 0

    count = 0
    for row, var_pct in variaciones:
        sigmas = (var_pct - media) / sigma
        if abs(sigmas) >= _SIGMA_ALTA:
            sev = _severidad_variacion(sigmas)
            direccion = "subió" if var_pct > 0 else "bajó"
            _upsert_anomalia(
                db,
                anio=anio,
                mes=mes,
                inciso=row.inciso,
                nombre_organismo=row.nombre_organismo,
                tipo="variacion_atipica",
                severidad=sev,
                descripcion=(
                    f"{row.nombre_organismo} {direccion} {abs(var_pct):.1f}% vs {anio_ant} "
                    f"({abs(sigmas):.1f} desviaciones estándar del promedio del conjunto)."
                ),
                valor_observado=round(var_pct, 4),
                valor_umbral=round(_SIGMA_ALTA * sigma + media, 4),
            )
            count += 1

    return count


# ---------------------------------------------------------------------------
# Regla 3 — dato_faltante
# ---------------------------------------------------------------------------


def _detectar_dato_faltante(
    db: Session,
    anio: int,
    mes: Optional[int],
    rows: list,
) -> int:
    anio_ant = anio - 1
    incisos_actuales = {r.inciso for r in rows}

    rows_ant = (
        db.query(EjecucionPresupuestal)
        .filter(
            EjecucionPresupuestal.anio == anio_ant,
            EjecucionPresupuestal.mes == mes,
        )
        .all()
    )

    count = 0
    for row_ant in rows_ant:
        if row_ant.inciso not in incisos_actuales:
            _upsert_anomalia(
                db,
                anio=anio,
                mes=mes,
                inciso=row_ant.inciso,
                nombre_organismo=row_ant.nombre_organismo,
                tipo="dato_faltante",
                severidad="MEDIA",
                descripcion=(
                    f"{row_ant.nombre_organismo} tenía datos en {anio_ant} "
                    f"pero no aparece en los datos de {anio}" + (f" (mes {mes})" if mes else "") + ". "
                    "Puede ser una reclasificación institucional o un gap en la fuente."
                ),
                valor_observado=None,
                valor_umbral=None,
            )
            count += 1

    return count


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------


def run_deteccion(
    db: Session,
    anio: Optional[int] = None,
    mes: Optional[int] = None,
) -> dict:
    """
    Ejecuta las tres reglas de deteccion para el anio/mes indicados.
    Si anio es None usa el mas reciente en DB.
    Si mes es None analiza los totales anuales (mes IS NULL).

    Retorna resumen con conteos por tipo.
    """
    if anio is None:
        from sqlalchemy import func as sqlfunc

        anio = db.query(sqlfunc.max(EjecucionPresupuestal.anio)).scalar()
        if anio is None:
            return {"error": "sin_datos"}

    rows = (
        db.query(EjecucionPresupuestal)
        .filter(
            EjecucionPresupuestal.anio == anio,
            EjecucionPresupuestal.mes == mes,
        )
        .all()
    )

    if not rows:
        logger.warning(f"run_deteccion: sin datos para anio={anio} mes={mes}")
        return {"anio": anio, "mes": mes, "total": 0}

    n_ejecucion = 0
    n_variacion = 0
    n_faltante = 0

    if mes is not None:
        n_ejecucion = _detectar_ejecucion_baja(db, anio, mes, rows)

    n_variacion = _detectar_variacion_atipica(db, anio, mes, rows)
    n_faltante = _detectar_dato_faltante(db, anio, mes, rows)

    db.commit()

    total = n_ejecucion + n_variacion + n_faltante
    logger.info(
        f"Deteccion anomalias anio={anio} mes={mes}: "
        f"ejecucion_baja={n_ejecucion} variacion_atipica={n_variacion} "
        f"dato_faltante={n_faltante} total={total}"
    )

    return {
        "anio": anio,
        "mes": mes,
        "ejecucion_baja": n_ejecucion,
        "variacion_atipica": n_variacion,
        "dato_faltante": n_faltante,
        "total": total,
    }
