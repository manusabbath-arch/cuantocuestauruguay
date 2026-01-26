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
            # Normalizar nombres de columnas
            df.columns = df.columns.str.lower().str.strip()

            # Log columnas disponibles para debug
            logger.info(f"Available columns: {df.columns.tolist()}")

            # Intentar diferentes formatos de fecha comunes en datasets uruguayos
            fecha_columns = ["periodo", "fecha", "date", "mes"]
            fecha_col = None

            for col in fecha_columns:
                if col in df.columns:
                    fecha_col = col
                    break

            if not fecha_col:
                logger.error(f"No date column found. Columns: {df.columns.tolist()}")
                return None

            # Convertir fechas (intentar múltiples formatos)
            try:
                df["fecha"] = pd.to_datetime(df[fecha_col], format="%Y-%m", errors="coerce")
            except:
                try:
                    df["fecha"] = pd.to_datetime(df[fecha_col], errors="coerce")
                except Exception as e:
                    logger.error(f"Error parsing dates: {e}")
                    return None

            # Eliminar filas con fechas inválidas
            df = df.dropna(subset=["fecha"])
            df["fecha"] = df["fecha"].dt.date

            # Transformar formato long (melted) si es necesario
            # Esto depende de la estructura específica del dataset

            logger.info(f"Transformed {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            return None

    async def load(self, df: pd.DataFrame) -> int:
        """Carga datos a PostgreSQL"""
        loaded_count = 0

        try:
            # Primero, asegurar que los productos existen
            await self._ensure_productos()

            # Preparar datos para inserción
            # Este código necesita adaptarse según la estructura real del dataset
            for _, row in df.iterrows():
                try:
                    # Buscar o crear producto (esto es un ejemplo, ajustar según estructura real)
                    for key, nombre in self.PRODUCTOS_MAP.items():
                        if key.lower() in str(row).lower():
                            producto = self.db.query(Producto).filter(Producto.nombre == nombre).first()

                            if producto and "fecha" in row and pd.notna(row["fecha"]):
                                # Verificar si ya existe el precio para esta fecha
                                existing = (
                                    self.db.query(Precio)
                                    .filter(Precio.producto_id == producto.id, Precio.fecha == row["fecha"])
                                    .first()
                                )

                                if not existing:
                                    # Insertar nuevo precio
                                    nuevo_precio = Precio(
                                        producto_id=producto.id,
                                        fecha=row["fecha"],
                                        valor=row.get("precio", row.get("valor", 0)),
                                        fuente="CKAN - catalogodatos.gub.uy",
                                    )
                                    self.db.add(nuevo_precio)
                                    loaded_count += 1

                except Exception as e:
                    logger.error(f"Error loading row: {e}")
                    continue

            self.db.commit()
            logger.info(f"Successfully loaded {loaded_count} new records")
            return loaded_count

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.db.rollback()
            return 0

    async def _ensure_productos(self):
        """Asegura que los productos básicos existen en la base de datos"""
        for nombre in self.PRODUCTOS_MAP.values():
            existing = self.db.query(Producto).filter(Producto.nombre == nombre).first()

            if not existing:
                nuevo_producto = Producto(nombre=nombre, categoria="combustible", unidad="litro", activo=True)
                self.db.add(nuevo_producto)

        self.db.commit()

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
