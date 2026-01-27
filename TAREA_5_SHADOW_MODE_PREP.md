# TAREA 5: Shadow Mode Testing - Preparación

**Estado**: 🟡 Listo para iniciar (dependencias completadas)

---

## Resumen

Shadow Mode es un patrón de testing en el que ejecutamos v1 (código actual) y v2 (código refactorizado) en **paralelo en producción o pre-producción**, comparamos los resultados, y validamos que son equivalentes antes de hacer el rollout gradual.

## Preparación Completada

✅ **TAREA 1-4 COMPLETADAS**: 
- combustibles_v2.py validado como referencia
- ute_v2.py creado
- ose_v2.py creado  
- antel_v2.py creado
- 25 tests pasando
- 1,277 líneas de código nuevo

## Plan de Implementación para TAREA 5

### Fase 1: Shadow Mode Infrastructure (1-2 días)

**Archivo a crear**: `backend/app/services/shadow_mode.py`

Responsabilidades:
1. **ShadowModeExecutor** clase que:
   - Ejecuta v1 y v2 en paralelo
   - Captura resultados de ambas
   - Compara resultados
   - Registra diferencias (si hay)
   - Retorna resultado de v1 al usuario

```python
class ShadowModeExecutor:
    async def run_shadow(self, etl_name: str, db_session: Session):
        """
        Ejecuta v1 y v2 en paralelo, compara resultados.
        
        Retorna resultado de v1 pero registra discrepancias.
        """
        # Ejecutar v1
        result_v1 = await etl_v1.run()
        
        # Ejecutar v2 (en paralelo con v1)
        result_v2 = await etl_v2.run()
        
        # Comparar
        comparison = self.compare_results(result_v1, result_v2)
        
        # Log discrepancias
        if comparison.has_differences():
            logger.warning(f"Shadow mode discrepancy: {comparison}")
        
        # Retornar v1 (no afectar a usuarios)
        return result_v1
```

### Fase 2: Shadow Mode Logging (1-2 días)

**Archivo a crear**: `backend/app/services/shadow_mode_logs.py`

Responsabilidades:
1. Registrar ejecución de v1 y v2
2. Almacenar comparaciones en base de datos
3. Dashboard para visualizar discrepancias

```python
class ShadowModeLog:
    - execution_id: UUID
    - etl_name: str
    - timestamp: datetime
    - v1_result: dict (success, records, duration, errors)
    - v2_result: dict (success, records, duration, errors)
    - differences: dict (detalles de diferencias)
    - metadata: dict (usuario, hash, etc)
```

### Fase 3: Shadow Mode Testing (2-3 días)

**Archivo a crear**: `backend/tests/test_shadow_mode.py`

Tests requeridos:
```python
class TestShadowMode:
    
    def test_shadow_combustibles_produces_same_results()
    def test_shadow_ute_produces_same_results()
    def test_shadow_ose_produces_same_results()
    def test_shadow_antel_produces_same_results()
    
    def test_shadow_handles_v1_failure()
    def test_shadow_handles_v2_failure()
    def test_shadow_handles_both_failures()
    
    def test_shadow_logs_discrepancies()
    def test_shadow_performance_acceptable()
```

### Fase 4: Integration (1-2 días)

**Modificaciones a endpoints**:

En `backend/app/api/routes/etl.py`:

```python
@router.post("/etl/run/{etl_name}")
async def run_etl_with_shadow(
    etl_name: str,
    shadow_mode: bool = True,  # Feature flag
    db: Session = Depends(get_db)
):
    if shadow_mode and ENV == "production":
        executor = ShadowModeExecutor(db)
        return await executor.run_shadow(etl_name)
    else:
        # Lógica actual con v1
        return await run_etl_v1(etl_name)
```

## Métricas de Validación

Antes de pasar a TAREA 6 (Endpoint Transitions), validaremos:

1. **Data Equivalence** (100%): 
   - Mismos registros procesados
   - Mismos valores en base de datos
   - Mismas fechas

2. **Performance** (±5%):
   - Tiempo de ejecución similar
   - Memoria usada comparable

3. **Error Handling** (100%):
   - Ambas capturan mismos errores
   - Logging consistente

4. **Logging** (100%):
   - Todos los eventos registrados
   - Formato consistente

## Timeline Estimado

| Tarea | Duración | Cumulative |
|-------|----------|-----------|
| 5.1: Shadow Infrastructure | 1-2 días | 1-2 días |
| 5.2: Shadow Logging | 1-2 días | 2-4 días |
| 5.3: Shadow Testing | 2-3 días | 4-7 días |
| 5.4: Integration | 1-2 días | 5-9 días |

**Estimado total Semana 2**: 5-9 días

## Archivo a Ejecutar Primero

```bash
# Crear infraestructura de shadow mode
touch backend/app/services/shadow_mode.py

# Test de integridad
pytest backend/tests/test_shadow_mode.py -v
```

## Requisitos Previos (Ya Completados ✅)

- ✅ combustibles_v2.py funcional
- ✅ ute_v2.py funcional  
- ✅ ose_v2.py funcional
- ✅ antel_v2.py funcional
- ✅ ETLBase disponible
- ✅ DB schema validado
- ✅ pytest + pytest-asyncio instalados

## Comandos para Iniciar TAREA 5

```bash
# Crear archivo de shadow mode
$ touch backend/app/services/shadow_mode.py

# Crear clase base
$ # ... copiar template from documentation

# Tests
$ pytest backend/tests/test_shadow_mode.py -v

# Validar integración
$ python -m pytest -k shadow -v
```

---

**Estado Actual**: Listo para TAREA 5
**Dependencias**: Todas completadas ✅
**Próximo Paso**: Implementar `backend/app/services/shadow_mode.py`

