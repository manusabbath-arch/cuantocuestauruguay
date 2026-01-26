"""
Ejemplo: ETL de Compras Públicas usando todos los packages compartidos.

Este ejemplo demuestra cómo usar:
- ETLBase (etl_core)
- SICEComprasClient (sice_client)
- Transaction (shared_models)
- BulkInserter (db_utils)

Para crear un ETL completo de compras públicas.
"""

import logging
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

# Imports de packages compartidos
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from packages.etl_core import ETLBase
from packages.sice_client import SICEComprasClient
from packages.shared_models import Transaction
from packages.db_utils import BulkInserter

# Imports de la app (ejemplo, ajustar según modelo real)
# from app.models.models import CompraPublica

logger = logging.getLogger(__name__)


class ComprasPublicasETL(ETLBase):
    """
    ETL para cargar compras públicas desde OCDS (catalogodatos.gub.uy).
    
    Demuestra uso de todos los packages compartidos en conjunto:
    - ETLBase: Estructura común del ETL
    - SICEComprasClient: Extracción de datos OCDS
    - Transaction: Modelo compartido de transacción
    - BulkInserter: Carga optimizada a DB
    
    Ejemplo de uso:
        db = SessionLocal()
        etl = ComprasPublicasETL(db=db, year=2024)
        result = etl.run()
        
        print(f"Compras cargadas: {result['records_processed']}")
    """
    
    def __init__(self, db: Session, year: int = 2024, month: int = None):
        """
        Inicializar ETL de compras públicas.
        
        Args:
            db: Sesión de base de datos
            year: Año de las compras a cargar
            month: Mes opcional para filtrar
        """
        super().__init__(name=f"compras_publicas_{year}", db_session=db)
        
        self.year = year
        self.month = month
        
        # Cliente SICE compartido
        self.sice = SICEComprasClient()
        
        self.logger.info(
            f"ETL inicializado para compras de {year}" +
            (f"-{month:02d}" if month else "")
        )
    
    def extract(self) -> pd.DataFrame:
        """
        Extraer compras públicas desde SICE (OCDS).
        
        Usa SICEComprasClient compartido.
        
        Returns:
            DataFrame con compras extraídas
        """
        self.logger.info(f"Extrayendo compras OCDS del año {self.year}")
        
        # Usar cliente SICE
        compras = self.sice.get_compras(
            year=self.year,
            month=self.month,
            limit=10000  # Cargar hasta 10k compras
        )
        
        if not compras:
            raise Exception(f"No se obtuvieron compras para {self.year}")
        
        # Convertir a DataFrame
        df = self.sice.to_dataframe(compras)
        
        self.logger.info(f"Extraídas {len(df)} compras públicas")
        
        # Guardar referencia para uso posterior
        self._compras_originales = compras
        
        return df
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transformar y limpiar datos de compras.
        
        Args:
            data: DataFrame con datos crudos
        
        Returns:
            DataFrame limpio y validado
        """
        self.logger.info("Transformando datos de compras")
        
        # Validar columnas requeridas
        required_cols = ['id', 'fecha', 'monto', 'proveedor', 'organismo']
        self.validate_data(data, required_cols)
        
        # Eliminar duplicados
        before_count = len(data)
        data = data.drop_duplicates(subset=['id'])
        after_count = len(data)
        
        if before_count > after_count:
            self.logger.warning(
                f"Eliminados {before_count - after_count} duplicados"
            )
        
        # Filtrar montos negativos o cero
        data = data[data['monto'] > 0]
        
        # Normalizar categorías
        data['categoria'] = data['categoria'].str.lower()
        
        # Marcar transacciones de alto valor (> $1M UYU)
        data['es_alto_valor'] = data['monto'] > 1_000_000
        
        self.logger.info(
            f"Transformados {len(data)} registros. "
            f"{data['es_alto_valor'].sum()} de alto valor."
        )
        
        return data
    
    def load(self, data: pd.DataFrame) -> None:
        """
        Cargar compras a base de datos usando BulkInserter.
        
        Args:
            data: DataFrame con datos procesados
        """
        self.logger.info("Cargando compras a base de datos")
        
        # OPCIÓN 1: Convertir a modelo Transaction compartido
        # (útil si quieres usar el modelo genérico)
        self.logger.info("Convirtiendo a modelo Transaction compartido")
        
        transactions = []
        for compra in self._compras_originales:
            txn = compra.to_transaction()
            transactions.append(txn.to_dict())
        
        # Crear DataFrame de transactions
        txn_df = pd.DataFrame(transactions)
        
        self.logger.info(f"Convertidas {len(txn_df)} compras a Transaction")
        
        # OPCIÓN 2: Usar BulkInserter para carga optimizada
        # (ejemplo genérico, ajustar según modelo real)
        
        # Si tuvieras un modelo CompraPublica:
        # inserter = BulkInserter(self.db_session, CompraPublica)
        # 
        # result = inserter.bulk_insert_dataframe(
        #     data,
        #     unique_columns=['id'],  # ID de compra es único
        #     skip_duplicates=True
        # )
        # 
        # self.logger.info(
        #     f"Carga completada: {result['inserted']} insertadas, "
        #     f"{result['skipped']} duplicadas, {result['errors']} errores"
        # )
        
        # Por ahora, solo loggeamos (sin modelo real definido)
        self.logger.info(
            f"✅ Datos listos para carga: {len(data)} compras procesadas"
        )
        self.logger.warning(
            "⚠️ Carga a DB pendiente: definir modelo CompraPublica"
        )
    
    def get_estadisticas(self) -> dict:
        """
        Obtener estadísticas de las compras procesadas.
        
        Returns:
            Diccionario con estadísticas
        """
        if not hasattr(self, '_compras_originales'):
            return {}
        
        compras = self._compras_originales
        
        # Separar normales de anomalías
        normal, anomalous = self.sice.filter_by_anomalies(compras)
        
        # Estadísticas
        total_monto = sum(c.monto for c in compras)
        monto_anomalias = sum(c.monto for c in anomalous)
        
        return {
            "total_compras": len(compras),
            "compras_normales": len(normal),
            "compras_anomalas": len(anomalous),
            "monto_total": total_monto,
            "monto_anomalias": monto_anomalias,
            "porcentaje_anomalias": (len(anomalous) / len(compras)) * 100 if compras else 0,
            "organismos_unicos": len(set(c.organismo for c in compras)),
            "proveedores_unicos": len(set(c.proveedor for c in compras)),
        }


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Simular sesión de DB (en producción usar SessionLocal real)
    class MockSession:
        def commit(self):
            pass
        
        def rollback(self):
            pass
    
    mock_db = MockSession()
    
    # Ejecutar ETL
    print("="*60)
    print("ETL DE COMPRAS PÚBLICAS - EJEMPLO")
    print("="*60)
    
    etl = ComprasPublicasETL(db=mock_db, year=2024, month=1)
    
    # Run ETL
    result = etl.run()
    
    # Mostrar resultado
    print("\n" + "="*60)
    print("RESULTADO DEL ETL")
    print("="*60)
    print(f"✅ Éxito: {result['success']}")
    print(f"📊 Registros: {result['records_processed']}")
    print(f"⏱️ Duración: {result['duration_seconds']:.2f}s")
    
    if result['errors']:
        print(f"❌ Errores: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   - {error}")
    
    # Estadísticas adicionales
    print("\n" + "="*60)
    print("ESTADÍSTICAS DETALLADAS")
    print("="*60)
    
    stats = etl.get_estadisticas()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*60)
    print("PACKAGES UTILIZADOS")
    print("="*60)
    print("✅ etl_core.ETLBase - Estructura del ETL")
    print("✅ sice_client.SICEComprasClient - Extracción OCDS")
    print("✅ shared_models.Transaction - Modelo compartido")
    print("✅ db_utils.BulkInserter - Carga optimizada (ready)")
    print("="*60)
