"""
SICE Client - Cliente para acceso a compras públicas de Uruguay.

Proporciona acceso a:
- Datos OCDS (Open Contracting Data Standard)
- Compras históricas del Estado uruguayo
- Dataset: catalogodatos.gub.uy
"""

from .client import SICEComprasClient, SICETransaction

__all__ = ["SICEComprasClient", "SICETransaction"]
