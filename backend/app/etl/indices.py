import io
import logging
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Precio, Producto

logger = logging.getLogger(__name__)


class IndicesETL:
    """ETL para índices económicos oficiales (IPC y tipo de cambio BCU)."""

    PRODUCTOS_CONFIG = {
        "IPC": {
            "unidad": "indice",
            "fuente": "CKAN - Índice de Precios al Consumo (IPC)",
        },
        "Dólar BCU": {
            "unidad": "UYU",
            "fuente": "BCU - Cotización de monedas",
        },
    }

    MONTH_MAP = {
        "ene": 1,
        "enero": 1,
        "feb": 2,
        "febrero": 2,
        "mar": 3,
        "marzo": 3,
        "abr": 4,
        "abril": 4,
        "may": 5,
        "mayo": 5,
        "jun": 6,
        "junio": 6,
        "jul": 7,
        "julio": 7,
        "ago": 8,
        "agosto": 8,
        "sep": 9,
        "set": 9,
        "septiembre": 9,
        "setiembre": 9,
        "oct": 10,
        "octubre": 10,
        "nov": 11,
        "noviembre": 11,
        "dic": 12,
        "diciembre": 12,
    }

    def __init__(self, db: Session):
        self.db = db
        self.ipc_url = settings.CKAN_IPC_RESOURCE_URL
        self.bcu_url = settings.BCU_COTIZACIONES_URL
        self.dolar_row_filter = settings.BCU_DOLAR_ROW_FILTER

    async def extract(self) -> Dict[str, pd.DataFrame]:
        """Extrae datasets crudos desde CKAN y BCU."""
        extracted: Dict[str, pd.DataFrame] = {}

        ipc_df = await self.extract_ipc()
        if ipc_df is not None and not ipc_df.empty:
            extracted["ipc"] = ipc_df

        bcu_df = await self.extract_bcu()
        if bcu_df is not None and not bcu_df.empty:
            extracted["bcu"] = bcu_df

        return extracted

    async def extract_ipc(self) -> Optional[pd.DataFrame]:
        """Descarga el CSV oficial de IPC."""
        try:
            response = requests.get(self.ipc_url, timeout=30)
            response.raise_for_status()
            dataframe = pd.read_csv(io.StringIO(response.text), sep=None, engine="python")
            logger.info("Extracted %s IPC rows", len(dataframe))
            return dataframe
        except Exception as exc:
            logger.error("Error extracting IPC data: %s", exc)
            return None

    async def extract_bcu(self) -> Optional[pd.DataFrame]:
        """Extrae la tabla oficial de cotizaciones del BCU."""
        try:
            response = requests.get(self.bcu_url, timeout=30)
            response.raise_for_status()
            tables = pd.read_html(io.StringIO(response.text), decimal=",", thousands=".")

            for table in tables:
                normalized_columns = {str(column).strip().lower(): column for column in table.columns}
                if "moneda" in normalized_columns and "venta" in normalized_columns:
                    logger.info("Extracted %s BCU rows", len(table))
                    return table

            logger.warning("BCU cotizaciones table not found in page")
            return None
        except Exception as exc:
            logger.error("Error extracting BCU exchange data: %s", exc)
            return None

    async def transform(self, datasets: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
        """Normaliza datasets heterogéneos a la forma común del ETL."""
        frames = []

        ipc_df = datasets.get("ipc")
        if ipc_df is not None and not ipc_df.empty:
            transformed_ipc = self._transform_ipc(ipc_df)
            if transformed_ipc is not None and not transformed_ipc.empty:
                frames.append(transformed_ipc)

        bcu_df = datasets.get("bcu")
        if bcu_df is not None and not bcu_df.empty:
            transformed_bcu = self._transform_bcu(bcu_df)
            if transformed_bcu is not None and not transformed_bcu.empty:
                frames.append(transformed_bcu)

        if not frames:
            return None

        combined = pd.concat(frames, ignore_index=True)
        combined = combined.dropna(subset=["fecha", "producto_nombre", "precio"])
        logger.info("Transformed %s index rows", len(combined))
        return combined

    def _transform_ipc(self, dataframe: pd.DataFrame) -> Optional[pd.DataFrame]:
        date_series = self._build_date_series(dataframe)
        if date_series is None:
            logger.error("Unable to identify IPC date columns: %s", dataframe.columns.tolist())
            return None

        value_column = self._find_value_column(dataframe, exclude=list(dataframe.columns))
        if value_column is None:
            logger.error("Unable to identify IPC value column: %s", dataframe.columns.tolist())
            return None

        transformed = pd.DataFrame(
            {
                "fecha": pd.to_datetime(date_series, errors="coerce").dt.date,
                "producto_nombre": "IPC",
                "precio": self._to_numeric(dataframe[value_column]),
                "fuente": self.PRODUCTOS_CONFIG["IPC"]["fuente"],
            }
        )
        return transformed.dropna(subset=["fecha", "precio"])

    def _transform_bcu(self, dataframe: pd.DataFrame) -> Optional[pd.DataFrame]:
        moneda_column = self._find_column(dataframe, exact_names=["moneda"])
        venta_column = self._find_column(dataframe, exact_names=["venta"])
        fecha_column = self._find_column(dataframe, exact_names=["fecha"])

        if moneda_column is None or venta_column is None or fecha_column is None:
            logger.error("Unable to identify BCU columns: %s", dataframe.columns.tolist())
            return None

        filtered = dataframe[
            dataframe[moneda_column].astype(str).str.contains(self.dolar_row_filter, case=False, na=False)
        ]
        if filtered.empty:
            logger.warning("No BCU rows matched filter %s", self.dolar_row_filter)
            return None

        prioritized = filtered[filtered[moneda_column].astype(str).str.contains("CABLE", case=False, na=False)]
        selected = prioritized.iloc[0] if not prioritized.empty else filtered.iloc[0]

        transformed = pd.DataFrame(
            {
                "fecha": [pd.to_datetime(selected[fecha_column], dayfirst=True, errors="coerce").date()],
                "producto_nombre": ["Dólar BCU"],
                "precio": [self._coerce_number(selected[venta_column])],
                "fuente": [self.PRODUCTOS_CONFIG["Dólar BCU"]["fuente"]],
            }
        )
        return transformed.dropna(subset=["fecha", "precio"])

    async def load(self, dataframe: pd.DataFrame) -> int:
        """Persiste series normalizadas en la tabla de precios histórica."""
        loaded_count = 0

        try:
            await self._ensure_productos()

            for _, row in dataframe.iterrows():
                producto = self.db.query(Producto).filter(Producto.nombre == row["producto_nombre"]).first()
                if producto is None:
                    continue

                exists = (
                    self.db.query(Precio)
                    .filter(Precio.producto_id == producto.id, Precio.fecha == row["fecha"])
                    .first()
                )
                if exists:
                    continue

                precio = Precio(
                    producto_id=producto.id,
                    fecha=row["fecha"],
                    valor=row["precio"],
                    fuente=row.get("fuente") or self.PRODUCTOS_CONFIG[row["producto_nombre"]]["fuente"],
                )
                self.db.add(precio)
                self.db.flush()
                loaded_count += 1

            self.db.commit()
            logger.info("Loaded %s index rows", loaded_count)
            return loaded_count
        except Exception as exc:
            logger.error("Error loading indices data: %s", exc, exc_info=True)
            self.db.rollback()
            return 0

    async def _ensure_productos(self):
        for product_name, config in self.PRODUCTOS_CONFIG.items():
            existing = self.db.query(Producto).filter(Producto.nombre == product_name).first()
            if existing is None:
                self.db.add(
                    Producto(
                        nombre=product_name,
                        categoria="indice",
                        unidad=config["unidad"],
                        activo=True,
                    )
                )
        self.db.commit()

    async def run(self) -> Dict[str, object]:
        """Ejecuta el pipeline completo de índices."""
        datasets = await self.extract()
        if not datasets:
            return {"success": False, "message": "No data extracted"}

        transformed = await self.transform(datasets)
        if transformed is None or transformed.empty:
            return {"success": False, "message": "Transformation failed"}

        loaded_count = await self.load(transformed)
        extracted_count = sum(len(frame) for frame in datasets.values())

        return {
            "success": True,
            "records_extracted": extracted_count,
            "records_loaded": loaded_count,
            "timestamp": datetime.now().isoformat(),
            "sources": sorted(datasets.keys()),
        }

    def _build_date_series(self, dataframe: pd.DataFrame) -> Optional[pd.Series]:
        date_column = self._find_column(
            dataframe,
            exact_names=["fecha", "periodo", "año-mes", "ano-mes", "mes", "date"],
        )
        if date_column is not None:
            parsed = pd.to_datetime(dataframe[date_column], errors="coerce", dayfirst=True)
            if parsed.notna().any():
                return parsed

        year_column = self._find_column(dataframe, exact_names=["año", "ano", "year"])
        month_column = self._find_column(dataframe, exact_names=["mes", "month"])
        if year_column is not None and month_column is not None:
            years = pd.to_numeric(dataframe[year_column], errors="coerce")
            months = dataframe[month_column].apply(self._parse_month)
            series = pd.to_datetime(
                {
                    "year": years,
                    "month": months,
                    "day": 1,
                },
                errors="coerce",
            )
            if series.notna().any():
                return series

        return None

    def _find_value_column(self, dataframe: pd.DataFrame, exclude: Optional[list[str]] = None) -> Optional[str]:
        exclude = set(exclude or [])
        candidates = [
            "ipc",
            "indice",
            "índice",
            "valor",
            "value",
            "dato",
        ]

        for column in dataframe.columns:
            normalized = str(column).strip().lower()
            if str(column) in exclude and normalized not in candidates:
                continue
            if normalized in candidates or any(token in normalized for token in candidates):
                return column

        numeric_candidates = []
        for column in dataframe.columns:
            if str(column) in exclude:
                continue
            numeric_series = self._to_numeric(dataframe[column])
            if numeric_series.notna().any():
                numeric_candidates.append(column)

        return numeric_candidates[-1] if numeric_candidates else None

    def _find_column(self, dataframe: pd.DataFrame, exact_names: list[str]) -> Optional[str]:
        normalized_map = {str(column).strip().lower(): column for column in dataframe.columns}
        for candidate in exact_names:
            if candidate in normalized_map:
                return normalized_map[candidate]
        return None

    def _parse_month(self, value) -> Optional[int]:
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            month = int(value)
            return month if 1 <= month <= 12 else None

        raw = str(value).strip().lower()
        if raw.isdigit():
            month = int(raw)
            return month if 1 <= month <= 12 else None

        return self.MONTH_MAP.get(raw)

    def _to_numeric(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series.apply(self._coerce_number), errors="coerce")

    def _coerce_number(self, value) -> Optional[float]:
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()
        if not text:
            return None

        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")

        try:
            return float(text)
        except ValueError:
            return None
