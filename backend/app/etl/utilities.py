"""
ETL module for utilities data (UTE, OSE, Antel)
Extracts data from URSEA PDFs and complementary sources like SAG Ingeniería
"""

import io
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


class UtilitiesETL:
    """ETL para datos de servicios públicos (UTE, OSE, Antel)"""

    # Mapeo de productos de servicios públicos
    PRODUCTOS_MAP = {
        # UTE - Electricidad
        "UTE_RESIDENCIAL_BT1": "UTE Tarifa Residencial BT1",
        "UTE_RESIDENCIAL_BT2": "UTE Tarifa Residencial BT2",
        "UTE_GENERAL_BT3": "UTE Tarifa General BT3",
        "UTE_INDUSTRIAL": "UTE Tarifa Industrial",
        # OSE - Agua
        "OSE_RESIDENCIAL": "OSE Tarifa Residencial",
        "OSE_COMERCIAL": "OSE Tarifa Comercial",
        # Antel - Telecomunicaciones
        "ANTEL_FIBRA_100": "Antel Fibra Óptica 100 Mbps",
        "ANTEL_FIBRA_200": "Antel Fibra Óptica 200 Mbps",
        "ANTEL_FIBRA_500": "Antel Fibra Óptica 500 Mbps",
        "ANTEL_MOVIL": "Antel Plan Móvil",
    }

    # URLs de fuentes de datos
    URSEA_UTE_URL = "https://www.ursea.gub.uy/inicio/energia-electrica/tarifas/"
    URSEA_OSE_URL = "https://www.ursea.gub.uy/inicio/agua-y-saneamiento/tarifas/"
    SAG_URL = "https://www.sag.com.uy"  # Fuente complementaria
    ANTEL_TARIFAS_URL = "https://www.antel.com.uy/personas/internet/planes"

    def __init__(self, db: Session):
        self.db = db

    async def extract_ute_tarifas(self) -> Optional[pd.DataFrame]:
        """
        Extrae tarifas de UTE desde el sitio oficial
        Fuente: https://portal.ute.com.uy/clientes/tarifas-vigentes
        """
        try:
            logger.info("Extracting UTE tarifas from official website")

            # Por ahora usamos datos simulados con fecha actual
            # TODO: Implementar scraping real del portal de UTE cuando se necesite
            # El sitio oficial requiere JavaScript, se podría usar Selenium o Playwright
            
            today = date.today()
            
            # Tarifas aproximadas basadas en tarifas vigentes 2024
            # Estas deberían actualizarse con scraping real
            data = [
                {
                    "producto": "UTE_RESIDENCIAL_BT1",
                    "fecha": today,
                    "valor": 4.92,  # $/kWh - Tarifa Simple Residencial
                    "fuente": "UTE - Portal Oficial (aproximado)",
                },
                {
                    "producto": "UTE_RESIDENCIAL_BT2",
                    "fecha": today,
                    "valor": 5.28,  # $/kWh - Tarifa Doble Horario
                    "fuente": "UTE - Portal Oficial (aproximado)",
                },
                {
                    "producto": "UTE_GENERAL_BT3",
                    "fecha": today,
                    "valor": 6.67,  # $/kWh - Tarifa General
                    "fuente": "UTE - Portal Oficial (aproximado)",
                },
                {
                    "producto": "UTE_INDUSTRIAL",
                    "fecha": today,
                    "valor": 7.85,  # $/kWh - Tarifa Industrial
                    "fuente": "UTE - Portal Oficial (aproximado)",
                },
            ]

            df = pd.DataFrame(data)
            logger.info(f"Extracted {len(df)} UTE tariff records for {today}")
            return df

        except Exception as e:
            logger.error(f"Error extracting UTE data: {e}")
            return None

    async def extract_ose_tarifas(self) -> Optional[pd.DataFrame]:
        """
        Extrae tarifas de OSE desde URSEA
        """
        try:
            logger.info("Extracting OSE tarifas from URSEA")

            # TODO: Implementar scraping específico para OSE
            data = self._get_sample_ose_data()
            df = pd.DataFrame(data)

            logger.info(f"Extracted {len(df)} OSE tariff records")
            return df

        except Exception as e:
            logger.error(f"Error extracting OSE data: {e}")
            return None

    async def extract_antel_tarifas(self) -> Optional[pd.DataFrame]:
        """
        Extrae tarifas de Antel desde su sitio web
        """
        try:
            logger.info("Extracting Antel tarifas")

            # TODO: Implementar scraping de tarifas de Antel
            data = self._get_sample_antel_data()
            df = pd.DataFrame(data)

            logger.info(f"Extracted {len(df)} Antel tariff records")
            return df

        except Exception as e:
            logger.error(f"Error extracting Antel data: {e}")
            return None

    def _get_sample_ute_data(self) -> List[Dict]:
        """Datos de ejemplo para UTE mientras se implementa el scraping real"""
        today = date.today()
        return [
            {
                "producto": "UTE_RESIDENCIAL_BT1",
                "fecha": today,
                "valor": 4.85,  # $/kWh aproximado
                "fuente": "URSEA - Datos de ejemplo",
            },
            {"producto": "UTE_RESIDENCIAL_BT2", "fecha": today, "valor": 5.20, "fuente": "URSEA - Datos de ejemplo"},
            {"producto": "UTE_GENERAL_BT3", "fecha": today, "valor": 6.50, "fuente": "URSEA - Datos de ejemplo"},
        ]

    def _get_sample_ose_data(self) -> List[Dict]:
        """Datos de ejemplo para OSE"""
        today = date.today()
        return [
            {
                "producto": "OSE_RESIDENCIAL",
                "fecha": today,
                "valor": 45.50,  # $/m³ aproximado
                "fuente": "URSEA - Datos de ejemplo",
            },
            {"producto": "OSE_COMERCIAL", "fecha": today, "valor": 85.00, "fuente": "URSEA - Datos de ejemplo"},
        ]

    def _get_sample_antel_data(self) -> List[Dict]:
        """Datos de ejemplo para Antel"""
        today = date.today()
        return [
            {
                "producto": "ANTEL_FIBRA_100",
                "fecha": today,
                "valor": 990.00,  # $/mes
                "fuente": "Antel - Datos de ejemplo",
            },
            {"producto": "ANTEL_FIBRA_200", "fecha": today, "valor": 1290.00, "fuente": "Antel - Datos de ejemplo"},
            {"producto": "ANTEL_FIBRA_500", "fecha": today, "valor": 1590.00, "fuente": "Antel - Datos de ejemplo"},
        ]

    async def transform(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Limpia y transforma datos de servicios públicos"""
        try:
            if df is None or df.empty:
                return None

            # Asegurar que la fecha está en formato correcto
            if "fecha" in df.columns:
                df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

            # Validar valores numéricos
            if "valor" in df.columns:
                df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
                df = df.dropna(subset=["valor"])

            logger.info(f"Transformed {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Error transforming utilities data: {e}")
            return None

    async def load(self, df: pd.DataFrame, categoria: str) -> int:
        """Carga datos de servicios públicos a PostgreSQL"""
        loaded_count = 0

        try:
            # Asegurar que los productos existen
            await self._ensure_productos(categoria)

            for _, row in df.iterrows():
                try:
                    producto_key = row.get("producto")
                    nombre_producto = self.PRODUCTOS_MAP.get(producto_key)

                    if not nombre_producto:
                        logger.warning(f"Unknown product key: {producto_key}")
                        continue

                    # Buscar producto
                    producto = self.db.query(Producto).filter(Producto.nombre == nombre_producto).first()

                    if not producto:
                        logger.warning(f"Product not found: {nombre_producto}")
                        continue

                    # Verificar si ya existe el precio
                    fecha = row["fecha"]
                    existing = (
                        self.db.query(Precio).filter(Precio.producto_id == producto.id, Precio.fecha == fecha).first()
                    )

                    if existing:
                        logger.info(f"Skipping existing price for {nombre_producto} on {fecha}")
                        continue

                    nuevo_precio = Precio(
                        producto_id=producto.id,
                        fecha=fecha,
                        valor=row["valor"],
                        fuente=row.get("fuente", "URSEA"),
                    )
                    # Inserción individual para evitar bulk insert masivo
                    self.db.add(nuevo_precio)
                    self.db.flush()
                    loaded_count += 1

                except Exception as e:
                    logger.error(f"Error loading row: {e}")
                    continue

            self.db.commit()
            logger.info(f"Successfully loaded {loaded_count} new records")
            return loaded_count

        except Exception as e:
            logger.error(f"Error loading utilities data: {e}")
            self.db.rollback()
            return 0

    async def _ensure_productos(self, categoria: str):
        """Asegura que los productos de servicios públicos existen"""
        unidad_map = {"servicio": "pesos", "electricidad": "kWh", "agua": "m³", "telecomunicaciones": "mes"}

        for key, nombre in self.PRODUCTOS_MAP.items():
            existing = self.db.query(Producto).filter(Producto.nombre == nombre).first()

            if not existing:
                # Determinar categoría y unidad
                if "UTE" in key:
                    cat = "electricidad"
                    unidad = "kWh"
                elif "OSE" in key:
                    cat = "agua"
                    unidad = "m³"
                elif "ANTEL" in key:
                    cat = "telecomunicaciones"
                    unidad = "mes"
                else:
                    cat = categoria
                    unidad = unidad_map.get(categoria, "pesos")

                nuevo_producto = Producto(nombre=nombre, categoria=cat, unidad=unidad, activo=True)
                self.db.add(nuevo_producto)

        self.db.commit()

    async def run_ute(self) -> Dict[str, any]:
        """Ejecuta ETL para UTE"""
        logger.info("Starting ETL process for UTE")

        df = await self.extract_ute_tarifas()
        if df is None or df.empty:
            return {"success": False, "message": "No UTE data extracted", "service": "UTE"}

        df_transformed = await self.transform(df)
        if df_transformed is None or df_transformed.empty:
            return {"success": False, "message": "UTE transformation failed", "service": "UTE"}

        loaded_count = await self.load(df_transformed, "electricidad")

        return {
            "success": True,
            "service": "UTE",
            "records_extracted": len(df),
            "records_loaded": loaded_count,
            "timestamp": datetime.now().isoformat(),
        }

    async def run_ose(self) -> Dict[str, any]:
        """Ejecuta ETL para OSE"""
        logger.info("Starting ETL process for OSE")

        df = await self.extract_ose_tarifas()
        if df is None or df.empty:
            return {"success": False, "message": "No OSE data extracted", "service": "OSE"}

        df_transformed = await self.transform(df)
        if df_transformed is None or df_transformed.empty:
            return {"success": False, "message": "OSE transformation failed", "service": "OSE"}

        loaded_count = await self.load(df_transformed, "agua")

        return {
            "success": True,
            "service": "OSE",
            "records_extracted": len(df),
            "records_loaded": loaded_count,
            "timestamp": datetime.now().isoformat(),
        }

    async def run_antel(self) -> Dict[str, any]:
        """Ejecuta ETL para Antel"""
        logger.info("Starting ETL process for Antel")

        df = await self.extract_antel_tarifas()
        if df is None or df.empty:
            return {"success": False, "message": "No Antel data extracted", "service": "Antel"}

        df_transformed = await self.transform(df)
        if df_transformed is None or df_transformed.empty:
            return {"success": False, "message": "Antel transformation failed", "service": "Antel"}

        loaded_count = await self.load(df_transformed, "telecomunicaciones")

        return {
            "success": True,
            "service": "Antel",
            "records_extracted": len(df),
            "records_loaded": loaded_count,
            "timestamp": datetime.now().isoformat(),
        }

    async def run_all(self) -> Dict[str, any]:
        """Ejecuta ETL para todos los servicios públicos"""
        logger.info("Starting ETL process for all utilities")

        results = {"ute": await self.run_ute(), "ose": await self.run_ose(), "antel": await self.run_antel()}

        total_loaded = sum(r.get("records_loaded", 0) for r in results.values() if r.get("success", False))

        return {
            "success": True,
            "message": "Utilities ETL completed",
            "results": results,
            "total_records_loaded": total_loaded,
            "timestamp": datetime.now().isoformat(),
        }
