"""
ETL de combustibles - Versión refactorizada usando packages compartidos.

Este archivo muestra cómo migrar el ETL actual para usar:
- ETLBase: Clase base común
- CKANClient: Cliente compartido para catalogodatos.gub.uy

Comparar con: app/etl/combustibles.py (versión original)
"""

import logging

# Imports desde packages compartidos
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Imports de la app
from app.core.config import settings
from app.models.models import Precio, Producto
from packages.ckan_client import CKANClient
from packages.etl_core import ETLBase

logger = logging.getLogger(__name__)


class CombustiblesETLv2(ETLBase):
    """
    ETL para datos de combustibles desde CKAN API.

    Versión 2: Refactorizada para usar paquetes compartidos.

    Mejoras vs versión original:
    - Hereda de ETLBase (patrón común)
    - Usa CKANClient (reutilizable)
    - Logging automático
    - Mejor manejo de errores
    - Métricas de ejecución
    """

    # Mapeo de nombres de productos de CKAN a nombres legibles
    PRODUCTOS_MAP = {
        "NAFTA_PREMIUM": "Nafta Premium 97",
        "NAFTA_SUPER": "Nafta Súper 95",
        "GASOIL_50S": "Gasoil 50-S",
        "GASOIL": "Gasoil Común",
        "SUPERGAS": "Supergás",
    }

    def __init__(self, db: Session):
        """
        Inicializar ETL de combustibles.

        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        super().__init__(name="combustibles", db_session=db)
        self.ckan = CKANClient()
        self.resource_id = settings.CKAN_COMBUSTIBLES_RESOURCE_ID

    def extract(self) -> pd.DataFrame:
        """
        Extraer datos de ANCAP vía CKAN API.

        Returns:
            DataFrame con datos crudos de combustibles

        Raises:
            Exception: Si falla la extracción
        """
        self.logger.info(f"Extrayendo datos del recurso: {self.resource_id}")

        try:
            # Usar cliente CKAN compartido
            df = self.ckan.fetch_resource_as_df(resource_id=self.resource_id, format_hint="csv")

            if df.empty:
                raise Exception("Dataset vacío recibido de CKAN")

            self.logger.info(f"Extraídos {len(df)} registros")
            return df

        except Exception as e:
            self.logger.error(f"Error en extracción: {e}")
            raise

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Limpiar y transformar datos de combustibles.

        Args:
            data: DataFrame con datos crudos

        Returns:
            DataFrame transformado y limpio

        Raises:
            ValueError: Si faltan columnas requeridas
        """
        self.logger.info("Transformando datos de combustibles")

        # Normalizar nombres de columnas
        data.columns = data.columns.str.lower().str.strip()

        self.logger.debug(f"Columnas disponibles: {data.columns.tolist()}")

        # Detectar columna de fecha
        fecha_col = self._detect_fecha_column(data.columns.tolist())
        if not fecha_col:
            raise ValueError(f"No se encontró columna de fecha. Columnas: {data.columns.tolist()}")

        # Convertir fechas
        data = self._parse_fechas(data, fecha_col)

        # Eliminar filas con fechas inválidas
        before_count = len(data)
        data = data.dropna(subset=["fecha"])
        after_count = len(data)

        if before_count > after_count:
            self.logger.warning(f"Eliminadas {before_count - after_count} filas con fechas inválidas")

        # Convertir fecha a date
        data["fecha"] = data["fecha"].dt.date

        self.logger.info(f"Transformados {len(data)} registros")
        return data

    def load(self, data: pd.DataFrame) -> None:
        """
        Cargar datos a PostgreSQL con deduplicación inteligente.

        Estrategia:
        1. Detectar producto por fila (PRODUCTOS_MAP)
        2. Verificar si ya existe (producto_id, fecha)
        3. Si existe y precio diferente → actualizar
        4. Si existe y precio igual → skip
        5. Si no existe → insertar

        Args:
            data: DataFrame con datos procesados

        Raises:
            Exception: Si falla la carga
        """
        self.logger.info("Cargando datos a PostgreSQL con deduplicación")

        # Asegurar que productos existen
        self._ensure_productos()

        loaded_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        items_to_insert = []

        for _, row in data.iterrows():
            try:
                # Buscar producto correspondiente
                producto = self._find_producto_for_row(row)

                if not producto:
                    self.logger.debug(f"No se encontró producto para fila: {row.to_dict()}")
                    failed_count += 1
                    continue

                if "fecha" not in row or pd.isna(row["fecha"]):
                    self.logger.debug(f"Fila sin fecha válida: {row.to_dict()}")
                    failed_count += 1
                    continue

                precio_valor = self._extract_precio_valor(row)
                fecha = row["fecha"]

                # Verificar si ya existe
                existing = (
                    self.db_session.query(Precio)
                    .filter(Precio.producto_id == producto.id, Precio.fecha == fecha)
                    .first()
                )

                if existing:
                    # Comparar valores (para detectar actualizaciones)
                    if abs(float(existing.valor) - float(precio_valor)) > 0.01:
                        # Actualizar si el precio cambió (revisión)
                        existing.valor = precio_valor
                        self.db_session.add(existing)
                        updated_count += 1
                        self.logger.debug(
                            f"Actualizado precio para {producto.nombre} en {fecha}: "
                            f"{existing.valor} → {precio_valor}"
                        )
                    else:
                        skipped_count += 1
                else:
                    # Guardar para insertar después
                    items_to_insert.append(
                        {
                            "producto_id": producto.id,
                            "fecha": fecha,
                            "valor": precio_valor,
                        }
                    )
                    loaded_count += 1

            except Exception as e:
                self.logger.error(f"Error procesando fila: {e}")
                failed_count += 1
                continue

        # Insertar nuevos precios
        for item in items_to_insert:
            try:
                nuevo_precio = Precio(
                    producto_id=item["producto_id"],
                    fecha=item["fecha"],
                    valor=item["valor"],
                    fuente="CKAN - catalogodatos.gub.uy",
                )
                self.db_session.add(nuevo_precio)
            except Exception as e:
                self.logger.error(f"Error preparando precio: {e}")
                failed_count += 1
                loaded_count -= 1

        # Commit de cambios
        try:
            self.db_session.commit()
            self.logger.info(
                f"Carga completada: {loaded_count} insertados, "
                f"{updated_count} actualizados, {skipped_count} duplicados, {failed_count} errores"
            )
        except Exception as e:
            self.db_session.rollback()
            # Reintentar con manejo individual
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                self.logger.warning(f"Conflicto de constraint detectado. Procesando con deduplicación individual...")
                successful = 0
                for item in items_to_insert:
                    try:
                        # Verificar nuevamente
                        existing = (
                            self.db_session.query(Precio)
                            .filter(Precio.producto_id == item["producto_id"], Precio.fecha == item["fecha"])
                            .first()
                        )
                        if not existing:
                            nuevo_precio = Precio(
                                producto_id=item["producto_id"],
                                fecha=item["fecha"],
                                valor=item["valor"],
                                fuente="CKAN - catalogodatos.gub.uy",
                            )
                            self.db_session.add(nuevo_precio)
                            self.db_session.commit()
                            successful += 1
                    except:
                        self.db_session.rollback()
                        continue

                self.logger.info(f"Recuperación: {successful} registros insertados exitosamente")
            else:
                raise

    # Métodos auxiliares

    def _detect_fecha_column(self, columns: list[str]) -> Optional[str]:
        """
        Detectar columna de fecha en el dataset.

        Args:
            columns: Lista de nombres de columnas

        Returns:
            Nombre de la columna de fecha o None
        """
        # Incluir variantes comunes en datasets locales: 'año-mes', 'ano-mes', 'año_mes'
        fecha_candidates = [
            "periodo",
            "fecha",
            "date",
            "mes",
            "month",
            "año-mes",
            "ano-mes",
            "año_mes",
            "ano_mes",
        ]

        for col in fecha_candidates:
            if col in columns:
                self.logger.debug(f"Columna de fecha detectada: {col}")
                return col

        return None

    def _parse_fechas(self, data: pd.DataFrame, fecha_col: str) -> pd.DataFrame:
        """
        Parsear fechas con múltiples formatos.

        Args:
            data: DataFrame
            fecha_col: Nombre de la columna de fecha

        Returns:
            DataFrame con columna 'fecha' parseada
        """
        try:
            # Intentar formato año-mes primero
            data["fecha"] = pd.to_datetime(data[fecha_col], format="%Y-%m", errors="coerce")
            self.logger.debug("Fechas parseadas con formato '%Y-%m'")
        except:
            try:
                # Fallback: dejar que pandas infiera
                data["fecha"] = pd.to_datetime(data[fecha_col], errors="coerce")
                self.logger.debug("Fechas parseadas con inferencia automática")
            except Exception as e:
                raise ValueError(f"Error parseando fechas: {e}")

        return data

    def _ensure_productos(self) -> None:
        """
        Asegurar que todos los productos existan en la base de datos.
        """
        for nombre in self.PRODUCTOS_MAP.values():
            producto = self.db_session.query(Producto).filter(Producto.nombre == nombre).first()

            if not producto:
                nuevo_producto = Producto(nombre=nombre, categoria="Combustibles", unidad="litro")
                self.db_session.add(nuevo_producto)
                self.logger.info(f"Producto creado: {nombre}")

        self.db_session.commit()

    def _find_producto_for_row(self, row: pd.Series) -> Optional[Producto]:
        """
        Buscar producto correspondiente a una fila del dataset.

        Args:
            row: Fila del DataFrame

        Returns:
            Producto o None si no se encuentra
        """
        row_str = str(row).lower()

        for key, nombre in self.PRODUCTOS_MAP.items():
            if key.lower() in row_str:
                producto = self.db_session.query(Producto).filter(Producto.nombre == nombre).first()
                if producto:
                    return producto

        return None

    def _extract_precio_valor(self, row: pd.Series) -> float:
        """
        Extraer valor de precio desde una fila.
        Intenta múltiples nombres de columnas comunes.

        Args:
            row: Fila del DataFrame

        Returns:
            Valor numérico del precio

        Raises:
            ValueError: Si no se encuentra un valor de precio válido
        """
        # Nombres de columnas a probar (en orden de preferencia)
        # Incluye precioexplantauyu que es el campo actual en CKAN
        price_columns = ["precio", "precioexplantauyu", "valor", "price", "value", "monto", "importe"]

        for col in price_columns:
            if col in row.index and pd.notna(row[col]):
                try:
                    # Convertir strings con comas a puntos (formato uruguayo)
                    price_str = str(row[col]).replace(",", ".")
                    price_val = float(price_str)
                    # Rechazar precios negativos (errores en datos)
                    if price_val > 0:
                        return price_val
                except (ValueError, TypeError):
                    continue

        raise ValueError(f"No se encontró valor de precio válido en fila: {row.to_dict()}")


# Ejemplo de uso
if __name__ == "__main__":
    from app.db.session import SessionLocal

    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear sesión de DB
    db = SessionLocal()

    try:
        # Ejecutar ETL
        etl = CombustiblesETLv2(db=db)
        result = etl.run()

        print("\n" + "=" * 50)
        print("RESULTADO DEL ETL")
        print("=" * 50)
        print(f"Éxito: {result['success']}")
        print(f"Registros procesados: {result['records_processed']}")
        print(f"Duración: {result['duration_seconds']:.2f}s")

        if result["errors"]:
            print(f"Errores: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"  - {error}")

    finally:
        db.close()
