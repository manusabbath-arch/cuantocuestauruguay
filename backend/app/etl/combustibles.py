import logging
from datetime import date, datetime
from typing import Dict, List, Optional

import pandas as pd
import requests
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Precio, Producto

logger = logging.getLogger(__name__)


class CombustiblesETL:
    """ETL para datos de combustibles desde CKAN API"""

    # Mapeo de nombres de productos de CKAN a nombres legibles
    PRODUCTOS_MAP = {
        "NAFTA_PREMIUM": "Nafta Premium 97",
        "NAFTA_SUPER": "Nafta Súper 95",
        "GASOIL_50S": "Gasoil 50-S",
        "GASOIL": "Gasoil Común",
        "SUPERGAS": "Supergás",
    }

    def __init__(self, db: Session):
        self.db = db
        self.api_url = f"{settings.CKAN_API_URL}/datastore_search"
        self.resource_id = settings.CKAN_COMBUSTIBLES_RESOURCE_ID

    async def extract(self) -> Optional[pd.DataFrame]:
        """Extrae datos de ANCAP vía CKAN API"""
        try:
            params = {"resource_id": self.resource_id, "limit": 1000}

            logger.info(f"Extracting data from CKAN API: {self.api_url}")
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get("success") and "result" in data:
                records = data["result"].get("records", [])
                if records:
                    df = pd.DataFrame(records)
                    logger.info(f"Extracted {len(df)} records")
                    return df
                else:
                    logger.warning("No records found in API response")
                    return None
            else:
                logger.error("API request was not successful")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error extracting data from CKAN API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {e}")
            return None

    async def transform(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Limpia y transforma datos"""
        try:
            # Log columnas originales
            logger.info(f"Original columns: {df.columns.tolist()}")

            # Buscar columna de fecha (respetar mayúsculas/minúsculas)
            fecha_col = None
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in ["ano-mes", "año-mes", "periodo", "fecha", "date", "mes"]:
                    fecha_col = col
                    break

            if not fecha_col:
                logger.error(f"No date column found. Columns: {df.columns.tolist()}")
                return None

            # Convertir fechas (formato YYYY-MM)
            df["fecha"] = pd.to_datetime(df[fecha_col], format="%Y-%m", errors="coerce")
            df = df.dropna(subset=["fecha"])
            df["fecha"] = df["fecha"].dt.date

            # Buscar columna de producto
            producto_col = None
            for col in df.columns:
                if col.lower() == "producto":
                    producto_col = col
                    break

            if not producto_col:
                logger.error(f"No producto column found. Columns: {df.columns.tolist()}")
                return None

            # Buscar columna de precio
            precio_col = None
            for col in df.columns:
                col_lower = col.lower()
                if "precio" in col_lower or "valor" in col_lower:
                    precio_col = col
                    break

            if not precio_col:
                logger.error(f"No precio column found. Columns: {df.columns.tolist()}")
                return None

            # Convertir precio (reemplazar coma por punto si es string)
            if df[precio_col].dtype == "object":
                df["precio"] = df[precio_col].str.replace(",", ".").astype(float)
            else:
                df["precio"] = pd.to_numeric(df[precio_col], errors="coerce")

            df = df.dropna(subset=["precio"])

            # Renombrar columna de producto
            df["producto_nombre"] = df[producto_col]

            # Mantener solo columnas necesarias
            df = df[["fecha", "producto_nombre", "precio"]]

            logger.info(f"Transformed {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            return None

    async def load(self, df: pd.DataFrame) -> int:
        """Carga datos a PostgreSQL"""
        loaded_count = 0

        try:
            logger.info(f"Load function called with {len(df)} rows")

            # Mapeo de nombres de CKAN
            nombre_map = {
                "Gasolina Premium 97": "Nafta Premium 97",
                "Gasolina Super 95": "Nafta Súper 95",
                "Gasoil 10-S": "Gasoil 50-S",
                "Gasoil 50-S": "Gasoil 50-S",
                "Gasoil": "Gasoil Común",
                "Supergas": "Supergás",
            }

            # Filtrar solo productos en el mapeo
            logger.info(f"Unique product names from source: {df['producto_nombre'].unique().tolist()}")
            df_filtered = df[df["producto_nombre"].isin(nombre_map.keys())].copy()
            logger.info(f"After filtering: {len(df_filtered)} rows match mapping")

            if len(df_filtered) == 0:
                logger.warning("No records after filtering")
                return 0

            # Asegurar que productos existen
            await self._ensure_productos()

            for idx, row in df_filtered.iterrows():
                try:
                    producto_original = row["producto_nombre"]
                    producto_nombre = nombre_map[producto_original]
                    fecha = row["fecha"]
                    precio = row["precio"]

                    producto = (
                        self.db.query(Producto)
                        .filter(Producto.nombre == producto_nombre)
                        .first()
                    )

                    if not producto:
                        logger.warning(f"Product not found: {producto_nombre}")
                        continue

                    exists = (
                        self.db.query(Precio)
                        .filter(Precio.producto_id == producto.id, Precio.fecha == fecha)
                        .first()
                    )

                    if exists:
                        continue

                    # Insertar individualmente para evitar problemas con bulk insert
                    precio_obj = Precio(
                        producto_id=producto.id,
                        fecha=fecha,
                        valor=precio,
                        fuente="CKAN - catalogodatos.gub.uy",
                    )
                    self.db.add(precio_obj)
                    self.db.flush()  # Forzar inserción inmediata
                    loaded_count += 1

                except Exception as e:
                    logger.error(f"Row {idx} error: {e}", exc_info=True)
                    continue

            self.db.commit()
            logger.info(f"Successfully loaded {loaded_count} records")
            return loaded_count

        except Exception as e:
            logger.error(f"Load error: {e}", exc_info=True)
            self.db.rollback()
            return 0

    async def _ensure_productos(self):
        """Asegura que los productos básicos existen en la base de datos"""
        created = 0
        existing_count = 0
        
        for nombre in self.PRODUCTOS_MAP.values():
            existing = self.db.query(Producto).filter(Producto.nombre == nombre).first()

            if not existing:
                nuevo_producto = Producto(
                    nombre=nombre, categoria="combustible", unidad="litro", activo=True
                )
                self.db.add(nuevo_producto)
                created += 1
            else:
                existing_count += 1

        self.db.commit()
        logger.info(
            f"_ensure_productos: Created {created}, Already existing {existing_count}"
        )

    async def run(self) -> Dict[str, any]:
        """Ejecuta el pipeline ETL completo"""
        logger.info("Starting ETL process for combustibles")

        # Extract
        df = await self.extract()
        if df is None or df.empty:
            return {"success": False, "message": "No data extracted"}

        # Transform
        df_transformed = await self.transform(df)
        if df_transformed is None or df_transformed.empty:
            return {"success": False, "message": "Transformation failed"}

        # Load
        loaded_count = await self.load(df_transformed)

        return {
            "success": True,
            "records_extracted": len(df),
            "records_loaded": loaded_count,
            "timestamp": datetime.now().isoformat(),
        }
