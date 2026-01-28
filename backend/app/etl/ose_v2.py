"""
ETL de tarifas OSE - Versión refactorizada usando packages compartidos.

Este archivo muestra cómo migrar el ETL de OSE para usar:
- ETLBase: Clase base común
- TARIFF_HISTORY: Datos verificados

Comparar con: app/etl/utilities.py.extract_ose_tarifas() (versión original)

Fuente: URSEA (Régimen Tarifario para OSE)
Última actualización histórico: Dic 2024

Nota: OSE expone data limitada públicamente. Se mantiene con histórico
actualizado mensualmente desde fuentes URSEA verificadas.
"""

import logging
import sys
import time
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Imports de la app
from app.core.config import settings
from app.etl.pdf_parser import list_pdfs_in_directory, parse_ose_tariff_pdf
from app.models.models import Precio, Producto
from packages.etl_core import ETLBase

logger = logging.getLogger(__name__)


class OSEETLv2(ETLBase):
    """
    ETL para tarifas de OSE desde histórico verificado.

    Versión 2: Refactorizada para usar paquetes compartidos.

    Estrategia:
    - OSE expone datos limitados públicamente
    - Se mantiene con histórico verificado actualizado mensualmente
    - Fuente: URSEA (Régimen Tarifario para OSE)

    Mejoras vs versión original:
    - Hereda de ETLBase (patrón común)
    - Logging automático
    - Mejor manejo de errores
    - Métricas de ejecución
    - Estructura compatible con ute_v2.py y antel_v2.py
    """

    # Mapeo de nombres internos a nombres legibles
    PRODUCTOS_MAP = {
        "OSE_RESIDENCIAL": "OSE Residencial",
        "OSE_COMERCIAL": "OSE Comercial",
    }

    # Histórico verificado de tarifas (fuente URSEA)
    # Actualizado: Enero 2026
    # Fuente: https://www.ursea.gub.uy/inicio/agua-y-saneamiento/tarifas/
    TARIFF_HISTORY = {
        "OSE_RESIDENCIAL": [
            {"fecha": "2026-01-28", "valor": 47.60},  # Enero 2026
            {"fecha": "2025-12-01", "valor": 45.50},  # Dic 2025
            {"fecha": "2025-11-01", "valor": 44.00},  # Nov 2025
            {"fecha": "2025-10-01", "valor": 42.50},  # Oct 2025
            {"fecha": "2025-09-01", "valor": 41.25},  # Sep 2025
        ],
        "OSE_COMERCIAL": [
            {"fecha": "2026-01-28", "valor": 88.25},  # Enero 2026
            {"fecha": "2025-12-01", "valor": 85.00},  # Dic 2025
            {"fecha": "2025-11-01", "valor": 82.50},  # Nov 2025
            {"fecha": "2025-10-01", "valor": 80.00},  # Oct 2025
            {"fecha": "2025-09-01", "valor": 77.50},  # Sep 2025
        ],
    }

    def __init__(self, db: Session):
        """Initialize OSE ETL"""
        super().__init__(name="ose_tarifas", db_session=db)

    def extract(self) -> Optional[pd.DataFrame]:
        """
        Extract OSE tariffs from PDF or verified historical data.

        Note: OSE exposes limited public data, so we use verified historical records
        from URSEA that are updated monthly.

        Returns:
            pd.DataFrame with columns: producto, fecha, valor, fuente, ultima_verificacion
        """
        logger.info("Starting OSE extract from PDF or verified history")

        try:
            # Intentar parsear PDF local primero
            pdf_dir = "backend/pdfs/ose"
            pdfs = list_pdfs_in_directory(pdf_dir)

            if pdfs:
                logger.info(f"Found {len(pdfs)} OSE PDF(s), attempting parse...")
                for pdf_path in pdfs:
                    try:
                        records = parse_ose_tariff_pdf(pdf_path)
                        if records:
                            logger.info(f"Successfully parsed {len(records)} records from {pdf_path}")
                            df = pd.DataFrame(records)
                            df["fecha"] = date.today()
                            df["fuente"] = "PDF Local (URSEA)"
                            return df
                    except Exception as e:
                        logger.warning(f"Failed to parse {pdf_path}: {e}")

            today = date.today()
            data = []

            for producto_key, display_name in self.PRODUCTOS_MAP.items():
                if producto_key in self.TARIFF_HISTORY:
                    history = self.TARIFF_HISTORY[producto_key]
                    latest = history[-1]
                    data.append(
                        {
                            "producto": producto_key,
                            "fecha": today,
                            "valor": latest["valor"],
                            "fuente": "Histórico URSEA (Verificado)",
                            "ultima_verificacion": latest["fecha"],
                        }
                    )

            df = pd.DataFrame(data)
            logger.info(f"Extracted {len(df)} OSE tariffs from verified history")
            return df

        except Exception as e:
            logger.error(f"Error during OSE extract: {e}")
            raise

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform OSE tariffs data.

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
        logger.info("Starting OSE transform")

        try:
            df = data.copy()

            # Normalize column names
            df.columns = df.columns.str.lower()

            # Map PDF parser columns to expected format
            if "valor_str" in df.columns and "valor" not in df.columns:
                def parse_valor(val_str):
                    if pd.isna(val_str):
                        return None
                    clean = str(val_str).replace("$", "").replace("UYU", "").strip()
                    clean = clean.replace(",", ".")
                    try:
                        return float(clean)
                    except ValueError:
                        return None

                df["valor"] = df["valor_str"].apply(parse_valor)

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

            logger.info(f"Transformed {len(df)} OSE tariff records")
            return df

        except Exception as e:
            logger.error(f"Error during OSE transform: {e}")
            raise

    def load(self, data: pd.DataFrame) -> None:
        """
        Load OSE tariffs into database.

        Operations:
        1. Ensure Producto records exist
        2. Insert or update Precio records

        Args:
            data: Cleaned and normalized DataFrame
        """
        logger.info(f"Loading {len(data)} OSE tariff records to database")

        try:
            inserted = 0

            for _, row in data.iterrows():
                producto_key = row["producto"]
                display_name = self.PRODUCTOS_MAP.get(producto_key, producto_key)

                # Ensure Producto exists
                producto = self.db_session.query(Producto).filter_by(nombre=display_name).first()

                if not producto:
                    logger.info(f"Creating new Producto: {display_name}")
                    producto = Producto(
                        nombre=display_name,
                        categoria="agua",
                        unidad="m³",
                        activo=True,
                    )
                    self.db_session.add(producto)
                    self.db_session.flush()

                # Avoid duplicates (producto_id + fecha)
                existing = (
                    self.db_session.query(Precio)
                    .filter_by(producto_id=producto.id, fecha=row["fecha"])
                    .first()
                )
                if existing:
                    logger.info(f"Skipping existing price for {display_name} on {row['fecha']}")
                    continue

                # Insert Precio
                precio = Precio(
                    producto_id=producto.id,
                    valor=float(row["valor"]),
                    fecha=row["fecha"],
                    fuente=row.get("fuente", "OSE ETL v2"),
                )
                self.db_session.add(precio)
                inserted += 1

            self.db_session.commit()
            logger.info(f"Successfully loaded {inserted} OSE tariff records")

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error loading OSE data: {e}")
            raise

    async def run(self):
        """
        Execute full OSE ETL pipeline.

        Returns:
            dict with execution status and metrics
        """
        logger.info("Starting OSE ETL v2 execution")
        start = time.monotonic()

        try:
            # Extract
            raw_data = self.extract()
            if raw_data is None or raw_data.empty:
                raise ValueError("No OSE data extracted")

            # Transform
            cleaned_data = self.transform(raw_data)
            if cleaned_data.empty:
                raise ValueError("No valid OSE data after transform")

            # Load
            self.load(cleaned_data)

            result = {
                "success": True,
                "name": self.name,
                "records_processed": len(cleaned_data),
                "duration_seconds": time.monotonic() - start,
                "errors": [],
            }

            logger.info(f"OSE ETL v2 completed successfully: {result}")
            return result

        except Exception as e:
            logger.error(f"OSE ETL v2 failed: {e}")
            return {
                "success": False,
                "name": self.name,
                "records_processed": 0,
                "duration_seconds": time.monotonic() - start,
                "errors": [str(e)],
            }
