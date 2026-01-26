"""
Modelos de datos compartidos entre apps.

Proporciona:
- Transaction: Modelo común de transacción de gasto público
- ETLRun: Metadata de ejecuciones ETL
"""

from .transaction import Transaction
from .etl_run import ETLRun

__all__ = ["Transaction", "ETLRun"]
