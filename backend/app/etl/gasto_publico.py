"""
ETL para datos de ejecucion presupuestal del MEF/OPP (Uruguay).

Fuente primaria (GastoPublicoETL):
  - CSV de ejecucion presupuestal por inciso publicado en el CKAN del MEF:
    catalogodatos.gub.uy/organization/ministerio-de-economia-y-finanzas

Fuente complementaria (PresupuestoAbiertoETL):
  - Dataset "Balance de Ejecucion Presupuestal" publicado por OPP en CKAN:
    catalogodatos.gub.uy/dataset/balance-de-ejecucion-presupuestal
  - Datos mas granulares (unidad ejecutora, programa) pero mismos campos
    de nivel inciso que se persisten en EjecucionPresupuestal
  - Se usa como fallback o para anios no cubiertos por la fuente MEF

Campos esperados en el CSV (nombres pueden variar; se detectan dinamicamente):
  - Ejercicio / Anio      -> anio
  - Mes                   -> mes  (opcional; si no existe se imputa None)
  - Cod. Inciso / Inciso  -> inciso
  - Inciso / Organismo    -> nombre_organismo
  - Credito Vigente       -> credito_vigente
  - Ejecutado             -> ejecutado

Si el CSV tiene nombres distintos, ajustar FIELD_CANDIDATES.
"""

import io
import logging
import zipfile
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import requests
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import EjecucionPresupuestal

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Heurísticas de detección de columnas
# ---------------------------------------------------------------------------


def _find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Retorna el primer nombre de columna que coincida (case-insensitive)."""
    normalized = {c.strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    return None


FIELD_CANDIDATES = {
    "anio": ["ejercicio", "año", "anio", "year", "periodo"],
    "mes": ["mes", "month", "periodo_mes"],
    "inciso": ["cod. inciso", "código inciso", "codigo inciso", "inciso_cod", "inciso cod", "cod_inciso"],
    "nombre_organismo": ["inciso", "organismo", "nombre inciso", "nombre_organismo", "denominacion"],
    "credito_vigente": ["crédito vigente", "credito vigente", "credito_vigente", "credito", "presupuesto vigente"],
    "ejecutado": ["ejecutado", "ejecucion", "ejecución", "devengado"],
}


class GastoPublicoETL:
    """ETL para ejecución presupuestal MEF → tabla ejecucion_presupuestal."""

    def __init__(self, db: Session):
        self.db = db
        self.url = settings.CKAN_MEF_EJECUCION_URL

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    async def extract(self) -> Optional[pd.DataFrame]:
        """Descarga el CSV de ejecución presupuestal desde CKAN MEF."""
        try:
            logger.info("Downloading MEF presupuesto CSV from %s", self.url)
            response = requests.get(self.url, timeout=60)
            response.raise_for_status()
            df = pd.read_csv(
                io.StringIO(response.text),
                sep=None,
                engine="python",
                dtype=str,
                encoding_errors="replace",
            )
            logger.info("Extracted %d rows from MEF CSV", len(df))
            return df
        except Exception as exc:
            logger.error("Error extracting MEF gasto data: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def _detect_columns(self, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """Mapea nombres semánticos a nombres reales de columna en el CSV."""
        return {field: _find_col(df, candidates) for field, candidates in FIELD_CANDIDATES.items()}

    def _to_numeric(self, series: pd.Series) -> pd.Series:
        cleaned = (
            series.astype(str)
            .str.replace(r"\s", "", regex=True)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.replace("$", "", regex=False)
        )
        return pd.to_numeric(cleaned, errors="coerce")

    async def transform(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Normaliza el CSV crudo al esquema de EjecucionPresupuestal."""
        if df is None or df.empty:
            return None

        cols = self._detect_columns(df)
        logger.info("Detected columns: %s", cols)

        # Campos obligatorios
        required = ["anio", "nombre_organismo", "credito_vigente", "ejecutado"]
        missing = [f for f in required if cols[f] is None]
        if missing:
            logger.error("Required columns not found in MEF CSV: %s (available: %s)", missing, df.columns.tolist())
            return None

        result = pd.DataFrame()
        result["anio"] = pd.to_numeric(df[cols["anio"]], errors="coerce")

        if cols["mes"]:
            result["mes"] = pd.to_numeric(df[cols["mes"]], errors="coerce").where(
                pd.to_numeric(df[cols["mes"]], errors="coerce").notna(), None
            )
        else:
            result["mes"] = None

        if cols["inciso"]:
            result["inciso"] = df[cols["inciso"]].astype(str).str.strip().str.zfill(2)
        else:
            # Fallback: derive from row number — not ideal but avoids silent drop
            result["inciso"] = df.index.astype(str).str.zfill(4)

        result["nombre_organismo"] = df[cols["nombre_organismo"]].astype(str).str.strip().str[:200]
        result["credito_vigente"] = self._to_numeric(df[cols["credito_vigente"]])
        result["ejecutado"] = self._to_numeric(df[cols["ejecutado"]])
        result["fuente"] = f"CKAN MEF - {self.url}"

        before = len(result)
        result = result.dropna(subset=["anio", "nombre_organismo", "credito_vigente", "ejecutado"])
        result = result[result["credito_vigente"] >= 0]
        result = result[result["ejecutado"] >= 0]
        logger.info("Transformed %d → %d rows (dropped %d nulls/negatives)", before, len(result), before - len(result))

        return result if not result.empty else None

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    async def load(self, df: pd.DataFrame) -> int:
        """Inserta/actualiza filas en ejecucion_presupuestal, evitando duplicados."""
        if df is None or df.empty:
            return 0

        loaded = 0
        for _, row in df.iterrows():
            try:
                anio = int(row["anio"])
                mes = int(row["mes"]) if row["mes"] is not None and not pd.isna(row["mes"]) else None

                existing = (
                    self.db.query(EjecucionPresupuestal)
                    .filter(
                        and_(
                            EjecucionPresupuestal.anio == anio,
                            EjecucionPresupuestal.mes == mes,
                            EjecucionPresupuestal.inciso == str(row["inciso"]),
                        )
                    )
                    .first()
                )

                if existing:
                    existing.credito_vigente = row["credito_vigente"]
                    existing.ejecutado = row["ejecutado"]
                    existing.nombre_organismo = row["nombre_organismo"]
                    existing.fuente = row["fuente"]
                else:
                    self.db.add(
                        EjecucionPresupuestal(
                            anio=anio,
                            mes=mes,
                            inciso=str(row["inciso"]),
                            nombre_organismo=row["nombre_organismo"],
                            credito_vigente=row["credito_vigente"],
                            ejecutado=row["ejecutado"],
                            fuente=row["fuente"],
                        )
                    )
                    loaded += 1

                self.db.flush()
            except Exception as exc:
                logger.error("Error loading gasto row: %s", exc)
                continue

        self.db.commit()
        logger.info("Loaded %d new gasto records", loaded)
        return loaded

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    async def run(self) -> Dict:
        logger.info("Starting GastoPublicoETL")
        df_raw = await self.extract()

        if df_raw is None or df_raw.empty:
            return {"success": False, "message": "No data extracted from MEF CSV"}

        df_transformed = await self.transform(df_raw)
        if df_transformed is None or df_transformed.empty:
            return {"success": False, "message": "MEF CSV could not be transformed (column mapping failed)"}

        records_extracted = len(df_transformed)
        records_loaded = await self.load(df_transformed)

        return {
            "success": True,
            "message": "GastoPublicoETL completed",
            "records_extracted": records_extracted,
            "records_loaded": records_loaded,
            "timestamp": datetime.now().isoformat(),
        }


# ---------------------------------------------------------------------------
# PresupuestoAbiertoETL
# ---------------------------------------------------------------------------


class PresupuestoAbiertoETL:
    """ETL complementario usando el dataset OPP 'Balance de Ejecucion Presupuestal'.

    Descubre recursos disponibles via CKAN API, descarga el CSV del anio
    solicitado (o el mas reciente), y carga en la misma tabla
    ejecucion_presupuestal reusando la logica de GastoPublicoETL.

    El dataset OPP puede distribuirse como ZIP con multiples CSVs internos;
    se selecciona el primer archivo .csv encontrado.
    """

    CKAN_API_URL = "https://catalogodatos.gub.uy/api/3/action"
    DATASET_ID = "balance-de-ejecucion-presupuestal"

    def __init__(self, db: Session):
        self.db = db
        self._delegate = GastoPublicoETL(db)

    # ------------------------------------------------------------------
    # Descubrimiento de recursos CKAN
    # ------------------------------------------------------------------

    def _get_dataset_resources(self) -> List[Dict]:
        """Retorna la lista de recursos del dataset OPP via CKAN API."""
        url = f"{self.CKAN_API_URL}/package_show"
        try:
            resp = requests.get(url, params={"id": self.DATASET_ID}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                logger.error("CKAN package_show returned success=False for %s", self.DATASET_ID)
                return []
            return data["result"].get("resources", [])
        except Exception as exc:
            logger.error("Error fetching OPP dataset resources: %s", exc)
            return []

    def _pick_resource(self, resources: List[Dict], anio: Optional[int]) -> Optional[Dict]:
        """Selecciona el recurso CSV/ZIP mas adecuado para el anio dado.

        Estrategia:
        1. Si se pide un anio concreto, busca recurso cuyo nombre contenga ese anio.
        2. Si no, toma el recurso con nombre que contenga el numero de anio mayor.
        3. Filtra a recursos de formato CSV o ZIP.
        """
        candidates = [r for r in resources if r.get("format", "").upper() in ("CSV", "ZIP")]
        if not candidates:
            logger.warning("No CSV/ZIP resources found in OPP dataset")
            return None

        if anio:
            year_str = str(anio)
            year_match = [r for r in candidates if year_str in r.get("name", "")]
            if year_match:
                return year_match[0]
            logger.warning("No resource found for year %s; falling back to most recent", anio)

        # Ordenar por anio embebido en el nombre (ej. "balancepresupuesto2024v4")
        def _extract_year(r: Dict) -> int:
            name = r.get("name", "") + r.get("url", "")
            for token in reversed(name.split()):
                digits = "".join(c for c in token if c.isdigit())
                if len(digits) == 4 and digits.startswith(("20", "19")):
                    return int(digits)
            return 0

        return max(candidates, key=_extract_year)

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    async def extract(self, anio: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Descarga y descomprime (si es ZIP) el CSV OPP para el anio dado."""
        resources = self._get_dataset_resources()
        if not resources:
            return None

        resource = self._pick_resource(resources, anio)
        if not resource:
            return None

        url = resource.get("url", "")
        fmt = resource.get("format", "").upper()
        logger.info("Downloading OPP presupuesto resource: %s (format=%s)", url, fmt)

        try:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Error downloading OPP resource %s: %s", url, exc)
            return None

        try:
            if fmt == "ZIP":
                return self._read_csv_from_zip(resp.content)
            return pd.read_csv(
                io.StringIO(resp.text),
                sep=None,
                engine="python",
                dtype=str,
                encoding_errors="replace",
            )
        except Exception as exc:
            logger.error("Error parsing OPP resource content: %s", exc)
            return None

    def _read_csv_from_zip(self, content: bytes) -> Optional[pd.DataFrame]:
        """Extrae el primer CSV encontrado dentro de un ZIP."""
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if not csv_names:
                    logger.error("No CSV files found inside OPP ZIP")
                    return None
                logger.info("Reading CSV from ZIP: %s", csv_names[0])
                with zf.open(csv_names[0]) as f:
                    return pd.read_csv(
                        f,
                        sep=None,
                        engine="python",
                        dtype=str,
                        encoding_errors="replace",
                    )
        except zipfile.BadZipFile as exc:
            logger.error("OPP resource is not a valid ZIP: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Transform / Load — delegados a GastoPublicoETL
    # ------------------------------------------------------------------

    async def transform(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Reutiliza la transformacion de GastoPublicoETL."""
        result = await self._delegate.transform(df)
        if result is not None:
            result["fuente"] = f"OPP CKAN - {self.DATASET_ID}"
        return result

    async def load(self, df: pd.DataFrame) -> int:
        return await self._delegate.load(df)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    async def run(self, anio: Optional[int] = None) -> Dict:
        logger.info("Starting PresupuestoAbiertoETL (anio=%s)", anio)
        df_raw = await self.extract(anio=anio)

        if df_raw is None or df_raw.empty:
            return {"success": False, "message": "No data extracted from OPP CKAN dataset"}

        df_transformed = await self.transform(df_raw)
        if df_transformed is None or df_transformed.empty:
            return {
                "success": False,
                "message": "OPP CSV could not be transformed (column mapping failed)",
            }

        records_extracted = len(df_transformed)
        records_loaded = await self.load(df_transformed)

        return {
            "success": True,
            "message": "PresupuestoAbiertoETL completed",
            "source": "OPP CKAN",
            "anio_requested": anio,
            "records_extracted": records_extracted,
            "records_loaded": records_loaded,
            "timestamp": datetime.now().isoformat(),
        }
