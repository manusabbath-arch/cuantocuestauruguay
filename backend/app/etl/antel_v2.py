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
    # Datos actualizados de tienda.antel.com.uy (Enero 2026)
    PRODUCTOS_MAP = {
        "ANTEL_FIBRA_BASICO": "Antel Fibra Básico 400/30 Mbps",
        "ANTEL_FIBRA_PLUS": "Antel Fibra Plus 550/40 Mbps",
        "ANTEL_FIBRA_ENT_ESTANDAR": "Antel Fibra Entretenimiento Estándar 550/40 Mbps",
        "ANTEL_FIBRA_DGO1": "Antel Fibra DGO 1 400/30 Mbps",
        "ANTEL_FIBRA_ENT_PREMIUM": "Antel Fibra Entretenimiento Premium 650/40 Mbps",
        "ANTEL_FIBRA_DGO2": "Antel Fibra DGO 2 400/30 Mbps",
        "ANTEL_FIBRA_ENT_NETFLIX": "Antel Fibra Entretenimiento Netflix 650/40 Mbps",
        "ANTEL_FIBRA_SUPER_ENT": "Antel Fibra Super Entretenimiento 900/200 Mbps",
        "ANTEL_FIBRA_ULTRA": "Antel Fibra Ultra 1000/300 Mbps",
    }

    # Tarifas verificadas desde tienda.antel.com.uy (Enero 2026)
    TARIFF_HISTORY = {
        "ANTEL_FIBRA_BASICO": [
            {"fecha": "2026-01-01", "valor": 1650.00, "velocidad": "400/30"},
            {"fecha": "2025-12-01", "valor": 1595.00, "velocidad": "400/30"},
        ],
        "ANTEL_FIBRA_PLUS": [
            {"fecha": "2026-01-01", "valor": 2138.00, "velocidad": "550/40"},
            {"fecha": "2025-12-01", "valor": 2065.00, "velocidad": "550/40"},
        ],
        "ANTEL_FIBRA_ENT_ESTANDAR": [
            {"fecha": "2026-01-01", "valor": 2370.00, "velocidad": "550/40"},
            {"fecha": "2025-12-01", "valor": 2290.00, "velocidad": "550/40"},
        ],
        "ANTEL_FIBRA_DGO1": [
            {"fecha": "2026-01-01", "valor": 2530.00, "velocidad": "400/30"},
        ],
        "ANTEL_FIBRA_ENT_PREMIUM": [
            {"fecha": "2026-01-01", "valor": 2599.00, "velocidad": "650/40"},
        ],
        "ANTEL_FIBRA_DGO2": [
            {"fecha": "2026-01-01", "valor": 2889.00, "velocidad": "400/30"},
        ],
        "ANTEL_FIBRA_ENT_NETFLIX": [
            {"fecha": "2026-01-01", "valor": 2799.00, "velocidad": "650/40"},
        ],
        "ANTEL_FIBRA_SUPER_ENT": [
            {"fecha": "2026-01-01", "valor": 3420.00, "velocidad": "900/200"},
        ],
        "ANTEL_FIBRA_ULTRA": [
            {"fecha": "2026-01-01", "valor": 4342.00, "velocidad": "1000/300"},
            {"fecha": "2025-12-01", "valor": 4195.00, "velocidad": "1000/300"},
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
                    data.append(
                        {
                            "producto": producto_key,
                            "fecha": today,
                            "valor": latest["valor"],
                            "fuente": "Antel Portal (Verificado)",
                            "ultima_verificacion": latest["fecha"],
                        }
                    )

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
        2. Insert or update Precio records with deduplication

        Args:
            data: Cleaned and normalized DataFrame
        """
        logger.info(f"Loading {len(data)} Antel plan records to database")

        try:
            inserted = 0
            updated = 0

            for _, row in data.iterrows():
                producto_key = row["producto"]
                display_name = self.PRODUCTOS_MAP.get(producto_key, producto_key)

                # Ensure Producto exists
                producto = self.db_session.query(Producto).filter_by(nombre=display_name).first()

                if not producto:
                    logger.info(f"Creating new Producto: {display_name}")
                    producto = Producto(
                        nombre=display_name,
                        categoria="Servicios Públicos - Telecomunicaciones",
                        unidad="$/mes",
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
                        existing.fuente = row.get("fuente", "Antel ETL v2")
                        self.db_session.add(existing)
                        updated += 1
                        logger.debug(f"Updated {display_name} price for {row['fecha']}")
                else:
                    # Insert new price
                    precio = Precio(
                        producto_id=producto.id,
                        valor=float(row["valor"]),
                        fecha=row["fecha"],
                        fuente=row.get("fuente", "Antel ETL v2"),
                    )
                    self.db_session.add(precio)
                    inserted += 1

            self.db_session.commit()
            logger.info(f"Successfully loaded {inserted} new records, {updated} updated")

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error loading Antel data: {e}")
            raise

    # Note: run() method is inherited from ETLBase and calls extract(), transform(), load() automatically
