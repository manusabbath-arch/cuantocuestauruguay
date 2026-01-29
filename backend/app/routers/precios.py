from datetime import date, datetime, timedelta
from decimal import Decimal
from time import time
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Precio, Producto
from app.models.schemas import (
    ComparacionItem,
    ComparacionResponse,
    PrecioConProducto,
    PrecioResponse,
    ProductoResponse,
    VariacionResponse,
)

router = APIRouter(prefix="/api/v1", tags=["precios"])

# Cache simple en memoria con TTL (segundos)
_CACHE: dict[str, tuple[float, Any]] = {}

# Mapeo de categorías cortas a categorías completas
CATEGORIA_MAP = {
    "electricidad": "Servicios Públicos - Electricidad",
    "agua": "Servicios Públicos - Agua",
    "telecomunicaciones": "Servicios Públicos - Telecomunicaciones",
    "combustibles": "Combustibles",
}


def _cache_get(key: str):
    now = time()
    item = _CACHE.get(key)
    if not item:
        return None
    expiry, value = item
    if expiry < now:
        _CACHE.pop(key, None)
        return None
    return value


def _cache_set(key: str, value, ttl: int = 600):
    _CACHE[key] = (time() + ttl, value)


@router.get("/productos", response_model=List[ProductoResponse])
async def listar_productos(categoria: Optional[str] = None, activo: bool = True, db: Session = Depends(get_db)):
    """Lista todos los productos disponibles"""
    cache_key = f"productos:{categoria}:{activo}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    query = db.query(Producto).filter(Producto.activo == activo)

    if categoria:
        # Map short category names to full names
        categoria_full = CATEGORIA_MAP.get(categoria.lower(), categoria)
        query = query.filter(Producto.categoria == categoria_full)

    productos = query.all()
    _cache_set(cache_key, productos, ttl=600)
    return productos


@router.get("/productos/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtiene un producto específico"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return producto


@router.get("/precios/{producto_id}", response_model=List[PrecioResponse])
async def obtener_precios(
    producto_id: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    """Obtiene serie histórica de precios para un producto"""
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Construir query
    query = db.query(Precio).filter(Precio.producto_id == producto_id)

    if fecha_desde:
        query = query.filter(Precio.fecha >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Precio.fecha <= fecha_hasta)

    # Ordenar por fecha descendente y limitar resultados
    precios = query.order_by(desc(Precio.fecha)).limit(limit).all()

    return precios


@router.get("/precios/{producto_id}/ultimo", response_model=PrecioResponse)
async def obtener_ultimo_precio(producto_id: int, db: Session = Depends(get_db)):
    """Obtiene el precio más reciente de un producto"""
    cache_key = f"ultimo:{producto_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    precio = db.query(Precio).filter(Precio.producto_id == producto_id).order_by(desc(Precio.fecha)).first()

    if not precio:
        raise HTTPException(status_code=404, detail="No hay precios disponibles para este producto")

    _cache_set(cache_key, precio, ttl=600)
    return precio


@router.get("/variacion/{producto_id}", response_model=VariacionResponse)
async def calcular_variacion(
    producto_id: int, periodo: str = Query("mes", regex="^(dia|semana|mes|año)$"), db: Session = Depends(get_db)
):
    """Calcula variación porcentual de precio en un periodo"""
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Obtener precio actual (más reciente)
    precio_actual = db.query(Precio).filter(Precio.producto_id == producto_id).order_by(desc(Precio.fecha)).first()

    if not precio_actual:
        raise HTTPException(status_code=404, detail="No hay precios disponibles")

    # Calcular fecha de referencia según el periodo
    fecha_referencia = precio_actual.fecha
    if periodo == "dia":
        fecha_referencia = fecha_referencia - timedelta(days=1)
    elif periodo == "semana":
        fecha_referencia = fecha_referencia - timedelta(days=7)
    elif periodo == "mes":
        fecha_referencia = fecha_referencia - timedelta(days=30)
    elif periodo == "año":
        fecha_referencia = fecha_referencia - timedelta(days=365)

    # Obtener precio anterior más cercano a la fecha de referencia
    precio_anterior = (
        db.query(Precio)
        .filter(Precio.producto_id == producto_id, Precio.fecha <= fecha_referencia)
        .order_by(desc(Precio.fecha))
        .first()
    )

    if not precio_anterior:
        raise HTTPException(
            status_code=404, detail=f"No hay datos históricos suficientes para calcular variación de {periodo}"
        )

    # Calcular variaciones
    variacion_absoluta = precio_actual.valor - precio_anterior.valor
    variacion_porcentual = (variacion_absoluta / precio_anterior.valor) * 100

    return VariacionResponse(
        producto_id=producto_id,
        nombre_producto=producto.nombre,
        precio_actual=precio_actual.valor,
        precio_anterior=precio_anterior.valor,
        variacion_absoluta=variacion_absoluta,
        variacion_porcentual=variacion_porcentual,
        fecha_actual=precio_actual.fecha,
        fecha_anterior=precio_anterior.fecha,
    )


@router.get("/comparar", response_model=ComparacionResponse)
async def comparar_productos(
    producto_ids: str = Query(..., description="IDs de productos separados por comas, ej: 1,2,3"),
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Compara múltiples productos en un rango de fechas"""
    cache_key = f"comparar:{producto_ids}:{fecha_desde}:{fecha_hasta}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    # Parsear IDs
    try:
        ids = [int(id.strip()) for id in producto_ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs de productos inválidos")

    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Máximo 10 productos para comparar")

    # Obtener productos
    productos = db.query(Producto).filter(Producto.id.in_(ids)).all()

    if len(productos) != len(ids):
        raise HTTPException(status_code=404, detail="Algunos productos no fueron encontrados")

    # Obtener precios para todos los productos
    query = db.query(Precio).filter(Precio.producto_id.in_(ids))

    if fecha_desde:
        query = query.filter(Precio.fecha >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Precio.fecha <= fecha_hasta)

    precios = query.order_by(Precio.fecha).all()

    # Organizar datos por fecha
    datos_por_fecha = {}
    for precio in precios:
        fecha_key = precio.fecha
        if fecha_key not in datos_por_fecha:
            datos_por_fecha[fecha_key] = {}
        datos_por_fecha[fecha_key][precio.producto_id] = float(precio.valor)

    # Convertir a lista de ComparacionItem
    datos = [ComparacionItem(fecha=fecha, valores=valores) for fecha, valores in sorted(datos_por_fecha.items())]

    result = ComparacionResponse(productos=productos, datos=datos)
    _cache_set(cache_key, result, ttl=900)
    return result


@router.get("/estadisticas/{producto_id}")
async def obtener_estadisticas(
    producto_id: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Obtiene estadísticas de un producto (min, max, promedio)"""
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Construir query
    query = db.query(
        func.min(Precio.valor).label("minimo"),
        func.max(Precio.valor).label("maximo"),
        func.avg(Precio.valor).label("promedio"),
        func.count(Precio.id).label("cantidad"),
    ).filter(Precio.producto_id == producto_id)

    if fecha_desde:
        query = query.filter(Precio.fecha >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Precio.fecha <= fecha_hasta)

    result = query.first()

    if not result or result.cantidad == 0:
        raise HTTPException(status_code=404, detail="No hay datos disponibles")

    return {
        "producto_id": producto_id,
        "nombre_producto": producto.nombre,
        "minimo": float(result.minimo) if result.minimo else None,
        "maximo": float(result.maximo) if result.maximo else None,
        "promedio": float(result.promedio) if result.promedio else None,
        "cantidad_registros": result.cantidad,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }
