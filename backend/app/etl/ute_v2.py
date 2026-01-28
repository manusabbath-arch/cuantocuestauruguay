"""
ETL de tarifas UTE - Versión refactorizada usando packages compartidos.

Este archivo mistra cómo migrar el ETL de UTE para usar:
- ETLBase: Clase base común
- PDF parsing utilities: Manejo de PDFs locales
- TARIFF_HISTORY: Fallback verificado

Comparer con: app/etl/utilities.py.extract_ute_tarifas() (versión original)

Fuente: URSEA (Régimen Tarifario para Distribuidoras)
Última actualización histórico: Dic 2024
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
from app.etl.pdf_parser import list_pdfs_in_directory, parse_ute_tariff_pdf
from app.models.models import Precio, Producto
from packages.etl_core import ETLBase

logger = logging.getLogger(__name__)


class UTEETLv2(ETLBase):
    """
    ETL para tarifas de UTE desde múltiples fuentes.

    Versión 2: Refactorizada para usar paquetes compartidos.

    Estrategia de extracción (en orden de prioridad):
    1. PDF local (si existe en backend/pdfs/ute/)
    2. Histórico verificado (fallback garantizado)

    Mejoras vs versión original:
    - Hereda de ETLBase (patrón común)
    - Logging automático
    - Mejor manejo de errores
    - Métricas de ejecución
    - Estructura compatible con ose_v2.py y antel_v2.py
    """

    # Mapeo de nombres internos a nombres legibles
    PRODUCTOS_MAP = {
        "UTE_RESIDENCIAL_BT1": "UTE Residencial BT1",
        "UTE_RESIDENCIAL_BT2": "UTE Residencial BT2",
        "UTE_GENERAL_BT3": "UTE General BT3",
        "UTE_INDUSTRIAL": "UTE Industrial",
    }

    # Histórico verificado de tarifas (último recurso)
    TARIFF_HISTORY = {
        "UTE_RESIDENCIAL_BT1": [
            {"fecha": "2024-12-01", "valor": 8.50},
            {"fecha": "2024-11-01", "valor": 8.45},
            {"fecha": "2024-10-01", "valor": 8.40},
        ],
        "UTE_RESIDENCIAL_BT2": [
            {"fecha": "2024-12-01", "valor": 7.80},
            {"fecha": "2024-11-01", "valor": 7.75},
            {"fecha": "2024-10-01", "valor": 7.70},
        ],
        "UTE_GENERAL_BT3": [
            {"fecha": "2024-12-01", "valor": 7.20},
            {"fecha": "2024-11-01", "valor": 7.15},
            {"fecha": "2024-10-01", "valor": 7.10},
        ],
        "UTE_INDUSTRIAL": [
            {"fecha": "2024-12-01", "valor": 6.50},
            {"fecha": "2024-11-01", "valor": 6.45},
            {"fecha": "2024-10-01", "valor": 6.40},
        ],
    }

    def __init__(self, db: Session):
        """Initialize UTE ETL"""
        super().__init__(name="ute_tarifas", db_session=db)

    def extract(self) -> Optional[pd.DataFrame]:
        """
        Extract UTE tariffs from PDF or historical fallback.

        Priority:
        1. PDF local (backend/pdfs/ute/)
        2. Histórico verificado

        Returns:
            pd.DataFrame with columns: producto, fecha, valor, fuente, ultima_verificacion
        """
        logger.info("Starting UTE extract from PDF or history")

        try:
            # Intenta parsear PDF local primero
            pdf_dir = "backend/pdfs/ute"
            pdfs = list_pdfs_in_directory(pdf_dir)

            if pdfs:
                logger.info(f"Found {len(pdfs)} UTE PDF(s), attempting parse...")
                for pdf_path in pdfs:
                    try:
                        records = parse_ute_tariff_pdf(pdf_path)
                        if records:
                            logger.info(f"Successfully parsed {len(records)} records from {pdf_path}")
                            df = pd.DataFrame(records)
                            df["fecha"] = date.today()
                            df["fuente"] = "PDF Local (URSEA)"
                            return df
                    except Exception as e:
                        logger.warning(f"Failed to parse {pdf_path}: {e}")

            # Fallback a histórico verificado
            logger.info("Using fallback: historical UTE tariffs")
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
            logger.info(f"Extracted {len(df)} UTE tariffs from historical data")
            logger.info(f"DataFrame columns: {df.columns.tolist()}")
            logger.info(f"DataFrame shape: {df.shape}")
            return df

        except Exception as e:
            logger.error(f"Error during UTE extract: {e}")
            raise

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform UTE tariffs data.

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
        logger.info("Starting UTE transform")

        try:
            df = data.copy()

            # Normalize column names
            df.columns = df.columns.str.lower()

            # Map PDF parser columns to expected format
            # PDF parser returns: nombre, valor_str
            # We need: producto, valor
            if "nombre" in df.columns and "producto" not in df.columns:
                df["producto"] = df["nombre"]
                logger.debug("Mapped 'nombre' → 'producto'")

            if "valor_str" in df.columns and "valor" not in df.columns:
                # Parse valor_str to numeric
                # Handle formats like "8.50", "8,50", "$8.50", etc.
                def parse_valor(val_str):
                    if pd.isna(val_str):
                        return None
                    # Remove currency symbols and whitespace
                    clean = str(val_str).replace("$", "").replace("UYU", "").strip()
                    # Replace comma with dot (Uruguayan format)
                    clean = clean.replace(",", ".")
                    try:
                        return float(clean)
                    except ValueError:
                        return None

                df["valor"] = df["valor_str"].apply(parse_valor)
                logger.debug("Parsed 'valor_str' → 'valor'")

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
                raise ValueError(f"Missing required columns: {missing}. Available: {df.columns.tolist()}")

            # Validate valor is numeric and positive
            df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
            df = df[df["valor"] > 0]  # Remove invalid/negative values
            df = df.dropna(subset=["valor"])

            # Note: Not filtering by PRODUCTOS_MAP because PDF contains many tariff types
            # Load() will create productos dynamically as needed

            logger.info(f"Transformed {len(df)} UTE tariff records (from {len(data)} raw)")
            return df

        except Exception as e:
            logger.error(f"Error during UTE transform: {e}")
            raise

    def load(self, data: pd.DataFrame) -> None:
        """
        Load UTE tariffs into database.

        Operations:
        1. Ensure Producto records exist
        2. Insert or update Precio records

        Args:
            data: Cleaned and normalized DataFrame
        """
        logger.info(f"Loading {len(data)} UTE tariff records to database")

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
                        categoria="Servicios Públicos - Electricidad",
                        unidad="$/kWh",
                    )
                    self.db_session.add(producto)
                    self.db_session.flush()

                # Check if price already exists for this date
                existing = (
                    self.db_session.query(Precio)
                    .filter(Precio.producto_id == producto.id, Precio.fecha == row["fecha"])
                    .first()
                )

                if existing:
                    # Update if different
                    if abs(float(existing.valor) - float(row["valor"])) > 0.01:
                        existing.valor = float(row["valor"])
                        existing.fuente = row.get("fuente", "UTE ETL v2")
                        self.db_session.add(existing)
                        logger.debug(f"Updated {display_name} price for {row['fecha']}")
                else:
                    # Insert new price
                    precio = Precio(
                        producto_id=producto.id,
                        valor=float(row["valor"]),
                        fecha=row["fecha"],
                        fuente=row.get("fuente", "UTE ETL v2"),
                    )
                    self.db_session.add(precio)
                    inserted += 1

            self.db_session.commit()
            logger.info(f"Successfully loaded {inserted} UTE tariff records")

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error loading UTE data: {e}")
            raise

    # Note: run() method is inherited from ETLBase and calls extract(), transform(), load() automatically
