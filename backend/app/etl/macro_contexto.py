"""
ETL para indicadores macroeconómicos de contexto (MIDES/CKAN).

Series disponibles (todas anuales, publicadas por MIDES en catalogodatos.gub.uy):

  isr             — Índice de Salario Real, base 2008=100, 1996–2018
                    resource: 805066d4-35a5-4aa4-9fb1-c7d402ebfb85

  pib_industrial  — PIB sector industrial, miles UYU constantes 2005, 2005–2018
  pib_agropecuario— PIB sector agropecuario, miles UYU constantes 2005, 2005–2018
  pib_construccion— PIB construcción, miles UYU constantes 2005, 2005–2018
  pib_servicios   — PIB servicios, miles UYU constantes 2005, 2005–2018
                    todos extraídos del resource: 856107dd-8b2a-4b3d-b6ec-62c959c2c5f0

Propósito: dar contexto a la sección de Gasto Público (costos laborales vs. ejecución
presupuestal; evolución del PIB sectorial como proxy de costos de producción).
"""

import logging
from io import StringIO
from typing import Optional

import pandas as pd
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import IndicadorMacro

logger = logging.getLogger(__name__)

_CKAN_DOWNLOAD = "https://catalogodatos.gub.uy/dataset/{dataset}/resource/{resource}/download"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; cuantocuestauruguay-etl/1.0)"}

# Sectores que extraemos del dataset PIB por industrias
_PIB_SECTORES = {
    "pib_industrial": ["INDUSTRIAS MANUFACTURERAS"],
    "pib_agropecuario": ["ACTIVIDADES PRIMARIAS"],
    "pib_construccion": ["CONSTRUCCION"],
    "pib_servicios": ["OTROS SERVICIOS", "COMERCIO. REPARACIONES. RESTAURANTES Y HOTELES"],
}

_UNIDAD_ISR = "indice base 2008=100"
_UNIDAD_PIB = "miles UYU constantes 2005"


def _fetch_csv(resource_id: str) -> Optional[pd.DataFrame]:
    """Descarga un CSV de CKAN por resource_id. Retorna DataFrame o None."""
    url = f"https://catalogodatos.gub.uy/dataset/resource/{resource_id}/download"
    # Algunos recursos no tienen el dataset en la URL; usamos la ruta corta
    try:
        r = requests.get(url, headers=_HEADERS, timeout=30, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))
    except Exception:
        pass

    # Fallback: URL directa con dataset placeholder omitido
    url2 = f"https://catalogodatos.gub.uy/dataset/mides-indicador-10458/resource/" f"{resource_id}/download"
    try:
        r = requests.get(url2, headers=_HEADERS, timeout=30, allow_redirects=True)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))
    except Exception as e:
        logger.error(f"Error descargando resource {resource_id}: {e}")
        return None


def _upsert(db: Session, codigo: str, nombre: str, anio: int, valor: float, unidad: str, fuente: str) -> bool:
    """Inserta o actualiza un indicador. Retorna True si fue nuevo."""
    existing = db.query(IndicadorMacro).filter(IndicadorMacro.codigo == codigo, IndicadorMacro.anio == anio).first()
    if existing:
        existing.valor = valor
        return False
    db.add(
        IndicadorMacro(
            codigo=codigo,
            nombre=nombre,
            anio=anio,
            valor=valor,
            unidad=unidad,
            fuente=fuente,
        )
    )
    return True


def _etl_isr(db: Session) -> dict:
    """Extrae el Índice de Salario Real (ISR)."""
    resource_id = settings.CKAN_ISR_RESOURCE_ID
    df = _fetch_csv(resource_id)
    if df is None:
        return {"success": False, "message": "No se pudo descargar ISR"}

    # Columnas esperadas: ao/año, valor
    col_anio = next((c for c in df.columns if c.strip().lower() in ("ao", "año", "anio", "year")), None)
    col_valor = next((c for c in df.columns if c.strip().lower() == "valor"), None)
    if not col_anio or not col_valor:
        return {"success": False, "message": f"Columnas inesperadas ISR: {list(df.columns)}"}

    nuevos = 0
    for _, row in df.iterrows():
        try:
            anio = int(row[col_anio])
            valor = float(row[col_valor])
        except (ValueError, TypeError):
            continue
        if _upsert(db, "isr", "Índice de Salario Real", anio, valor, _UNIDAD_ISR, f"MIDES/CKAN resource:{resource_id}"):
            nuevos += 1

    db.commit()
    return {"success": True, "records_loaded": nuevos, "total": len(df)}


def _etl_pib_industrias(db: Session) -> dict:
    """Extrae PIB por industrias y desagrega en códigos sectoriales."""
    resource_id = settings.CKAN_PIB_INDUSTRIAS_RESOURCE_ID

    # URL directa conocida
    url = f"https://catalogodatos.gub.uy/dataset/mides-indicador-11139/resource/" f"{resource_id}/download"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=30, allow_redirects=True)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
    except Exception as e:
        logger.error(f"Error descargando PIB industrias: {e}")
        return {"success": False, "message": str(e)}

    # Columnas: "Tipo de Actividad", ao, valor
    col_tipo = next((c for c in df.columns if "actividad" in c.lower() or "tipo" in c.lower()), None)
    col_anio = next((c for c in df.columns if c.strip().lower() in ("ao", "año", "anio")), None)
    col_valor = next((c for c in df.columns if c.strip().lower() == "valor"), None)
    if not col_tipo or not col_anio or not col_valor:
        return {"success": False, "message": f"Columnas inesperadas PIB: {list(df.columns)}"}

    df[col_tipo] = df[col_tipo].str.strip().str.upper()

    nuevos = 0
    for codigo, patrones in _PIB_SECTORES.items():
        mask = df[col_tipo].isin([p.upper() for p in patrones])
        sub = df[mask].copy()
        if sub.empty:
            logger.warning(f"Sin datos para sector {codigo} (patrones: {patrones})")
            continue

        # Si hay múltiples filas por año (ej. servicios suma dos categorías), agrupar
        agrupado = sub.groupby(col_anio)[col_valor].sum().reset_index()
        nombre = f"PIB {codigo.replace('pib_', '').capitalize()}"

        for _, row in agrupado.iterrows():
            try:
                anio = int(row[col_anio])
                valor = float(row[col_valor])
            except (ValueError, TypeError):
                continue
            if _upsert(db, codigo, nombre, anio, valor, _UNIDAD_PIB, f"MIDES/CKAN resource:{resource_id}"):
                nuevos += 1

    db.commit()
    return {"success": True, "records_loaded": nuevos}


class MacroContextoETL:
    """Orquesta todos los ETLs de contexto macroeconómico."""

    def __init__(self, db: Session):
        self.db = db

    async def run(self) -> dict:
        results = {}

        results["isr"] = _etl_isr(self.db)
        results["pib_industrias"] = _etl_pib_industrias(self.db)

        total_nuevos = sum(r.get("records_loaded", 0) for r in results.values())
        success = all(r.get("success", False) for r in results.values())

        return {
            "success": success,
            "records_loaded": total_nuevos,
            "detalle": results,
        }
