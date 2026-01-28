"""
Cliente CKAN para acceso a catalogodatos.gub.uy.

Proporciona métodos para:
- Buscar datasets
- Obtener metadatos de datasets
- Descargar recursos (CSV, JSON, etc.)
"""

import logging
import requests
from typing import Optional, Dict, Any, List
import pandas as pd
from io import StringIO

logger = logging.getLogger(__name__)


class CKANClient:
    """
    Cliente para API CKAN de catalogodatos.gub.uy.
    
    Ejemplo:
        client = CKANClient()
        
        # Buscar datasets
        datasets = client.search_datasets("combustibles")
        
        # Obtener dataset específico
        dataset = client.get_dataset("precios-de-combustibles")
        
        # Descargar recurso como DataFrame
        df = client.fetch_resource_as_df("resource-id-123")
    """
    
    BASE_URL = "https://catalogodatos.gub.uy"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Inicializar cliente CKAN.
        
        Args:
            api_key: API key para autenticación (opcional)
            timeout: Timeout en segundos para requests
        """
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                "Authorization": api_key,
                "User-Agent": "CuantoCuestaUruguay/1.0"
            })
        else:
            self.session.headers.update({
                "User-Agent": "CuantoCuestaUruguay/1.0"
            })
    
    def _make_request(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Hacer request a la API CKAN.
        
        Args:
            action: Acción de la API (ej: "package_search")
            params: Parámetros del request
        
        Returns:
            Respuesta JSON de la API
        
        Raises:
            requests.HTTPError: Si el request falla
        """
        url = f"{self.BASE_URL}/api/3/action/{action}"
        
        try:
            response = self.session.get(url, params=params or {}, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("success"):
                error_msg = data.get("error", {}).get("message", "Unknown error")
                raise Exception(f"CKAN API error: {error_msg}")
            
            return data["result"]
            
        except requests.RequestException as e:
            logger.error(f"Error en request a CKAN: {e}")
            raise
    
    def search_datasets(self, query: str, rows: int = 10, start: int = 0) -> List[Dict[str, Any]]:
        """
        Buscar datasets por palabra clave.
        
        Args:
            query: Término de búsqueda
            rows: Número de resultados a retornar
            start: Offset para paginación
        
        Returns:
            Lista de datasets encontrados
        """
        logger.info(f"Buscando datasets: '{query}'")
        
        params = {
            "q": query,
            "rows": rows,
            "start": start
        }
        
        result = self._make_request("package_search", params)
        datasets = result.get("results", [])
        
        logger.info(f"Encontrados {len(datasets)} datasets")
        return datasets
    
    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Obtener metadatos de un dataset específico.
        
        Args:
            dataset_id: ID o nombre del dataset
        
        Returns:
            Metadatos del dataset
        """
        logger.info(f"Obteniendo dataset: {dataset_id}")
        
        params = {"id": dataset_id}
        dataset = self._make_request("package_show", params)
        
        return dataset
    
    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """
        Obtener metadatos de un recurso específico.
        
        Args:
            resource_id: ID del recurso
        
        Returns:
            Metadatos del recurso
        """
        logger.info(f"Obteniendo recurso: {resource_id}")
        
        params = {"id": resource_id}
        resource = self._make_request("resource_show", params)
        
        return resource
    
    def fetch_resource_as_df(
        self,
        resource_id: str,
        format_hint: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Descargar recurso como DataFrame de pandas.
        
        Args:
            resource_id: ID del recurso
            format_hint: Formato del archivo ("csv", "json", etc.)
        
        Returns:
            DataFrame con los datos del recurso
        
        Raises:
            Exception: Si el formato no es soportado
        """
        logger.info(f"Descargando recurso {resource_id} como DataFrame")
        
        # Obtener metadatos del recurso
        resource = self.get_resource(resource_id)
        url = resource.get("url")
        
        if not url:
            raise ValueError(f"Recurso {resource_id} no tiene URL")
        
        # Determinar formato
        format_type = format_hint or resource.get("format", "").lower()
        
        # Descargar datos
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        # Parsear según formato
        if format_type in ["csv", "text/csv"]:
            # Manejo robusto de CSV: BOM + delimitador automático
            # 1) Intento con autodetección de separador y BOM
            try:
                from io import BytesIO
                df = pd.read_csv(
                    BytesIO(response.content),
                    sep=None,  # autodetecta delimitador (incluye ';')
                    engine="python",
                    encoding="utf-8-sig",  # elimina BOM si existe
                )
            except Exception:
                # 2) Fallback explícito a ';' por datasets uruguayos
                try:
                    from io import BytesIO
                    df = pd.read_csv(
                        BytesIO(response.content),
                        sep=";",
                        engine="python",
                        encoding="utf-8-sig",
                    )
                except Exception as e:
                    logger.error(f"Error parseando CSV: {e}")
                    raise
        elif format_type in ["json", "application/json"]:
            df = pd.read_json(StringIO(response.text))
        else:
            raise Exception(
                f"Formato no soportado: {format_type}. "
                "Use format_hint='csv' o 'json'"
            )
        
        logger.info(f"DataFrame cargado: {len(df)} filas, {len(df.columns)} columnas")
        return df
    
    def list_datasets_by_organization(
        self,
        organization: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Listar todos los datasets de una organización.
        
        Args:
            organization: Nombre de la organización
            limit: Límite de datasets a retornar
        
        Returns:
            Lista de datasets de la organización
        """
        logger.info(f"Listando datasets de: {organization}")
        
        params = {
            "id": organization,
            "include_datasets": True
        }
        
        result = self._make_request("organization_show", params)
        datasets = result.get("packages", [])[:limit]
        
        logger.info(f"Encontrados {len(datasets)} datasets de {organization}")
        return datasets
