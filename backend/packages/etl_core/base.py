"""
Clase base abstracta para todos los procesos ETL.

Establece un contrato común para:
- extract(): Extraer datos de fuente (API, CSV, DB)
- transform(): Transformar y limpiar datos
- load(): Cargar datos a base de datos
- run(): Orquestar el proceso completo
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class ETLBase(ABC):
    """
    Clase base abstracta para todos los ETL.
    
    Todas las clases ETL deben heredar de esta e implementar:
    - extract()
    - transform()
    - load()
    
    Ejemplo:
        class CombustiblesETL(ETLBase):
            def extract(self) -> pd.DataFrame:
                # Lógica de extracción
                pass
            
            def transform(self, data: pd.DataFrame) -> pd.DataFrame:
                # Lógica de transformación
                pass
            
            def load(self, data: pd.DataFrame) -> None:
                # Lógica de carga
                pass
    """
    
    def __init__(self, name: str, db_session: Optional[Any] = None):
        """
        Inicializar ETL.
        
        Args:
            name: Nombre descriptivo del ETL
            db_session: Sesión de base de datos (opcional)
        """
        self.name = name
        self.db_session = db_session
        self.logger = logging.getLogger(f"etl.{name}")
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.records_processed: int = 0
        self.errors: list[str] = []
    
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """
        Extraer datos de la fuente.
        
        Returns:
            DataFrame con datos extraídos
        
        Raises:
            Exception: Si falla la extracción
        """
        pass
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transformar y limpiar datos.
        
        Args:
            data: DataFrame con datos crudos
        
        Returns:
            DataFrame con datos transformados
        
        Raises:
            Exception: Si falla la transformación
        """
        pass
    
    @abstractmethod
    def load(self, data: pd.DataFrame) -> None:
        """
        Cargar datos a la base de datos.
        
        Args:
            data: DataFrame con datos procesados
        
        Raises:
            Exception: Si falla la carga
        """
        pass
    
    def run(self) -> dict[str, Any]:
        """
        Ejecutar el proceso ETL completo.
        
        Returns:
            Diccionario con estadísticas de ejecución:
            {
                "success": bool,
                "records_processed": int,
                "duration_seconds": float,
                "errors": list[str]
            }
        """
        self.start_time = datetime.now()
        self.logger.info(f"Iniciando ETL: {self.name}")
        
        try:
            # 1. Extract
            self.logger.info("Fase 1: Extracción")
            raw_data = self.extract()
            self.logger.info(f"Extraídos {len(raw_data)} registros")
            
            # 2. Transform
            self.logger.info("Fase 2: Transformación")
            clean_data = self.transform(raw_data)
            self.logger.info(f"Transformados {len(clean_data)} registros")
            
            # 3. Load
            self.logger.info("Fase 3: Carga")
            self.load(clean_data)
            self.records_processed = len(clean_data)
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            self.logger.info(
                f"ETL completado exitosamente: {self.records_processed} registros "
                f"en {duration:.2f}s"
            )
            
            return {
                "success": True,
                "records_processed": self.records_processed,
                "duration_seconds": duration,
                "errors": []
            }
            
        except Exception as e:
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            error_msg = f"Error en ETL {self.name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.errors.append(error_msg)
            
            return {
                "success": False,
                "records_processed": 0,
                "duration_seconds": duration,
                "errors": self.errors
            }
    
    def validate_data(self, data: pd.DataFrame, required_columns: list[str]) -> None:
        """
        Validar que el DataFrame tenga las columnas requeridas.
        
        Args:
            data: DataFrame a validar
            required_columns: Lista de columnas requeridas
        
        Raises:
            ValueError: Si faltan columnas requeridas
        """
        missing_cols = set(required_columns) - set(data.columns)
        if missing_cols:
            raise ValueError(
                f"Faltan columnas requeridas: {missing_cols}"
            )
