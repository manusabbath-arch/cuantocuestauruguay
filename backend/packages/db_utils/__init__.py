"""
DB Utils - Utilidades compartidas para operaciones de base de datos.

Proporciona:
- Helpers de SQLAlchemy
- Validadores de datos
- Utilidades de bulk insert/update
"""

from .helpers import BulkInserter, validate_unique_constraint

__all__ = ["BulkInserter", "validate_unique_constraint"]
