from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Producto(Base):
    """Modelo para productos (combustibles, servicios, índices)"""

    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    categoria = Column(String(50), nullable=False)  # 'combustible', 'servicio', 'indice'
    unidad = Column(String(20), nullable=False)  # 'litro', 'pesos', 'porcentaje'
    activo = Column(Boolean, default=True)

    # Relaciones
    precios = relationship("Precio", back_populates="producto", cascade="all, delete-orphan")


class Precio(Base):
    """Modelo para precios históricos"""

    __tablename__ = "precios"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    valor = Column(Numeric(10, 2), nullable=False)
    fuente = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    producto = relationship("Producto", back_populates="precios")

    # Constraint único para evitar duplicados
    __table_args__ = (UniqueConstraint("producto_id", "fecha", name="_producto_fecha_uc"),)
