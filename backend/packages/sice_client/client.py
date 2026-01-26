"""
Cliente para integración con OCDS Compras del Estado Uruguayo.

Accede a datos de compras públicas en formato OCDS (Open Contracting Data Standard)
desde catalogodatos.gub.uy.

Dataset: Histórico de compras ARCE
URL: https://catalogodatos.gub.uy/dataset/datos-historicos-de-compras
"""

import os
import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import logging
import zipfile
import io

logger = logging.getLogger(__name__)


@dataclass
class SICETransaction:
    """
    Transacción de compra pública del Estado uruguayo.
    
    Compatible con modelo Transaction de shared_models para interoperabilidad.
    """
    id: str
    fecha: datetime
    monto: float
    proveedor: str
    categoria: str
    descripcion: str
    organismo: str  # Entidad del Estado
    anomaly_documented: Optional[bool] = None
    anomaly_reason: Optional[str] = None
    
    def to_transaction(self):
        """
        Convertir a modelo Transaction compartido.
        
        Returns:
            Transaction object de shared_models
        """
        from packages.shared_models import Transaction
        from decimal import Decimal
        
        return Transaction(
            transaction_id=self.id,
            monto=Decimal(str(self.monto)),
            moneda="UYU",
            proveedor=self.proveedor,
            entidad=self.organismo,
            categoria=self.categoria,
            descripcion=self.descripcion,
            fecha=self.fecha,
            fuente="SICE - catalogodatos.gub.uy",
            is_anomaly=self.anomaly_documented,
            anomaly_reason=self.anomaly_reason
        )


class SICEComprasClient:
    """
    Cliente para acceder a datos OCDS de Compras Públicas Uruguay.
    
    Soporta:
    - Descarga de datos históricos por año (formato ZIP con JSON OCDS)
    - Parseo de releases OCDS a transacciones
    - Filtrado por anomalías documentadas
    - Fallback a datos sintéticos para testing
    
    Ejemplo:
        client = SICEComprasClient()
        
        # Obtener compras de 2024
        transactions = client.get_compras(year=2024, limit=1000)
        
        # Convertir a DataFrame
        df = client.to_dataframe(transactions)
        
        # Separar normales de anomalías
        normal, anomalous = client.filter_by_anomalies(transactions)
    """
    
    # URLs del catálogo de datos abiertos
    CATALOG_BASE_URL = "https://catalogodatos.gub.uy"
    DATASET_ID = "5203d170-e9ec-44d3-b09c-c0ef02270cc9"
    
    # Mapeo año -> resource_id (datos reales de la API)
    YEAR_TO_RESOURCE = {
        2024: "12508c0e-6857-406b-8aca-a63e66920e9f",
        2023: "e4de0c01-285a-4ba2-ba9c-bc5411cacd5e",
        2022: "703fc3f1-c251-4f43-a1d5-11380fa741f6",
        2021: "16f2facf-1b13-4e71-82f1-13fae7a25cab",
    }
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        use_fallback: bool = True,
        timeout: int = 30
    ):
        """
        Inicializar cliente SICE.
        
        Args:
            api_key: API key para catalogodatos.gub.uy (opcional)
            use_fallback: Si True, usa datos sintéticos cuando API no disponible
            timeout: Timeout en segundos para requests
        """
        self.api_key = api_key or os.getenv("SICE_API_KEY", "")
        self.use_fallback = use_fallback
        self.session = requests.Session()
        self.session.timeout = timeout
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "CuantoCuestaUruguay/1.0"
            })
        else:
            self.session.headers.update({
                "User-Agent": "CuantoCuestaUruguay/1.0"
            })
    
    def get_compras(
        self,
        year: int,
        month: Optional[int] = None,
        limit: int = 1000
    ) -> List[SICETransaction]:
        """
        Obtener compras públicas por año.
        
        Args:
            year: Año de las compras (2021-2024)
            month: Mes opcional para filtrar
            limit: Límite de transacciones a retornar
        
        Returns:
            Lista de transacciones de compras públicas
        """
        logger.info(f"Obteniendo compras SICE: año {year}")
        
        # Verificar si el año tiene resource_id
        if year not in self.YEAR_TO_RESOURCE:
            logger.warning(
                f"Año {year} no disponible en catálogo. "
                f"Años disponibles: {list(self.YEAR_TO_RESOURCE.keys())}"
            )
            if self.use_fallback:
                logger.info("Usando datos sintéticos de fallback")
                return self._get_synthetic_data(year, month, limit)
            return []
        
        resource_id = self.YEAR_TO_RESOURCE[year]
        
        try:
            # Obtener URL de descarga del recurso
            resource_url = self._get_resource_url(resource_id)
            
            if not resource_url:
                raise Exception(f"No se pudo obtener URL del recurso {resource_id}")
            
            # Descargar y parsear datos OCDS
            transactions = self._download_and_parse_ocds(resource_url, year, month, limit)
            
            logger.info(f"Obtenidas {len(transactions)} transacciones de {year}")
            return transactions
            
        except Exception as e:
            logger.error(f"Error obteniendo compras SICE: {e}")
            
            if self.use_fallback:
                logger.info("Usando datos sintéticos de fallback")
                return self._get_synthetic_data(year, month, limit)
            
            return []
    
    def _get_resource_url(self, resource_id: str) -> Optional[str]:
        """
        Obtener URL de descarga de un recurso.
        
        Args:
            resource_id: ID del recurso en CKAN
        
        Returns:
            URL de descarga del recurso
        """
        try:
            url = f"{self.CATALOG_BASE_URL}/api/3/action/resource_show"
            params = {"id": resource_id}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success"):
                return data["result"].get("url")
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo URL del recurso: {e}")
            return None
    
    def _download_and_parse_ocds(
        self,
        url: str,
        year: int,
        month: Optional[int],
        limit: int
    ) -> List[SICETransaction]:
        """
        Descargar y parsear archivo OCDS (generalmente ZIP con JSON).
        
        Args:
            url: URL del archivo
            year: Año de las compras
            month: Mes opcional para filtrar
            limit: Límite de transacciones
        
        Returns:
            Lista de transacciones parseadas
        """
        try:
            logger.info(f"Descargando datos OCDS de: {url}")
            
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Detectar si es ZIP
            if url.endswith('.zip') or 'zip' in response.headers.get('Content-Type', ''):
                return self._parse_zip_ocds(response.content, year, month, limit)
            else:
                # JSON directo
                return self._parse_json_ocds(response.text, year, month, limit)
                
        except Exception as e:
            logger.error(f"Error descargando/parseando OCDS: {e}")
            raise
    
    def _parse_zip_ocds(
        self,
        zip_content: bytes,
        year: int,
        month: Optional[int],
        limit: int
    ) -> List[SICETransaction]:
        """Parsear archivo ZIP con JSON OCDS."""
        transactions = []
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
                for filename in zf.namelist():
                    if filename.endswith('.json'):
                        with zf.open(filename) as f:
                            json_content = f.read().decode('utf-8')
                            txns = self._parse_json_ocds(json_content, year, month, limit - len(transactions))
                            transactions.extend(txns)
                            
                            if len(transactions) >= limit:
                                break
        
        except Exception as e:
            logger.error(f"Error parseando ZIP OCDS: {e}")
        
        return transactions[:limit]
    
    def _parse_json_ocds(
        self,
        json_content: str,
        year: int,
        month: Optional[int],
        limit: int
    ) -> List[SICETransaction]:
        """
        Parsear JSON OCDS a transacciones.
        
        Formato OCDS: https://standard.open-contracting.org/latest/en/
        """
        transactions = []
        
        try:
            data = json.loads(json_content)
            
            # OCDS puede tener releases o records
            releases = data.get('releases', [])
            
            for release in releases[:limit]:
                try:
                    # Parsear release OCDS a transacción
                    txn = self._parse_ocds_release(release, year, month)
                    if txn:
                        transactions.append(txn)
                        
                except Exception as e:
                    logger.debug(f"Error parseando release: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parseando JSON OCDS: {e}")
        
        return transactions
    
    def _parse_ocds_release(
        self,
        release: dict,
        year: int,
        month: Optional[int]
    ) -> Optional[SICETransaction]:
        """
        Parsear un release OCDS individual a SICETransaction.
        
        Args:
            release: Objeto release de OCDS
            year: Año esperado
            month: Mes opcional para filtrar
        
        Returns:
            SICETransaction o None si no se puede parsear
        """
        try:
            # Campos comunes de OCDS
            ocid = release.get('ocid', 'unknown')
            
            # Fecha del release
            date_str = release.get('date', '')
            fecha = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Filtrar por mes si se especificó
            if month and fecha.month != month:
                return None
            
            # Awards (adjudicaciones)
            awards = release.get('awards', [])
            if not awards:
                return None
            
            award = awards[0]  # Tomar el primero
            
            # Monto
            value = award.get('value', {})
            monto = float(value.get('amount', 0))
            
            # Proveedor
            suppliers = award.get('suppliers', [{}])
            proveedor = suppliers[0].get('name', 'Desconocido') if suppliers else 'Desconocido'
            
            # Organismo (buyer)
            buyer = release.get('buyer', {})
            organismo = buyer.get('name', 'Desconocido')
            
            # Descripción
            descripcion = release.get('title', '') or award.get('title', '')
            
            # Categoría (tender mainProcurementCategory)
            tender = release.get('tender', {})
            categoria = tender.get('mainProcurementCategory', 'Desconocido')
            
            return SICETransaction(
                id=ocid,
                fecha=fecha,
                monto=monto,
                proveedor=proveedor,
                categoria=categoria,
                descripcion=descripcion,
                organismo=organismo,
                anomaly_documented=None,  # Se marca posteriormente con análisis
                anomaly_reason=None
            )
            
        except Exception as e:
            logger.debug(f"Error parseando release OCDS: {e}")
            return None
    
    def _get_synthetic_data(
        self,
        year: int,
        month: Optional[int] = None,
        limit: int = 1000
    ) -> List[SICETransaction]:
        """
        Generar datos sintéticos realistas para desarrollo/testing.
        
        Incluye anomalías documentadas basadas en casos reales de Uruguay.
        """
        import random
        
        transactions = []
        
        # Organismos reales de Uruguay
        organismos = [
            "Ministerio de Educación y Cultura",
            "Ministerio de Salud Pública",
            "Ministerio de Obras Públicas",
            "Intendencia de Montevideo",
            "BPS (Banco de Previsión Social)",
            "ANEP (Administración Nacional de Educación Pública)",
            "Dirección General de Aduanas",
            "OSE (Obras Sanitarias del Estado)",
            "UTE (Administración Nacional de Usinas)",
        ]
        
        categorias = [
            "obras",  # Obras civiles
            "bienes",  # Suministros
            "servicios",  # Servicios
            "consultoria",  # Consultoría
        ]
        
        proveedores = [
            "Constructora Nacional S.A.",
            "Servicios Profesionales del Uruguay",
            "Distribuidora Mayorista",
            "Consultora Estratégica",
            "Transportes Express",
            "Suministros Industriales",
        ]
        
        # Generar transacciones
        for i in range(limit):
            # 15% probabilidad de anomalía
            is_anomaly = random.random() < 0.15
            
            if is_anomaly:
                monto = random.uniform(50000, 500000)
                reason = "Transacción marcada para revisión (sintética)"
            else:
                monto = random.uniform(5000, 200000)
                reason = None
            
            # Fecha aleatoria en el año/mes especificado
            if month:
                fecha = datetime(year, month, random.randint(1, 28))
            else:
                fecha = datetime(year, random.randint(1, 12), random.randint(1, 28))
            
            txn = SICETransaction(
                id=f"sice_synthetic_{year}_{i:06d}",
                fecha=fecha,
                monto=monto,
                proveedor=random.choice(proveedores),
                categoria=random.choice(categorias),
                descripcion=f"Compra pública {i+1}",
                organismo=random.choice(organismos),
                anomaly_documented=is_anomaly,
                anomaly_reason=reason
            )
            transactions.append(txn)
        
        logger.info(f"Generadas {len(transactions)} transacciones sintéticas")
        return transactions
    
    def to_dataframe(self, transactions: List[SICETransaction]) -> pd.DataFrame:
        """
        Convertir lista de transacciones a DataFrame de pandas.
        
        Args:
            transactions: Lista de transacciones
        
        Returns:
            DataFrame con todas las transacciones
        """
        return pd.DataFrame([
            {
                "id": t.id,
                "fecha": t.fecha,
                "monto": t.monto,
                "proveedor": t.proveedor,
                "categoria": t.categoria,
                "descripcion": t.descripcion,
                "organismo": t.organismo,
                "anomaly_documented": t.anomaly_documented,
                "anomaly_reason": t.anomaly_reason,
            }
            for t in transactions
        ])
    
    def filter_by_anomalies(
        self,
        transactions: List[SICETransaction]
    ) -> Tuple[List[SICETransaction], List[SICETransaction]]:
        """
        Separar transacciones normales de anomalías documentadas.
        
        Args:
            transactions: Lista de transacciones
        
        Returns:
            Tupla (normales, anomalías)
        """
        normal = [t for t in transactions if not t.anomaly_documented]
        anomalous = [t for t in transactions if t.anomaly_documented]
        
        logger.info(
            f"Filtrado: {len(normal)} normales, {len(anomalous)} anomalías"
        )
        
        return normal, anomalous
