# Make models accessible from app.models
from .models import Producto, Precio, Alerta
from .schemas import (
    ProductoBase, ProductoCreate, ProductoResponse,
    PrecioBase, PrecioCreate, PrecioResponse, PrecioConProducto,
    VariacionResponse, ComparacionResponse, ComparacionItem,
    AlertaBase, AlertaCreate, AlertaResponse
)

__all__ = [
    "Producto", "Precio", "Alerta",
    "ProductoBase", "ProductoCreate", "ProductoResponse",
    "PrecioBase", "PrecioCreate", "PrecioResponse", "PrecioConProducto",
    "VariacionResponse", "ComparacionResponse", "ComparacionItem",
    "AlertaBase", "AlertaCreate", "AlertaResponse"
]
