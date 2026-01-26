"""
Modelo para rastrear ejecuciones de ETL.

Permite auditar y monitorear todos los procesos ETL.
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum


class ETLStatus(str, Enum):
    """Estado de ejecución del ETL."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Completado con errores


@dataclass
class ETLRun:
    """
    Metadata de una ejecución ETL.
    
    Permite rastrear:
    - Cuándo se ejecutó
    - Cuánto duró
    - Cuántos registros procesó
    - Si tuvo errores
    """
    
    # Identificación
    etl_name: str
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    # Estado
    status: ETLStatus = ETLStatus.PENDING
    
    # Tiempos
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Resultados
    records_extracted: int = 0
    records_loaded: int = 0
    records_failed: int = 0
    
    # Errores
    errors: List[str] = field(default_factory=list)
    
    # Metadata adicional
    triggered_by: str = "manual"  # "manual", "scheduler", "api"
    
    def duration_seconds(self) -> Optional[float]:
        """Calcular duración en segundos."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def success_rate(self) -> float:
        """
        Calcular tasa de éxito.
        
        Returns:
            Porcentaje de registros cargados exitosamente (0.0 - 1.0)
        """
        total = self.records_extracted
        if total == 0:
            return 0.0
        return self.records_loaded / total
    
    def mark_as_success(self) -> None:
        """Marcar ejecución como exitosa."""
        self.status = ETLStatus.SUCCESS
        self.end_time = datetime.now()
    
    def mark_as_failed(self, error: str) -> None:
        """
        Marcar ejecución como fallida.
        
        Args:
            error: Mensaje de error
        """
        self.status = ETLStatus.FAILED
        self.end_time = datetime.now()
        self.errors.append(error)
    
    def mark_as_partial(self) -> None:
        """Marcar ejecución como parcialmente exitosa."""
        self.status = ETLStatus.PARTIAL
        self.end_time = datetime.now()
    
    def to_dict(self) -> dict:
        """Convertir a diccionario."""
        return {
            "etl_name": self.etl_name,
            "run_id": self.run_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds(),
            "records_extracted": self.records_extracted,
            "records_loaded": self.records_loaded,
            "records_failed": self.records_failed,
            "success_rate": self.success_rate(),
            "errors": self.errors,
            "triggered_by": self.triggered_by,
        }
