"""
ETL de planes Antel - Versión refactorizada usando packages compartidos.

Este archivo muestra cómo migrar el ETL de Antel para usar:
- ETLBase: Clase base común
- TARIFF_HISTORY: Datos verificados

Comparar con: app/etl/utilities.py.extract_antel_tarifas() (versión original)

Fuente: Antel (Planes de fibra óptica residencial)
Última actualización histórico: Dic 2024

Nota: Antel expone planes vía su portal público. Se mantiene con histórico
de cambios de precios verificado.
"""

import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Imports de la app
from app.core.config import settings
from app.models.models import Precio, Producto
from packages.etl_core import ETLBase

logger = logging.getLogger(__name__)


class AntelETLv2(ETLBase):
    """
    ETL para planes Antel desde histórico verificado.

    Versión 2: Refactorizada para usar paquetes compartidos.

    Estrategia:
    - Antel expone planes vía portal público
    - Se mantiene con histórico verificado de cambios de precio
    - Productos: ANTEL_FIBRA_100, ANTEL_FIBRA_200, ANTEL_FIBRA_500

    Mejoras vs versión original:
    - Hereda de ETLBase (patrón común)
    - Logging automático
    - Mejor manejo de errores
    - Métricas de ejecución
    - Estructura compatible con ute_v2.py y ose_v2.py
    """

    # Mapeo de nombres internos a nombres legibles
    PRODUCTOS_MAP = {
        "ANTEL_FIBRA_100": "Antel Fibra Óptica 100 Mbps",
        "ANTEL_FIBRA_200": "Antel Fibra Óptica 200 Mbps",
        "ANTEL_FIBRA_500": "Antel Fibra Óptica 500 Mbps",
    }

    # Histórico verificado de planes y precios
    TARIFF_HISTORY = {
        "ANTEL_FIBRA_100": [
            {"fecha": "2024-12-01", "valor": 895.00},
            {"fecha": "2024-11-01", "valor": 895.00},
            {"fecha": "2024-10-01", "valor": 895.00},
            {"fecha": "2024-09-01", "valor": 850.00},
        ],
        "ANTEL_FIBRA_200": [
            {"fecha": "2024-12-01", "valor": 1295.00},
            {"fecha": "2024-11-01", "valor": 1295.00},
            {"fecha": "2024-10-01", "valor": 1295.00},
            {"fecha": "2024-09-01", "valor": 1250.00},
        ],
        "ANTEL_FIBRA_500": [
            {"fecha": "2024-12-01", "valor": 1895.00},
            {"fecha": "2024-11-01", "valor": 1895.00},
            {"fecha": "2024-10-01", "valor": 1895.00},
            {"fecha": "2024-09-01", "valor": 1850.00},
        ],
    }

    def __init__(self, db: Session):
        """Initialize Antel ETL"""
        super().__init__(name="antel_planes", db_session=db)

    def extract(self) -> Optional[pd.DataFrame]:
        """
        Extract Antel plans from verified historical data.

        Note: Antel exposes plans via public portal, but we use verified
        historical records to track price changes over time.

        Returns:
            pd.DataFrame with columns: producto, fecha, valor, fuente, ultima_verificacion
        """
        logger.info("Starting Antel extract from verified history")

        try:
            today = date.today()
            data = []

            for producto_key, display_name in self.PRODUCTOS_MAP.items():
                if producto_key in self.TARIFF_HISTORY:
                    history = self.TARIFF_HISTORY[producto_key]
                    latest = history[-1]
                    data.append({
                        "producto": producto_key,
                        "display_name": display_name,
                        "fecha": today,
                        "valor": latest["valor"],
                        "fuente": "Antel Portal (Verificado)",
                        "ultima_verificacion": latest["fecha"],
                    })

            df = pd.DataFrame(data)
            logger.info(f"Extracted {len(df)} Antel plans from verified history")
            return df

        except Exception as e:
            logger.error(f"Error during Antel extract: {e}")
            raise

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform Antel plans data.

        Operations:
        1. Normalize column names (lowercase)
        2. Parse dates
        3. Remove invalid records
        4. Validate productos

        Args:
            data: Raw extracted data

        Returns:
            Cleaned and normalized DataFrame
        """
        logger.info("Starting Antel transform")

        try:
            df = data.copy()

            # Normalize column names
            df.columns = df.columns.str.lower()

            # Parse fecha column
            if "fecha" in df.columns:
                df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
            else:
                logger.warning("fecha column not found, using today's date")
                df["fecha"] = date.today()

            # Ensure all required columns exist
            required = ["producto", "valor", "fecha"]
            missing = [col for col in required if col not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            # Validate valor is numeric
            df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
            df = df.dropna(subset=["valor"])

            # Remove rows with invalid products
            valid_productos = set(self.PRODUCTOS_MAP.keys())
            df = df[df["producto"].isin(valid_productos)]

            logger.info(f"Transformed {len(df)} Antel plan records")
            return df

        except Exception as e:
            logger.error(f"Error during Antel transform: {e}")
            raise

    def load(self, data: pd.DataFrame) -> None:
        """
        Load Antel plans into database.

        Operations:
        1. Ensure Producto records exist
        2. Insert or update Precio records

        Args:
            data: Cleaned and normalized DataFrame
        """
        logger.info(f"Loading {len(data)} Antel plan records to database")

        try:
            inserted = 0

            for _, row in data.iterrows():
                producto_key = row["producto"]
                display_name = self.PRODUCTOS_MAP.get(
                    producto_key, producto_key
                )

                # Ensure Producto exists
                producto = self.db_session.query(Producto).filter_by(
                    nombre=display_name
                ).first()

                if not producto:
                    logger.info(f"Creating new Producto: {display_name}")
                    producto = Producto(
                        nombre=display_name,
                        categoria="Telecomunicaciones",
                        supplier="Antel",
                    )
                    self.db_session.add(producto)
                    self.db_session.flush()

                # Insert Precio
                precio = Precio(
                    producto_id=producto.id,
                    valor=float(row["valor"]),
                    fecha=row["fecha"],
                    fuente=row.get("fuente", "Antel ETL v2"),
                    metadata={
                        "producto_key": producto_key,
                        "ultima_verificacion": row.get("ultima_verificacion"),
                    },
                )
                self.db_session.add(precio)
                inserted += 1

            self.db_session.commit()
            logger.info(f"Successfully loaded {inserted} Antel plan records")

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error loading Antel data: {e}")
            raise

    async def run(self):
        """
        Execute full Antel ETL pipeline.

        Returns:
            dict with execution status and metrics
        """
        logger.info("Starting Antel ETL v2 execution")

        try:
            # Extract
            raw_data = self.extract()
            if raw_data is None or raw_data.empty:
                raise ValueError("No Antel data extracted")

            # Transform
            cleaned_data = self.transform(raw_data)
            if cleaned_data.empty:
                raise ValueError("No valid Antel data after transform")

            # Load
            self.load(cleaned_data)

            result = {
                "success": True,
                "name": self.name,
                "records_processed": len(cleaned_data),
                "duration_seconds": self.duration_seconds,
                "errors": [],
            }

            logger.info(f"Antel ETL v2 completed successfully: {result}")
            return result

        except Exception as e:
            logger.error(f"Antel ETL v2 failed: {e}")
            return {
                "success": False,
                "name": self.name,
                "records_processed": 0,
                "duration_seconds": self.duration_seconds,
                "errors": [str(e)],
            }
