# Migración de ETL a Arquitectura de Packages

## Comparación: Versión Original vs v2

### Archivo: `combustibles.py` → `combustibles_v2.py`

#### ❌ Versión Original (sin packages)

```python
class CombustiblesETL:
    def __init__(self, db: Session):
        self.db = db
        self.api_url = f"{settings.CKAN_API_URL}/datastore_search"
        self.resource_id = settings.CKAN_COMBUSTIBLES_RESOURCE_ID
    
    async def extract(self) -> Optional[pd.DataFrame]:
        # 40 líneas de código para hacer request HTTP
        params = {"resource_id": self.resource_id, "limit": 1000}
        response = requests.get(self.api_url, params=params, timeout=30)
        data = response.json()
        # ... más código
```

**Problemas:**
- 🔴 Código de acceso a CKAN duplicado en cada ETL
- 🔴 No hay logging automático de fases
- 🔴 Sin métricas de performance
- 🔴 Cada ETL implementa su propia lógica de error handling
- 🔴 Difícil de testear (dependencias acopladas)

#### ✅ Versión v2 (con packages)

```python
from packages.etl_core import ETLBase
from packages.ckan_client import CKANClient

class CombustiblesETLv2(ETLBase):
    def __init__(self, db: Session):
        super().__init__(name="combustibles", db_session=db)
        self.ckan = CKANClient()  # Cliente reutilizable
        self.resource_id = settings.CKAN_COMBUSTIBLES_RESOURCE_ID
    
    def extract(self) -> pd.DataFrame:
        # 5 líneas de código
        df = self.ckan.fetch_resource_as_df(
            resource_id=self.resource_id,
            format_hint="csv"
        )
        return df
```

**Beneficios:**
- ✅ Código CKAN reutilizable en todos los ETL
- ✅ Logging automático de todas las fases
- ✅ Métricas automáticas (duración, registros, errores)
- ✅ Error handling consistente
- ✅ Fácil de testear (dependencias inyectables)
- ✅ Método `run()` orquesta todo el proceso

## Comparación de Líneas de Código

| Aspecto | Original | v2 con Packages | Ahorro |
|---------|----------|-----------------|--------|
| Extracción (extract) | 40 líneas | 8 líneas | **80%** |
| Transformación (transform) | 60 líneas | 50 líneas | **17%** |
| Carga (load) | 50 líneas | 45 líneas | **10%** |
| Boilerplate (logging, metrics) | 30 líneas | 0 líneas (heredado) | **100%** |
| **TOTAL** | **180 líneas** | **103 líneas** | **43%** |

## Mejoras de Calidad

### 1. Logging Automático

**Original:**
```python
logger.info("Extracting data from CKAN API...")
# ... código
logger.info(f"Extracted {len(df)} records")
# Hay que loggear manualmente cada paso
```

**v2:**
```python
# ETLBase se encarga automáticamente:
# [INFO] Iniciando ETL: combustibles
# [INFO] Fase 1: Extracción
# [INFO] Extraídos 1234 registros
# [INFO] Fase 2: Transformación
# [INFO] Transformados 1234 registros
# [INFO] Fase 3: Carga
# [INFO] ETL completado: 1234 registros en 5.6s
```

### 2. Métricas de Performance

**Original:**
```python
# No hay tracking automático de métricas
async def run():
    df = await self.extract()
    df = await self.transform(df)
    await self.load(df)
    # ¿Cuánto tardó? ¿Cuántos errores? 🤷
```

**v2:**
```python
result = etl.run()
# {
#     "success": True,
#     "records_processed": 1234,
#     "duration_seconds": 5.6,
#     "errors": []
# }
```

### 3. Error Handling Consistente

**Original:**
```python
try:
    # Código ETL
except requests.exceptions.RequestException as e:
    logger.error(f"Error: {e}")
    return None  # ⚠️ Cada ETL maneja errores diferente
```

**v2:**
```python
# ETLBase captura y loggea TODOS los errores
# Retorna resultado estandarizado:
# {
#     "success": False,
#     "errors": ["Error en ETL combustibles: Connection timeout"]
# }
```

## Plan de Migración Gradual

### Fase 1: Preparación ✅ (Completado)

- [x] Crear `backend/packages/etl_core/`
- [x] Crear `backend/packages/ckan_client/`
- [x] Crear `backend/packages/shared_models/`
- [x] Documentar en `packages/README.md`
- [x] Crear ejemplo refactorizado: `combustibles_v2.py`

### Fase 2: Testing de v2 (Próximo)

- [ ] Crear tests para `CombustiblesETLv2`
- [ ] Ejecutar v2 en paralelo con original (shadow mode)
- [ ] Comparar resultados: ¿son idénticos?
- [ ] Benchmark de performance

### Fase 3: Migración Progresiva

#### Sprint 1: Combustibles
- [ ] Validar que `combustibles_v2.py` funciona correctamente
- [ ] Reemplazar `combustibles.py` con v2
- [ ] Actualizar endpoint `/etl/combustibles` para usar v2
- [ ] Deploy a staging → validar → deploy a producción

#### Sprint 2: UTE
- [ ] Crear `ute_v2.py` usando `ETLBase`
- [ ] Migrar endpoint
- [ ] Deploy

#### Sprint 3: OSE
- [ ] Crear `ose_v2.py` usando `ETLBase`
- [ ] Migrar endpoint
- [ ] Deploy

#### Sprint 4: Antel
- [ ] Crear `antel_v2.py` usando `ETLBase`
- [ ] Migrar endpoint
- [ ] Deploy

### Fase 4: Cleanup

- [ ] Eliminar archivos `*_v1.py` antiguos
- [ ] Actualizar toda la documentación
- [ ] Crear tests de integración
- [ ] Métricas de performance post-migración

## Estrategia: Migración sin Downtime

### Opción A: Feature Flag

```python
# app/etl/__init__.py
USE_V2_ETL = os.getenv("USE_V2_ETL", "false").lower() == "true"

if USE_V2_ETL:
    from app.etl.combustibles_v2 import CombustiblesETLv2 as CombustiblesETL
else:
    from app.etl.combustibles import CombustiblesETL
```

### Opción B: Shadow Mode (Ejecutar ambos, comparar)

```python
# Ejecutar v1
result_v1 = await etl_v1.run()

# Ejecutar v2
result_v2 = etl_v2.run()

# Comparar resultados
if result_v1 == result_v2:
    logger.info("✅ v2 produce resultados idénticos")
else:
    logger.warning("⚠️ Diferencias detectadas")
    # Guardar para análisis
```

### Opción C: Blue-Green Deployment

1. Deploy v2 a entorno staging
2. Ejecutar batería completa de tests
3. Validar métricas de performance
4. Switch gradual de tráfico: 10% → 50% → 100%
5. Rollback automático si errores > threshold

## Validación Post-Migración

### Checklist de QA

- [ ] ✅ Todos los tests pasan
- [ ] ✅ Performance igual o mejor que v1
- [ ] ✅ Logs más descriptivos y útiles
- [ ] ✅ Métricas disponibles en dashboard
- [ ] ✅ Sin errores en producción por 7 días
- [ ] ✅ Código más legible y mantenible

### Métricas a Monitorear

| Métrica | Target | Actual v1 | Actual v2 |
|---------|--------|-----------|-----------|
| Tiempo de ejecución | < 10s | 8.5s | ⏱️ TBD |
| Tasa de éxito | > 99% | 98.5% | ⏱️ TBD |
| Líneas de código | ↓ 40% | 180 LOC | 103 LOC ✅ |
| Cobertura de tests | > 80% | 45% | ⏱️ TBD |

## Próximos Pasos Inmediatos

1. **Crear tests para `combustibles_v2.py`**
   ```bash
   pytest tests/etl/test_combustibles_v2.py -v
   ```

2. **Ejecutar en local y validar**
   ```bash
   cd backend
   python -m app.etl.combustibles_v2
   ```

3. **Revisar logs y métricas**
   - ¿Los logs son más útiles?
   - ¿Las métricas ayudan a debuggear?

4. **Decisión GO/NO-GO**
   - Si todo OK → migrar otros ETL
   - Si hay issues → ajustar y repetir

---

**Última actualización**: 2025-01-26  
**Estado**: Fase 1 completada, iniciando Fase 2  
**Responsable**: @manusabbath-arch
