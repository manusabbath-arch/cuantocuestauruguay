"""
Helpers de base de datos compartidos.

Proporciona utilidades comunes para operaciones con SQLAlchemy.
"""

import logging
from typing import List, Dict, Any, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
import pandas as pd

logger = logging.getLogger(__name__)


class BulkInserter:
    """
    Utilidad para inserción masiva optimizada con SQLAlchemy.
    
    Maneja:
    - Bulk insert eficiente
    - Detección de duplicados
    - Skip de registros existentes
    - Estadísticas de inserción
    
    Ejemplo:
        inserter = BulkInserter(session, Precio)
        
        data = [
            {"producto_id": 1, "fecha": "2024-01-01", "valor": 100},
            {"producto_id": 1, "fecha": "2024-01-02", "valor": 105},
        ]
        
        result = inserter.bulk_insert_dict(
            data,
            unique_columns=["producto_id", "fecha"]
        )
        
        print(f"Insertados: {result['inserted']}")
        print(f"Duplicados: {result['skipped']}")
    """
    
    def __init__(self, session: Session, model: Type):
        """
        Inicializar bulk inserter.
        
        Args:
            session: Sesión de SQLAlchemy
            model: Modelo de SQLAlchemy (clase)
        """
        self.session = session
        self.model = model
        self.table_name = model.__tablename__
    
    def bulk_insert_dict(
        self,
        data: List[Dict[str, Any]],
        unique_columns: Optional[List[str]] = None,
        skip_duplicates: bool = True
    ) -> Dict[str, int]:
        """
        Insertar múltiples registros desde diccionarios.
        
        Args:
            data: Lista de diccionarios con datos
            unique_columns: Columnas que definen unicidad
            skip_duplicates: Si True, omite duplicados. Si False, lanza error.
        
        Returns:
            Diccionario con estadísticas:
            {
                "inserted": int,
                "skipped": int,
                "errors": int
            }
        """
        inserted = 0
        skipped = 0
        errors = 0
        
        logger.info(f"Insertando {len(data)} registros en {self.table_name}")
        
        # Si hay unique_columns, verificar duplicados
        if unique_columns and skip_duplicates:
            data = self._filter_duplicates(data, unique_columns)
            skipped = len(data) - len(data)
        
        # Bulk insert
        try:
            if data:
                self.session.bulk_insert_mappings(self.model, data)
                self.session.commit()
                inserted = len(data)
                logger.info(f"Insertados {inserted} registros")
        
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Error de integridad en bulk insert: {e}")
            
            # Fallback: insertar uno por uno
            logger.info("Intentando inserción individual...")
            for record in data:
                try:
                    obj = self.model(**record)
                    self.session.add(obj)
                    self.session.commit()
                    inserted += 1
                except IntegrityError:
                    self.session.rollback()
                    skipped += 1
                except Exception as e:
                    self.session.rollback()
                    logger.error(f"Error insertando registro: {e}")
                    errors += 1
        
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error en bulk insert: {e}")
            errors = len(data)
        
        return {
            "inserted": inserted,
            "skipped": skipped,
            "errors": errors
        }
    
    def bulk_insert_dataframe(
        self,
        df: pd.DataFrame,
        unique_columns: Optional[List[str]] = None,
        skip_duplicates: bool = True
    ) -> Dict[str, int]:
        """
        Insertar desde DataFrame de pandas.
        
        Args:
            df: DataFrame con datos
            unique_columns: Columnas que definen unicidad
            skip_duplicates: Si True, omite duplicados
        
        Returns:
            Estadísticas de inserción
        """
        # Convertir DataFrame a lista de diccionarios
        data = df.to_dict('records')
        
        return self.bulk_insert_dict(data, unique_columns, skip_duplicates)
    
    def _filter_duplicates(
        self,
        data: List[Dict[str, Any]],
        unique_columns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filtrar registros que ya existen en la base de datos.
        
        Args:
            data: Lista de registros
            unique_columns: Columnas que definen unicidad
        
        Returns:
            Lista de registros no duplicados
        """
        # Construir valores únicos existentes
        existing_values = set()
        
        try:
            # Query para obtener valores existentes
            query = self.session.query(
                *[getattr(self.model, col) for col in unique_columns]
            )
            
            for row in query.all():
                key = tuple(row)
                existing_values.add(key)
        
        except Exception as e:
            logger.error(f"Error verificando duplicados: {e}")
            return data  # Retornar todo si falla
        
        # Filtrar duplicados
        unique_data = []
        for record in data:
            key = tuple(record.get(col) for col in unique_columns)
            if key not in existing_values:
                unique_data.append(record)
                existing_values.add(key)  # Agregar para evitar duplicados en el batch
        
        duplicates_count = len(data) - len(unique_data)
        if duplicates_count > 0:
            logger.info(f"Filtrados {duplicates_count} duplicados")
        
        return unique_data


def validate_unique_constraint(
    session: Session,
    model: Type,
    data: Dict[str, Any],
    unique_columns: List[str]
) -> bool:
    """
    Validar si un registro viola constraint de unicidad.
    
    Args:
        session: Sesión de SQLAlchemy
        model: Modelo a verificar
        data: Datos del registro
        unique_columns: Columnas que definen unicidad
    
    Returns:
        True si el registro ya existe (viola unicidad), False si no existe
    
    Ejemplo:
        existe = validate_unique_constraint(
            session,
            Precio,
            {"producto_id": 1, "fecha": "2024-01-01"},
            ["producto_id", "fecha"]
        )
        
        if existe:
            print("Registro duplicado, omitiendo...")
    """
    try:
        # Construir query con filtros
        query = session.query(model)
        
        for col in unique_columns:
            query = query.filter(getattr(model, col) == data[col])
        
        # Verificar si existe
        exists = session.query(query.exists()).scalar()
        return exists
    
    except Exception as e:
        logger.error(f"Error validando constraint: {e}")
        return False


def get_table_columns(model: Type) -> List[str]:
    """
    Obtener nombres de columnas de un modelo SQLAlchemy.
    
    Args:
        model: Modelo de SQLAlchemy
    
    Returns:
        Lista de nombres de columnas
    """
    mapper = inspect(model)
    return [col.key for col in mapper.columns]


def dataframe_to_model(
    df: pd.DataFrame,
    model: Type,
    column_mapping: Optional[Dict[str, str]] = None
) -> List:
    """
    Convertir DataFrame a lista de objetos de modelo SQLAlchemy.
    
    Args:
        df: DataFrame con datos
        model: Modelo de SQLAlchemy
        column_mapping: Mapeo de nombres de columnas (df -> model)
                       {"col_df": "col_model"}
    
    Returns:
        Lista de objetos del modelo
    
    Ejemplo:
        df = pd.DataFrame({
            "prod_id": [1, 2],
            "valor": [100, 200]
        })
        
        mapping = {"prod_id": "producto_id"}
        
        objects = dataframe_to_model(df, Precio, mapping)
    """
    # Aplicar mapeo de columnas
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    # Convertir a diccionarios
    records = df.to_dict('records')
    
    # Crear objetos del modelo
    objects = [model(**record) for record in records]
    
    return objects


def chunk_list(data: List, chunk_size: int = 1000) -> List[List]:
    """
    Dividir lista en chunks para procesamiento por lotes.
    
    Args:
        data: Lista a dividir
        chunk_size: Tamaño de cada chunk
    
    Returns:
        Lista de chunks
    
    Ejemplo:
        data = list(range(5000))
        chunks = chunk_list(data, chunk_size=1000)
        # chunks = [[0...999], [1000...1999], ...]
        
        for chunk in chunks:
            process_chunk(chunk)
    """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
