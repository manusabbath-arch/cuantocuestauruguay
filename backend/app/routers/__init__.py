# Routers package initialization
from .etl import router as etl_router
from .facturas import router as facturas_router
from .gasto import router as gasto_router
from .precios import router as precios_router

__all__ = ["precios_router", "etl_router", "facturas_router", "gasto_router"]
