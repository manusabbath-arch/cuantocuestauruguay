"""
ETL Core - Base común para todos los procesos ETL.

Proporciona:
- ETLBase: Clase abstracta para heredar en todos los ETL
- Validators: Validadores comunes de datos
- Extractors: Extractores genéricos (CSV, API, DB)
"""

from .base import ETLBase

__all__ = ["ETLBase"]
