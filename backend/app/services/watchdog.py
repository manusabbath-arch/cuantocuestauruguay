"""
Watchdog de salud de fuentes ETL.

Tres checks por fuente:

  1. silencio      — sin registros nuevos en N dias (umbral por fuente)
  2. rango         — ultimo valor fuera de rango historico esperado
  3. tariff_stale  — TARIFF_HISTORY de utilities mas antiguo que umbral de dias

Cada check retorna un dict con:
  fuente, check, estado ('ok'|'warn'|'error'), mensaje, ultimo_valor, ultimo_fecha

Se expone via GET /api/v1/etl/watchdog y se llama desde el scheduler diario.
No lanza excepciones — devuelve estado 'error' en el resultado si algo falla.
"""

import logging
import statistics
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import EjecucionPresupuestal, Precio, Producto

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Umbrales de silencio por fuente (dias sin datos nuevos → warn/error)
# ---------------------------------------------------------------------------

_SILENCIO_UMBRALES = {
    "combustible": {"dias_warn": 10, "dias_error": 20},
    "indice": {"dias_warn": 45, "dias_error": 70},
    "utilities": {"dias_warn": 45, "dias_error": 120},
    "gasto": {"dias_warn": 40, "dias_error": 60},
}

# Cuantos valores historicos usar para calcular rango esperado
_RANGO_VENTANA = 12


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dias_desde(fecha) -> Optional[int]:
    if fecha is None:
        return None
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    return (date.today() - fecha).days


def _check_silencio(fuente: str, ultima_fecha, dias_warn: int, dias_error: int) -> dict:
    dias = _dias_desde(ultima_fecha)
    if dias is None:
        return {
            "check": "silencio",
            "estado": "error",
            "mensaje": "Sin datos en DB para esta fuente.",
            "dias_sin_datos": None,
        }
    if dias >= dias_error:
        estado = "error"
    elif dias >= dias_warn:
        estado = "warn"
    else:
        estado = "ok"

    return {
        "check": "silencio",
        "estado": estado,
        "mensaje": f"Último dato hace {dias} día{'s' if dias != 1 else ''}."
        + (" Posible fallo de fuente." if estado == "error" else ""),
        "dias_sin_datos": dias,
    }


def _check_rango(fuente: str, ultimos_valores: list, ultimo_valor: float) -> dict:
    if len(ultimos_valores) < 4:
        return {"check": "rango", "estado": "ok", "mensaje": "Historial insuficiente para validar rango."}

    try:
        media = statistics.mean(ultimos_valores)
        sigma = statistics.stdev(ultimos_valores)
    except statistics.StatisticsError:
        return {"check": "rango", "estado": "ok", "mensaje": "No se pudo calcular rango."}

    if sigma == 0:
        return {"check": "rango", "estado": "ok", "mensaje": "Sin variación histórica."}

    z = abs(ultimo_valor - media) / sigma

    if z >= 3.0:
        estado, label = "error", f"{z:.1f}σ fuera del rango histórico"
    elif z >= 2.0:
        estado, label = "warn", f"{z:.1f}σ fuera del rango histórico"
    else:
        estado, label = "ok", "dentro del rango histórico"

    return {
        "check": "rango",
        "estado": estado,
        "mensaje": f"Último valor {ultimo_valor:.2f}: {label} (media={media:.2f}, σ={sigma:.2f}).",
        "z_score": round(z, 2),
        "media_historica": round(media, 2),
        "sigma_historica": round(sigma, 2),
    }


# ---------------------------------------------------------------------------
# Checks por tipo de fuente
# ---------------------------------------------------------------------------


def _check_combustibles(db: Session) -> list:
    resultados = []
    productos = db.query(Producto).filter(Producto.categoria == "combustible", Producto.activo.is_(True)).all()

    for prod in productos:
        try:
            ultima_fecha = db.query(func.max(Precio.fecha)).filter(Precio.producto_id == prod.id).scalar()
            umbrales = _SILENCIO_UMBRALES["combustible"]
            sil = _check_silencio("combustible", ultima_fecha, **umbrales)

            # Rango: últimos N valores
            ultimos = (
                db.query(Precio.valor)
                .filter(Precio.producto_id == prod.id)
                .order_by(Precio.fecha.desc())
                .limit(_RANGO_VENTANA + 1)
                .all()
            )
            valores = [float(r.valor) for r in ultimos]
            rango = (
                _check_rango("combustible", valores[1:], valores[0])
                if valores
                else {"check": "rango", "estado": "ok", "mensaje": "Sin valores."}
            )

            resultados.append(
                {
                    "fuente": "combustible",
                    "producto": prod.nombre,
                    "ultima_fecha": ultima_fecha.isoformat() if ultima_fecha else None,
                    "ultimo_valor": valores[0] if valores else None,
                    "checks": [sil, rango],
                    "estado_global": _estado_global([sil, rango]),
                }
            )
        except Exception as exc:
            logger.error(f"Watchdog combustible {prod.nombre}: {exc}")
            resultados.append(
                {
                    "fuente": "combustible",
                    "producto": prod.nombre,
                    "checks": [{"check": "excepcion", "estado": "error", "mensaje": str(exc)}],
                    "estado_global": "error",
                }
            )

    return resultados


def _check_indices(db: Session) -> list:
    resultados = []
    productos = db.query(Producto).filter(Producto.categoria == "indice", Producto.activo.is_(True)).all()

    for prod in productos:
        try:
            ultima_fecha = db.query(func.max(Precio.fecha)).filter(Precio.producto_id == prod.id).scalar()
            umbrales = _SILENCIO_UMBRALES["indice"]
            sil = _check_silencio("indice", ultima_fecha, **umbrales)

            ultimos = (
                db.query(Precio.valor)
                .filter(Precio.producto_id == prod.id)
                .order_by(Precio.fecha.desc())
                .limit(_RANGO_VENTANA + 1)
                .all()
            )
            valores = [float(r.valor) for r in ultimos]
            rango = (
                _check_rango("indice", valores[1:], valores[0])
                if valores
                else {"check": "rango", "estado": "ok", "mensaje": "Sin valores."}
            )

            resultados.append(
                {
                    "fuente": "indice",
                    "producto": prod.nombre,
                    "ultima_fecha": ultima_fecha.isoformat() if ultima_fecha else None,
                    "ultimo_valor": valores[0] if valores else None,
                    "checks": [sil, rango],
                    "estado_global": _estado_global([sil, rango]),
                }
            )
        except Exception as exc:
            logger.error(f"Watchdog indice {prod.nombre}: {exc}")
            resultados.append(
                {
                    "fuente": "indice",
                    "producto": prod.nombre,
                    "checks": [{"check": "excepcion", "estado": "error", "mensaje": str(exc)}],
                    "estado_global": "error",
                }
            )

    return resultados


def _check_utilities(db: Session) -> list:
    """
    Verifica utilities via DB (categoria 'utilities' o similares) y adicionalmente
    la antigüedad de TARIFF_HISTORY como señal de riesgo de datos hardcodeados.
    """
    resultados = []

    # Check por DB (productos categoria utilities/servicios)
    productos = (
        db.query(Producto).filter(Producto.categoria.in_(["utilities", "servicio"]), Producto.activo.is_(True)).all()
    )

    for prod in productos:
        try:
            ultima_fecha = db.query(func.max(Precio.fecha)).filter(Precio.producto_id == prod.id).scalar()
            umbrales = _SILENCIO_UMBRALES["utilities"]
            sil = _check_silencio("utilities", ultima_fecha, **umbrales)
            resultados.append(
                {
                    "fuente": "utilities",
                    "producto": prod.nombre,
                    "ultima_fecha": ultima_fecha.isoformat() if ultima_fecha else None,
                    "checks": [sil],
                    "estado_global": sil["estado"],
                }
            )
        except Exception as exc:
            logger.error(f"Watchdog utilities {prod.nombre}: {exc}")
            resultados.append(
                {
                    "fuente": "utilities",
                    "producto": prod.nombre,
                    "checks": [{"check": "excepcion", "estado": "error", "mensaje": str(exc)}],
                    "estado_global": "error",
                }
            )

    # Check de TARIFF_HISTORY stale (importacion lazy para no acoplar)
    try:
        from app.etl.utilities import TARIFF_HISTORY  # noqa: PLC0415

        fechas = []
        for entries in TARIFF_HISTORY.values():
            if entries:
                last = entries[-1]
                if isinstance(last, dict) and "fecha" in last:
                    fechas.append(last["fecha"])
                elif isinstance(last, (list, tuple)) and len(last) >= 1:
                    fechas.append(str(last[0]))

        if fechas:
            fechas_sorted = sorted(fechas, reverse=True)
            ultima_str = fechas_sorted[0]
            try:
                ultima_dt = date.fromisoformat(ultima_str)
                dias = (date.today() - ultima_dt).days
                if dias > 180:
                    estado = "error"
                elif dias > 90:
                    estado = "warn"
                else:
                    estado = "ok"
                resultados.append(
                    {
                        "fuente": "utilities",
                        "producto": "TARIFF_HISTORY (fallback)",
                        "ultima_fecha": ultima_str,
                        "checks": [
                            {
                                "check": "tariff_stale",
                                "estado": estado,
                                "mensaje": f"Última entrada de TARIFF_HISTORY tiene {dias} días."
                                + (" Riesgo de datos desactualizados." if estado != "ok" else ""),
                                "dias_sin_datos": dias,
                            }
                        ],
                        "estado_global": estado,
                    }
                )
            except ValueError:
                pass
    except Exception as exc:
        logger.warning(f"Watchdog TARIFF_HISTORY check failed: {exc}")

    return resultados


def _check_gasto(db: Session) -> list:
    try:
        ultima_fecha_row = (
            db.query(
                func.max(EjecucionPresupuestal.anio),
                func.max(EjecucionPresupuestal.mes),
            )
            .filter(EjecucionPresupuestal.mes.isnot(None))
            .first()
        )

        if ultima_fecha_row and ultima_fecha_row[0]:
            anio_max, mes_max = ultima_fecha_row
            # Aproximar fecha como primer dia del mes+anio
            try:
                ultima_fecha = date(anio_max, mes_max or 1, 1)
            except (TypeError, ValueError):
                ultima_fecha = None
        else:
            ultima_fecha = None

        umbrales = _SILENCIO_UMBRALES["gasto"]
        sil = _check_silencio("gasto", ultima_fecha, **umbrales)

        return [
            {
                "fuente": "gasto_publico",
                "producto": "Ejecución presupuestal MEF",
                "ultima_fecha": ultima_fecha.isoformat() if ultima_fecha else None,
                "checks": [sil],
                "estado_global": sil["estado"],
            }
        ]
    except Exception as exc:
        logger.error(f"Watchdog gasto: {exc}")
        return [
            {
                "fuente": "gasto_publico",
                "producto": "Ejecución presupuestal MEF",
                "checks": [{"check": "excepcion", "estado": "error", "mensaje": str(exc)}],
                "estado_global": "error",
            }
        ]


# ---------------------------------------------------------------------------
# Estado global de una lista de checks
# ---------------------------------------------------------------------------


def _estado_global(checks: list) -> str:
    estados = [c.get("estado", "ok") for c in checks]
    if "error" in estados:
        return "error"
    if "warn" in estados:
        return "warn"
    return "ok"


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------


def run_watchdog(db: Session) -> dict:
    """
    Corre todos los checks y retorna un resumen consolidado.
    """
    resultados = []
    resultados.extend(_check_combustibles(db))
    resultados.extend(_check_indices(db))
    resultados.extend(_check_utilities(db))
    resultados.extend(_check_gasto(db))

    errores = [r for r in resultados if r["estado_global"] == "error"]
    warnings = [r for r in resultados if r["estado_global"] == "warn"]

    estado_general = "ok"
    if errores:
        estado_general = "error"
    elif warnings:
        estado_general = "warn"

    return {
        "estado_general": estado_general,
        "ejecutado_en": datetime.now(timezone.utc).isoformat(),
        "resumen": {
            "total": len(resultados),
            "ok": len([r for r in resultados if r["estado_global"] == "ok"]),
            "warn": len(warnings),
            "error": len(errores),
        },
        "fuentes": resultados,
    }
