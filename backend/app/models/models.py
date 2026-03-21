from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
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


class EjecucionPresupuestal(Base):
    """Ejecución presupuestal por organismo (inciso) extraída del MEF / CKAN."""

    __tablename__ = "ejecucion_presupuestal"

    id = Column(Integer, primary_key=True, index=True)
    anio = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=True)  # None = total anual
    inciso = Column(String(10), nullable=False)  # Código interno MEF (ej. "02")
    nombre_organismo = Column(String(200), nullable=False)
    credito_vigente = Column(Numeric(18, 2), nullable=False)
    ejecutado = Column(Numeric(18, 2), nullable=False)
    fuente = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("anio", "mes", "inciso", name="_ejecucion_anio_mes_inciso_uc"),)

    @hybrid_property
    def porcentaje_ejecucion(self):
        if self.credito_vigente and self.credito_vigente != 0:
            return round(float(self.ejecutado) / float(self.credito_vigente) * 100, 2)
        return None
