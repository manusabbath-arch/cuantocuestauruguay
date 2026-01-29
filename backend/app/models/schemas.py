from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# Schemas para Producto
class ProductoBase(BaseModel):
    nombre: str
    categoria: str
    unidad: str
    activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True


# Schemas para Precio
class PrecioBase(BaseModel):
    producto_id: int
    fecha: date
    valor: Decimal
    fuente: Optional[str] = None


class PrecioCreate(PrecioBase):
    pass


class PrecioResponse(PrecioBase):
    id: int

    class Config:
        from_attributes = True


class PrecioConProducto(PrecioResponse):
    producto: ProductoResponse


# Schemas para variaciones
class VariacionResponse(BaseModel):
    producto_id: int
    nombre_producto: str
    precio_actual: Decimal
    precio_anterior: Decimal
    variacion_absoluta: Decimal
    variacion_porcentual: Decimal
    fecha_actual: date
    fecha_anterior: date


# Schemas para comparaciones
class ComparacionItem(BaseModel):
    fecha: date
    valores: dict  # {producto_id: valor}


class ComparacionResponse(BaseModel):
    productos: List[ProductoResponse]
    datos: List[ComparacionItem]


# Schemas para Alerta
class AlertaBase(BaseModel):
    email: str
    producto_id: int
    umbral_cambio: Decimal
    activo: bool = True


class AlertaCreate(AlertaBase):
    pass


class AlertaResponse(AlertaBase):
    id: int

    class Config:
        from_attributes = True
