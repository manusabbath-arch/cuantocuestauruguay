# Plan de Integración Backend - Monorepo Gradual

## Contexto
Integración gradual de 3 proyectos relacionados bajo **cuantocuestauruguay.com**:
- **PreciosRegulados** (actual): API de precios de servicios públicos
- **Transparencia**: API de datos abiertos del gobierno
- **BotFiscalizador**: Monitor de gastos públicos del MEF

## Estrategia: Monorepo Backend-First

### Fase 1: Extracción de Código Compartido (Sprint Actual)

#### 1.1 Crear estructura de paquetes compartidos
```
backend/
├── packages/                    # Código compartido entre apps
│   ├── etl_core/               # Base común para ETL
│   │   ├── __init__.py
│   │   ├── base.py             # ETLBase clase abstracta
│   │   ├── validators.py       # Validadores comunes
│   │   └── extractors.py       # Extractores genéricos
│   ├── ckan_client/            # Cliente para catalogodatos.gub.uy
│   │   ├── __init__.py
│   │   └── client.py           # Wrapper de CKAN API
│   └── db_utils/               # Utilidades de DB compartidas
│       ├── __init__.py
│       └── helpers.py          # Helpers de SQLAlchemy
└── app/                         # App actual (PreciosRegulados)
    └── etl/                     # Refactorizar para usar packages/
```

#### 1.2 Código descubierto en transparencia (reutilizable)

**SICEComprasConnector** (`services/data_ingestion.py`):
- Cliente para API de SICE Compras
- Útil para datos de compras públicas
- Migrar a `packages/sice_client/`

**Transaction dataclass** (`services/data_ingestion.py`):
- Modelo común de transacción de gasto público
- Puede ser base para estandarizar datos entre apps
- Migrar a `packages/shared_models/`

**CKAN Client** (`archive/temp/all/integrations/ckan/client.py`):
- Wrapper para API de catalogodatos.gub.uy
- Migrar a `packages/ckan_client/`

**ETL Schemas** (`etl/schemas.py`):
- Esquemas de validación para ETL
- Revisar compatibilidad con Pydantic v2

### Fase 2: Refactorización del ETL Actual

#### 2.1 Refactorizar `backend/app/etl/combustibles.py`
Heredar de `ETLBase` para establecer patrón:
```python
from packages.etl_core.base import ETLBase
from packages.ckan_client import CKANClient

class CombustiblesETL(ETLBase):
    def extract(self) -> pd.DataFrame:
        # Usar CKANClient compartido
        client = CKANClient()
        return client.fetch_resource(...)
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        # Lógica actual
        pass
    
    def load(self, data: pd.DataFrame) -> None:
        # Usar db_utils compartidos
        pass
```

#### 2.2 Migrar otros ETL
- `app/etl/ute.py` → usar `ETLBase`
- `app/etl/ose.py` → usar `ETLBase`
- `app/etl/antel.py` → usar `ETLBase`

### Fase 3: Preparación para Migración de Transparencia

#### 3.1 Crear apps/transparencia (sin romper repo original)
```
backend/
├── packages/                # Ya creado en Fase 1
└── apps/
    ├── precios/             # Renombrar app/ actual
    │   └── ...
    └── transparencia/       # Nuevo, copia selectiva
        ├── api/             # Endpoints de transparencia
        ├── models/          # Modelos de DB
        └── etl/             # ETL usando packages/
```

#### 3.2 Verificar dependencias compartidas
- PostgreSQL (ambos usan)
- SQLAlchemy (verificar versiones)
- FastAPI (ambos usan)
- Pydantic v2 (migrar si es necesario)

### Fase 4: Configuración Multi-App

#### 4.1 Actualizar `backend/app/main.py`
```python
from fastapi import FastAPI
from apps.precios.routes import precios_router
from apps.transparencia.routes import transparencia_router

app = FastAPI(title="CuantoCuestaUruguay - API Unificada")

app.include_router(precios_router, prefix="/precios", tags=["Precios"])
app.include_router(transparencia_router, prefix="/datos", tags=["Datos Abiertos"])
```

#### 4.2 Subdominios/Rutas
- **cuantocuestauruguay.com/api/precios/** → PreciosRegulados
- **cuantocuestauruguay.com/api/datos/** → Transparencia
- **cuantocuestauruguay.com/api/gastos/** → BotFiscalizador (Fase 5)

### Fase 5: Integración de BotFiscalizador (Streamlit → FastAPI)

#### 5.1 Extraer lógica de negocio
- BotFiscalizador usa Streamlit (UI directa)
- Separar lógica de análisis de UI
- Crear API FastAPI para análisis de gastos
- Streamlit puede consumir la API como cliente

#### 5.2 Estructura propuesta
```
backend/apps/gastos/
├── api/                     # FastAPI endpoints
│   └── analisis.py         # Análisis de gastos
├── models/                  # Modelos DB
│   └── gasto.py
└── services/                # Lógica de negocio
    └── anomaly_detector.py # Detectar anomalías
```

## Roadmap de Ejecución

### Sprint 1: Fundaciones (2-3 días)
- [x] Análisis de código existente
- [ ] Crear `backend/packages/etl_core/`
- [ ] Crear `backend/packages/ckan_client/`
- [ ] Documentar convenciones de código

### Sprint 2: Refactorización (3-4 días)
- [ ] Migrar CombustiblesETL a usar ETLBase
- [ ] Probar todos los ETL existentes
- [ ] Actualizar tests

### Sprint 3: Preparar Transparencia (5-7 días)
- [ ] Copiar código de transparencia a `apps/transparencia/`
- [ ] Adaptar a usar `packages/`
- [ ] Configurar rutas `/api/datos/`
- [ ] Actualizar Render.com deployment

### Sprint 4: Frontend Multi-App (1 semana)
- [ ] Crear `frontend/apps/precios/` (actual)
- [ ] Crear `frontend/apps/datos/` (transparencia)
- [ ] Shared UI components en `frontend/packages/`
- [ ] Configurar routing

### Sprint 5: BotFiscalizador (1 semana)
- [ ] Extraer lógica de Streamlit
- [ ] Crear API en `apps/gastos/`
- [ ] Integrar en monorepo
- [ ] Opcional: mantener Streamlit como cliente separado

## Ventajas de Este Enfoque

✅ **Gradual**: No rompe nada, se migra paso a paso
✅ **Reutilización**: Código compartido evita duplicación
✅ **Escalable**: Fácil agregar nuevas apps
✅ **Mantenible**: Cambios en `packages/` benefician a todas las apps
✅ **Dominio único**: Todo bajo cuantocuestauruguay.com
✅ **Testing**: Tests compartidos para `packages/`

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Romper ETL actual al refactorizar | Tests exhaustivos antes de cambiar |
| Conflictos de versiones de dependencias | Usar requirements-shared.txt |
| Complejidad de deploy multi-app | Mantener apps independientes en Render |
| Frontend monolítico | Usar code-splitting y lazy loading |

## Próximos Pasos Inmediatos

1. **Crear `packages/etl_core/base.py`** con clase abstracta
2. **Copiar CKAN client de transparencia** a `packages/ckan_client/`
3. **Crear `packages/shared_models/transaction.py`** con modelo común
4. **Actualizar `requirements.txt`** para packages compartidos
5. **Refactorizar un ETL como prueba** (combustibles)

## Decisiones Pendientes

- [ ] ¿Usar Turborepo/Nx o estructura manual?
- [ ] ¿Separar DBs por app o DB unificada?
- [ ] ¿BotFiscalizador como API o mantener Streamlit standalone?
- [ ] ¿Migrar frontend a monorepo o mantener separado?

---

**Última actualización**: 2025-01-26  
**Estado**: En progreso - Fase 1 iniciada  
**Owner**: @manusabbath-arch
