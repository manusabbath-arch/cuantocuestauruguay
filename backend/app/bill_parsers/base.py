"""Base types for bill parsing."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class BillData:
    """Normalized bill data returned by all parsers."""

    servicio: str  # "UTE", "OSE", "ANTEL"
    periodo_desde: date
    periodo_hasta: date
    consumo: float  # kWh, m3, or GB depending on service
    consumo_unidad: str  # "kWh", "m3", "GB"
    cargo_fijo: float  # Fixed charges in UYU
    cargo_variable: float  # Variable charges in UYU
    total: float  # Total bill amount in UYU
    tarifa_tipo: str  # e.g. "Residencial Simple", "Doble Horario"
    detalles: dict = field(default_factory=dict)  # Service-specific extras
    precio_unitario: float = 0.0  # Computed: cargo_variable / consumo
    costo_diario: float = 0.0  # Computed: total / days in period


@dataclass
class Recomendacion:
    """A single recommendation for the user."""

    tipo: str  # "cambio_tarifa", "reduccion_consumo", "informativo"
    titulo: str
    descripcion: str
    ahorro_estimado: Optional[float] = None  # UYU/month, None if not quantifiable


@dataclass
class BillAnalysis:
    """Complete analysis result for a bill."""

    bill: BillData
    comparacion_tarifa_oficial: dict
    percentil_consumo: Optional[int]  # 0-100, where user falls vs averages
    recomendaciones: list  # list of Recomendacion
    ahorro_potencial: float  # Total estimated savings in UYU/month
