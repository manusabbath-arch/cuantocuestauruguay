# 🔧 ARCH-002: Plan de Ejecución - Migración ETL a Packages

**Estado**: 🚀 INICIANDO  
**Fecha Inicio**: 26 de enero de 2026  
**Duración Estimada**: 2-3 semanas  
**Prioridad**: 🔴 ALTA (ARCH-002)

---

## 📋 Objetivo

Refactorizar ETL existentes (UTE, OSE, Antel) para usar la arquitectura compartida de `packages/`, siguiendo el patrón demostrado en `combustibles_v2.py`.

**Beneficios**:
- ✅ Reducción de código (~43%)
- ✅ Reutilización de componentes
- ✅ Logging automático y métricas integradas
- ✅ Preparación para monorepo unificado
- ✅ Mejor mantenibilidad

---

## 📊 Estado Actual

### Completado ✅
- [x] `backend/packages/etl_core/` - ETLBase abstracta
- [x] `backend/packages/ckan_client/` - Cliente CKAN
- [x] `backend/packages/db_utils/` - Utilidades DB
- [x] `backend/packages/shared_models/` - Modelos compartidos
- [x] `backend/app/etl/combustibles_v2.py` - Ejemplo de migración

### Por Hacer ⏳
- [ ] Testear `combustibles_v2.py` en staging
- [ ] Crear `ute_v2.py` usando ETLBase
- [ ] Crear `ose_v2.py` usando ETLBase
- [ ] Crear `antel_v2.py` usando ETLBase
- [ ] Performance testing (v1 vs v2)
- [ ] Documentation actualizada
- [ ] Deploy gradual a prod

---

## 🎯 Tareas Detalladas

### TAREA 1: Testear `combustibles_v2.py` (Semana 1)

#### 1.1 Validar syntax y imports
```bash
python3 -m py_compile backend/app/etl/combustibles_v2.py
```
Checklist:
- [ ] Imports correctos
- [ ] Herencia de ETLBase funciona
- [ ] CKANClient importa correctamente

#### 1.2 Análisis estático (Pylance/Pylint)
```bash
pylint backend/app/etl/combustibles_v2.py --disable=all --enable=E,F
```
Checklist:
- [ ] Sin errores críticos
- [ ] Sin imports no usados
- [ ] Type hints válidos

#### 1.3 Unit tests para `CombustiblesETLv2`
Crear `backend/tests/test_combustibles_v2.py`:
```python
@pytest.mark.asyncio
async def test_combustibles_v2_initialization(db_session):
    """Verificar que v2 se inicializa correctamente"""
    etl = CombustiblesETLv2(db_session)
    assert etl.name == "combustibles"
    assert etl.ckan is not None

@pytest.mark.asyncio
async def test_combustibles_v2_extract(db_session, mocker):
    """Mock CKAN client y verificar extracción"""
    etl = CombustiblesETLv2(db_session)
    # ... mock setup ...
    df = etl.extract()
    assert not df.empty

@pytest.mark.asyncio
async def test_combustibles_v2_run(db_session, mocker):
    """Test end-to-end de ejecución"""
    etl = CombustiblesETLv2(db_session)
    # ... mocks ...
    result = await etl.run()
    assert result['success']
```

Checklist:
- [ ] Tests pass en local
- [ ] Coverage > 80%
- [ ] Mock CKAN client funciona

#### 1.4 Performance comparison (v1 vs v2)
Crear `backend/tests/test_performance_combustibles.py`:
```python
import time

def test_combustibles_v1_timing(db_session):
    """Benchmark de combustibles.py (v1)"""
    etl = CombustiblesETL(db_session)
    start = time.time()
    result = etl.run()
    elapsed = time.time() - start
    print(f"v1 took {elapsed:.2f}s")

def test_combustibles_v2_timing(db_session):
    """Benchmark de combustibles_v2.py (v2)"""
    etl = CombustiblesETLv2(db_session)
    start = time.time()
    result = etl.run()
    elapsed = time.time() - start
    print(f"v2 took {elapsed:.2f}s")
```

Checklist:
- [ ] v2 similar o más rápido que v1
- [ ] Overhead de ETLBase < 5%
- [ ] Memory footprint similar

---

### TAREA 2: Crear `ute_v2.py` (Semana 1-2)

**Base**: Analizar `backend/app/etl/utilities.py` extraer UTE

#### 2.1 Análisis de dependencias
```bash
# Identificar qué usa extract_ute_tarifas()
grep -r "extract_ute_tarifas" backend/app/
```

Checklist:
- [ ] Identificar todas las dependencies
- [ ] Listar endpoints que usan UTE
- [ ] Documentar cambios necesarios

#### 2.2 Crear estructura básica
```python
# backend/app/etl/ute_v2.py
from packages.etl_core import ETLBase
from packages.ckan_client import CKANClient
from packages.db_utils import db_helpers

class UTEETLv2(ETLBase):
    """ETL para tarifas de UTE (v2 - usando packages)"""
    
    def __init__(self, db: Session):
        super().__init__(name="ute", db_session=db)
        # ... inicialización específica UTE
    
    def extract(self) -> pd.DataFrame:
        """Extraer de PDF o URSEA"""
        # Usar lógica de pdf_parser.py y TARIFF_HISTORY
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Normalizar columnas, datas, valores"""
    
    def load(self, data: pd.DataFrame) -> None:
        """Insertar en tabla precios"""
```

Checklist:
- [ ] Estructura básica creada
- [ ] Imports funcionales
- [ ] Métodos abstract implementados

#### 2.3 Integrar lógica existente
Copiar/adaptar de `utilities.py.extract_ute_tarifas()`:
- [x] PDF parsing (ya está en pdf_parser.py)
- [x] Historical fallback (TARIFF_HISTORY)
- [x] Scraper option (gracefully degraded)
- [ ] Logging compatible con ETLBase

#### 2.4 Tests para `UTEETLv2`
Similar a TAREA 1.3, pero para UTE:
- [ ] Unit tests
- [ ] Mocking de PDF parser
- [ ] Performance comparison

---

### TAREA 3: Crear `ose_v2.py` (Semana 2)

**Base**: Analizar `backend/app/etl/utilities.py` extraer OSE

Proceso idéntico a TAREA 2:
1. Analizar dependencias
2. Crear estructura básica
3. Integrar lógica existente
4. Tests

Checklist:
- [ ] `ose_v2.py` creado
- [ ] Tests pass
- [ ] Performance OK

---

### TAREA 4: Crear `antel_v2.py` (Semana 2)

**Base**: Analizar `backend/app/etl/utilities.py` extraer Antel

Mismo proceso que OSE:

Checklist:
- [ ] `antel_v2.py` creado
- [ ] Tests pass
- [ ] Performance OK

---

### TAREA 5: Shadow Mode Testing (Semana 2-3)

#### 5.1 Ejecutar v1 y v2 en paralelo
```python
# backend/app/etl/shadow_runner.py
async def shadow_run():
    """Ejecutar ambas versiones en paralelo"""
    # Correr v1
    result_v1 = await combustibles.run()
    
    # Correr v2
    result_v2 = await combustibles_v2.run()
    
    # Comparar resultados
    compare_results(result_v1, result_v2)
```

Checklist:
- [ ] Script de shadow mode creado
- [ ] Ejecutado exitosamente en staging
- [ ] Resultados idénticos (v1 == v2)
- [ ] Performance similar

#### 5.2 Validación de datos
- [ ] Misma cantidad de registros
- [ ] Mismo contenido
- [ ] Misma estructura en BD

---

### TAREA 6: Preparar Endpoints para v2 (Semana 2-3)

#### 6.1 Crear endpoints de transición
```python
# backend/app/api/etl_v2.py (nuevo)

@app.post("/api/v1/etl/combustibles-v2")
async def execute_combustibles_v2():
    """Endpoint para probar v2"""
    etl = CombustiblesETLv2(db)
    result = await etl.run()
    return result
```

Checklist:
- [ ] Endpoints v2 creados
- [ ] No rompen endpoints v1 existentes
- [ ] Documentación de endpoints

#### 6.2 Feature flag para v2
```python
# config.py
USE_ETL_V2: bool = False  # Toggle para v2

# En ETL runner
if settings.USE_ETL_V2:
    etl = CombustiblesETLv2(db)
else:
    etl = CombustiblesETL(db)
```

Checklist:
- [ ] Feature flag implementado
- [ ] Puede togglearse sin redeploy
- [ ] Logging indica cuál versión corre

---

### TAREA 7: Migrar a v2 Gradualmente (Semana 3)

#### 7.1 En Staging
- [ ] Activar `USE_ETL_V2=True` en staging
- [ ] Ejecutar ETL completo
- [ ] Verificar logs y alertas
- [ ] Comparar data con prod

#### 7.2 En Producción (Gradual)
- [ ] Día 1: 10% tráfico a v2 (feature flag)
- [ ] Día 2: 25% tráfico a v2
- [ ] Día 3: 50% tráfico a v2
- [ ] Día 4: 100% en v2
- [ ] Día 5: Remover v1 endpoints

Checklist:
- [ ] Logs limpios en cada etapa
- [ ] Sin errores en alertas
- [ ] Performance OK
- [ ] Users no afectados

---

### TAREA 8: Documentación y Cleanup (Semana 3)

#### 8.1 Documentar ARCH-002
- [ ] Crear `docs/ARCH_002_COMPLETED.md`
- [ ] Actualizar `ROADMAP.md`
- [ ] Documentar decisiones de migración
- [ ] Performance improvements

#### 8.2 Cleanup de v1
- [ ] Archivar `combustibles.py` (no eliminar aún)
- [ ] Remover referencias a v1 en documentación
- [ ] Actualizar todos los imports

#### 8.3 Código de ejemplo
- [ ] Actualizar `backend/app/etl/utilities.py` para usar ETLBase
- [ ] Crear template para nuevos ETL
- [ ] Documentar best practices

Checklist:
- [ ] Documentación completa
- [ ] Código limpio
- [ ] Ready para próxima fase

---

## 🧪 Tests a Crear/Actualizar

```
backend/tests/
├── test_combustibles_v2.py          (NEW)
├── test_ute_v2.py                   (NEW)
├── test_ose_v2.py                   (NEW)
├── test_antel_v2.py                 (NEW)
├── test_performance_combustibles.py (NEW)
└── test_etl_migration.py             (NEW - integration tests)
```

---

## 📈 Métricas de Éxito

| Métrica | Target | Status |
|---------|--------|--------|
| Tests Pass | 100% | ⏳ |
| Code Coverage | >85% | ⏳ |
| Performance (v2 vs v1) | ±5% | ⏳ |
| Data Consistency | 100% match | ⏳ |
| Migration Time | <1 hour | ⏳ |
| No Breaking Changes | 0 issues | ⏳ |

---

## 🚀 Próximos Pasos

### Hoy (26 Jan 2026)
- [ ] Review este documento
- [ ] Confirmar entendimiento de ARCH-002
- [ ] Iniciar TAREA 1

### Semana 1
- [ ] Completar TAREA 1: Test `combustibles_v2.py`
- [ ] Iniciar TAREA 2: Crear `ute_v2.py`

### Semana 2
- [ ] Completar TAREA 2: `ute_v2.py`
- [ ] Completar TAREA 3: `ose_v2.py`
- [ ] Completar TAREA 4: `antel_v2.py`
- [ ] Iniciar TAREA 5: Shadow mode testing

### Semana 3
- [ ] Completar TAREA 5-8
- [ ] Deploy en staging
- [ ] Preparar para deploy en prod
- [ ] Code review + merge a main

---

## 📚 Referencias

- `backend/packages/README.md` - Documentación de packages
- `docs/INTEGRACION_BACKEND.md` - Plan de integración general
- `docs/MIGRACION_ETL.md` - Detalles técnicos de migración
- `backend/app/etl/combustibles_v2.py` - Ejemplo de v2

---

## 💬 Notas

- Este es un refactor NO-BREAKING: v1 sigue funcionando
- Usar feature flags para transición gradual
- Shadow mode permite comparar v1 vs v2 en tiempo real
- El objetivo es demostrar el valor de packages compartidos
- Prepara el terreno para migración de otros proyectos

---

**Status**: 🟢 READY TO START  
**Owner**: Development Team  
**Next Review**: End of Week 1
