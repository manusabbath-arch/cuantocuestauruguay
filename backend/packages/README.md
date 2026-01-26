# Backend Packages - Código Compartido

Paquetes compartidos entre todas las apps del monorepo CuantoCuestaUruguay.

## Estructura

```
packages/
├── etl_core/           # Base común para ETL
├── ckan_client/        # Cliente para catalogodatos.gub.uy
├── sice_client/        # Cliente para compras públicas (OCDS)
├── db_utils/           # Utilidades de base de datos
└── shared_models/      # Modelos de datos compartidos
```

## 📦 etl_core

Base común para todos los procesos ETL (Extract, Transform, Load).

### Uso

```python
from packages.etl_core import ETLBase
import pandas as pd

class MiETL(ETLBase):
    def extract(self) -> pd.DataFrame:
        # Extraer datos de fuente
        return pd.read_csv("datos.csv")
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        # Limpiar y transformar
        data = data.dropna()
        data["precio"] = data["precio"].astype(float)
        return data
    
    def load(self, data: pd.DataFrame) -> None:
        # Cargar a base de datos
        data.to_sql("precios", self.db_session.bind, if_exists="append")

# Ejecutar
etl = MiETL(name="precios_combustibles", db_session=session)
result = etl.run()

print(result)
# {
#     "success": True,
#     "records_processed": 1234,
#     "duration_seconds": 5.6,
#     "errors": []
# }
```

### Métodos heredados

- `run()`: Ejecuta extract → transform → load
- `validate_data(df, required_columns)`: Valida columnas requeridas
- Logging automático de todas las fases

## 📦 ckan_client

Cliente para API de catalogodatos.gub.uy (datos abiertos del gobierno).

### Uso

```python
from packages.ckan_client import CKANClient

client = CKANClient()

# Buscar datasets
datasets = client.search_datasets("combustibles")
print(f"Encontrados: {len(datasets)} datasets")

# Obtener dataset específico
dataset = client.get_dataset("precios-de-combustibles")
print(dataset["title"])

# Descargar recurso como DataFrame
resource_id = dataset["resources"][0]["id"]
df = client.fetch_resource_as_df(resource_id)
print(df.head())
```

### Métodos principales

- `search_datasets(query)`: Buscar por palabra clave
- `get_dataset(dataset_id)`: Obtener metadatos de dataset
- `get_resource(resource_id)`: Obtener metadatos de recurso
- `fetch_resource_as_df(resource_id)`: Descargar como DataFrame
- `list_datasets_by_organization(org)`: Listar datasets de organización

## 📦 shared_models

Modelos de datos compartidos entre apps.

### Transaction

Modelo común de transacción de gasto público.

```python
from packages.shared_models import Transaction
from decimal import Decimal
from datetime import datetime

# Crear transacción
txn = Transaction(
    transaction_id="TXN-2024-001",
    monto=Decimal("150000.00"),
    moneda="UYU",
    proveedor="Empresa XYZ S.A.",
    entidad="Intendencia de Montevideo",
    categoria="Servicios de Limpieza",
    descripcion="Servicio de limpieza mensual",
    fecha=datetime.now(),
    fuente="SICE"
)

# Verificar si es alto valor
if txn.is_high_value():
    print("⚠️ Transacción de alto valor")

# Verificar si necesita revisión
if txn.flagged_for_review():
    print("🔍 Requiere revisión manual")

# Exportar a dict
data = txn.to_dict()
```

### ETLRun

Metadata de ejecuciones ETL para auditoría.

```python
from packages.shared_models import ETLRun, ETLStatus

# Crear registro de ejecución
run = ETLRun(
    etl_name="combustibles_etl",
    triggered_by="scheduler"
)

# Durante ejecución
run.status = ETLStatus.RUNNING
run.records_extracted = 1500

# Al finalizar
run.records_loaded = 1500
run.records_failed = 0
run.mark_as_success()

# Estadísticas
print(f"Duración: {run.duration_seconds()}s")
print(f"Tasa de éxito: {run.success_rate() * 100}%")

# Guardar en DB
session.add(ETLRunModel(**run.to_dict()))
session.commit()
```

## 🔧 Integración con Apps

### Ejemplo: Refactorizar ETL existente

**Antes (sin packages):**

```python
# app/etl/combustibles.py
def run_combustibles_etl():
    # Código todo junto
    data = requests.get("https://catalogodatos.gub.uy/...").json()
    df = pd.DataFrame(data)
    df = df.dropna()
    df.to_sql("combustibles", engine)
```

**Después (con packages):**

```python
# app/etl/combustibles.py
from packages.etl_core import ETLBase
from packages.ckan_client import CKANClient
import pandas as pd

class CombustiblesETL(ETLBase):
    def __init__(self, db_session):
        super().__init__(name="combustibles", db_session=db_session)
        self.ckan = CKANClient()
    
    def extract(self) -> pd.DataFrame:
        dataset = self.ckan.get_dataset("precios-de-combustibles")
        resource_id = dataset["resources"][0]["id"]
        return self.ckan.fetch_resource_as_df(resource_id)
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        self.validate_data(data, ["fecha", "producto", "precio"])
        data = data.dropna()
        data["precio"] = data["precio"].astype(float)
        return data
    
    def load(self, data: pd.DataFrame) -> None:
        data.to_sql("combustibles", self.db_session.bind, if_exists="append")

# Uso
etl = CombustiblesETL(db_session=session)
result = etl.run()
```

### Beneficios

✅ **Reutilización**: Código compartido entre precios/gastos/datos  
✅ **Mantenibilidad**: Cambios en un lugar benefician a todas las apps  
✅ **Testing**: Tests compartidos para packages  
✅ **Escalabilidad**: Fácil agregar nuevas apps  
✅ **Consistencia**: Mismo patrón ETL en todo el proyecto  

## 📝 Convenciones

1. **Imports**: Usar rutas absolutas desde `packages/`
   ```python
   from packages.etl_core import ETLBase
   from packages.ckan_client import CKANClient
   ```

2. **Logging**: Todos los packages usan `logging.getLogger(__name__)`

3. **Type hints**: Usar type hints en todas las funciones públicas

4. **Documentación**: Docstrings estilo Google

5. **Testing**: Tests en `tests/packages/`

## � sice_client

Cliente para acceso a compras públicas del Estado uruguayo (formato OCDS).

### Uso

```python
from packages.sice_client import SICEComprasClient

client = SICEComprasClient()

# Obtener compras de 2024
transactions = client.get_compras(year=2024, limit=1000)
print(f"Obtenidas: {len(transactions)} compras públicas")

# Convertir a DataFrame
df = client.to_dataframe(transactions)

# Separar normales de anomalías documentadas
normal, anomalous = client.filter_by_anomalies(transactions)
print(f"Normales: {len(normal)}, Anomalías: {len(anomalous)}")

# Convertir a modelo Transaction compartido
from packages.shared_models import Transaction
shared_txn = transactions[0].to_transaction()
```

### Métodos principales

- `get_compras(year, month, limit)`: Obtener compras por año/mes
- `to_dataframe(transactions)`: Convertir a pandas DataFrame
- `filter_by_anomalies(transactions)`: Separar normales de anomalías
- Fallback automático a datos sintéticos si API no disponible

---

## 📦 db_utils

Utilidades compartidas para operaciones de base de datos.

### BulkInserter

Inserción masiva optimizada con detección de duplicados.

```python
from packages.db_utils import BulkInserter
from app.models.models import Precio

inserter = BulkInserter(session, Precio)

data = [
    {"producto_id": 1, "fecha": "2024-01-01", "valor": 100},
    {"producto_id": 1, "fecha": "2024-01-02", "valor": 105},
]

result = inserter.bulk_insert_dict(
    data,
    unique_columns=["producto_id", "fecha"],
    skip_duplicates=True
)

print(f"✅ Insertados: {result['inserted']}")
print(f"⏭️ Duplicados: {result['skipped']}")
print(f"❌ Errores: {result['errors']}")
```

### Validación de Duplicados

```python
from packages.db_utils import validate_unique_constraint

data = {"producto_id": 1, "fecha": "2024-01-01", "valor": 100}

existe = validate_unique_constraint(
    session,
    Precio,
    data,
    unique_columns=["producto_id", "fecha"]
)

if not existe:
    session.add(Precio(**data))
    session.commit()
```

### Helpers Adicionales

- `get_table_columns(model)`: Obtener columnas de un modelo
- `dataframe_to_model(df, model, mapping)`: Convertir DataFrame a objetos
- `chunk_list(data, size)`: Dividir lista en chunks para procesamiento

---

## 🚀 Próximos Pasos

1. ~~Migrar ETL actual de combustibles a usar `ETLBase`~~ ✅ Completado (v2)
2. Crear tests para cada package
3. Documentar ejemplos adicionales
4. Integrar `sice_client` en app de gastos públicos
5. Usar `BulkInserter` en todos los ETL para optimizar carga

---

**Última actualización**: 2025-01-26  
**Packages creados**: 5 (etl_core, ckan_client, sice_client, db_utils, shared_models)  
**Mantenedor**: @manusabbath-arch
