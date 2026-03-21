"""
Narrativa automatica de gasto publico.

Genera frases interpretativas deterministas a partir de los datos
de ejecucion presupuestal ya almacenados en DB.
Sin LLM: toda la logica es calculo directo sobre los registros.
"""

from sqlalchemy.orm import Session

from app.models.models import EjecucionPresupuestal


def _fmt_millones(valor: float) -> str:
    """Formatea un valor en pesos uruguayos de forma legible."""
    if valor >= 1_000_000_000:
        return f"${valor / 1_000_000_000:.1f}B"
    if valor >= 1_000_000:
        return f"${valor / 1_000_000:.0f}M"
    return f"${valor:,.0f}"


def construir_narrativa(db: Session, anio: int) -> dict:
    """
    Retorna un dict con frases interpretativas para el anio dado.

    Campos:
      anio                  - año analizado
      resumen_global        - frase de resumen de ejecucion total
      mayor_gasto           - organismo con mayor ejecutado
      menor_ejecucion       - organismo con menor % de ejecucion (min 3 organismos)
      mayor_crecimiento     - organismo con mayor variacion interanual (si hay anio anterior)
      mayor_caida           - organismo con mayor caida interanual (si hay anio anterior)
      total_presupuestado   - credito vigente agregado
      total_ejecutado       - ejecutado agregado
      porcentaje_global     - % de ejecucion global
      organismos_analizados - cantidad de organismos con datos
    """
    # Totales anuales: mes IS NULL
    rows = (
        db.query(EjecucionPresupuestal)
        .filter(
            EjecucionPresupuestal.anio == anio,
            EjecucionPresupuestal.mes.is_(None),
        )
        .all()
    )

    if not rows:
        return {"anio": anio, "sin_datos": True}

    total_credito = sum(float(r.credito_vigente) for r in rows)
    total_ejecutado = sum(float(r.ejecutado) for r in rows)
    pct_global = round(total_ejecutado / total_credito * 100, 1) if total_credito else None

    # Organismo con mayor gasto ejecutado
    mayor = max(rows, key=lambda r: float(r.ejecutado))

    # Organismo con menor % de ejecucion (solo los que tienen credito > 0)
    con_credito = [r for r in rows if float(r.credito_vigente) > 0]
    menor_ejec = min(con_credito, key=lambda r: r.porcentaje_ejecucion or 0) if con_credito else None

    # Variacion interanual
    anio_ant = anio - 1
    rows_ant = (
        db.query(EjecucionPresupuestal)
        .filter(
            EjecucionPresupuestal.anio == anio_ant,
            EjecucionPresupuestal.mes.is_(None),
        )
        .all()
    )

    mayor_crecimiento = None
    mayor_caida = None

    if rows_ant:
        ejecutado_ant = {r.inciso: float(r.ejecutado) for r in rows_ant}
        variaciones = []
        for r in rows:
            ant = ejecutado_ant.get(r.inciso)
            if ant and ant > 0:
                pct_var = (float(r.ejecutado) - ant) / ant * 100
                variaciones.append((r, pct_var))

        if variaciones:
            top = max(variaciones, key=lambda x: x[1])
            bot = min(variaciones, key=lambda x: x[1])
            mayor_crecimiento = {
                "nombre": top[0].nombre_organismo,
                "variacion_pct": round(top[1], 1),
                "ejecutado_actual": float(top[0].ejecutado),
            }
            if bot[1] < 0:
                mayor_caida = {
                    "nombre": bot[0].nombre_organismo,
                    "variacion_pct": round(bot[1], 1),
                    "ejecutado_actual": float(bot[0].ejecutado),
                }

    return {
        "anio": anio,
        "sin_datos": False,
        "total_presupuestado": round(total_credito, 2),
        "total_ejecutado": round(total_ejecutado, 2),
        "porcentaje_global": pct_global,
        "organismos_analizados": len(rows),
        "resumen_global": (
            f"En {anio}, el Estado uruguayo ejecutó "
            f"{_fmt_millones(total_ejecutado)} de "
            f"{_fmt_millones(total_credito)} presupuestados" + (f" ({pct_global}%)." if pct_global is not None else ".")
        ),
        "mayor_gasto": {
            "nombre": mayor.nombre_organismo,
            "ejecutado": float(mayor.ejecutado),
            "porcentaje_ejecucion": mayor.porcentaje_ejecucion,
            "frase": (
                f"El organismo con mayor gasto fue "
                f"{mayor.nombre_organismo} "
                f"({_fmt_millones(float(mayor.ejecutado))})."
            ),
        },
        "menor_ejecucion": (
            {
                "nombre": menor_ejec.nombre_organismo,
                "porcentaje_ejecucion": menor_ejec.porcentaje_ejecucion,
                "frase": (
                    f"{menor_ejec.nombre_organismo} tuvo la ejecución más baja: "
                    f"{menor_ejec.porcentaje_ejecucion:.1f}% del crédito vigente."
                ),
            }
            if menor_ejec
            else None
        ),
        "mayor_crecimiento": mayor_crecimiento,
        "mayor_caida": mayor_caida,
    }
