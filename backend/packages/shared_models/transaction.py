"""
Modelo común de transacción de gasto público.

Usado por:
- App de gastos públicos
- App de transparencia
- Bot fiscalizador
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Transaction:
    """
    Transacción de gasto público.
    
    Modelo común compartido entre todas las apps que manejan
    gastos públicos o compras del Estado.
    """
    
    # Identificación
    transaction_id: str
    
    # Montos
    monto: Decimal
    moneda: str = "UYU"
    
    # Partes involucradas
    proveedor: str = ""
    entidad: str = ""  # Entidad del Estado que realiza el gasto
    
    # Clasificación
    categoria: str = ""
    descripcion: str = ""
    
    # Temporal
    fecha: datetime = field(default_factory=datetime.now)
    
    # Metadata
    fuente: str = ""  # "SICE", "MEF", "catalogodatos", etc.
    
    # Análisis de anomalías
    is_anomaly: Optional[bool] = None
    anomaly_reason: Optional[str] = None
    anomaly_score: Optional[float] = None  # 0.0 - 1.0
    
    # Evidencia
    evidence_source: Optional[str] = None  # "documentado", "sospecha", etc.
    url_comprobante: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario."""
        return {
            "transaction_id": self.transaction_id,
            "monto": float(self.monto),
            "moneda": self.moneda,
            "proveedor": self.proveedor,
            "entidad": self.entidad,
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat(),
            "fuente": self.fuente,
            "is_anomaly": self.is_anomaly,
            "anomaly_reason": self.anomaly_reason,
            "anomaly_score": self.anomaly_score,
            "evidence_source": self.evidence_source,
            "url_comprobante": self.url_comprobante,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Crear desde diccionario."""
        # Convertir fecha si es string
        if isinstance(data.get("fecha"), str):
            data["fecha"] = datetime.fromisoformat(data["fecha"])
        
        # Convertir monto a Decimal
        if "monto" in data:
            data["monto"] = Decimal(str(data["monto"]))
        
        return cls(**data)
    
    def is_high_value(self, threshold: Decimal = Decimal("1000000")) -> bool:
        """
        Determinar si es una transacción de alto valor.
        
        Args:
            threshold: Umbral en pesos uruguayos (default: $1M UYU)
        
        Returns:
            True si supera el umbral
        """
        return self.monto >= threshold
    
    def flagged_for_review(self) -> bool:
        """
        Determinar si debe ser revisada manualmente.
        
        Returns:
            True si es anomalía o alto valor
        """
        return self.is_anomaly or self.is_high_value()
