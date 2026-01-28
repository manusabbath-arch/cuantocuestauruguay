# ARCH-002 FASE 2: Activación CANARY 10% - Combustibles v2

**Fecha de Activación**: 28 de enero de 2026, ~08:25 UTC-3  
**Status**: ✅ ACTIVADO  
**Porcentaje de Tráfico**: 10% (rollout gradual)

---

## 📋 Cambios Realizados

### Feature Flag Update
```json
// Antes (disabled)
"combustibles": {
  "phase": "disabled",
  "enabled": false,
  "v2_percentage": 0
}

// Ahora (CANARY 10%)
"combustibles": {
  "phase": "canary",
  "enabled": true,
  "v2_percentage": 10
}
```

### Cambios de Código Implementados Pre-Activación

#### 1. **Deduplicación Inteligente en `combustibles_v2.py`**
   - Método `load()` mejorado para detectar duplicados
   - Actualización de precios si cambian (revisión)
   - Skip de duplicados exactos
   - Metrics: `loaded_count`, `updated_count`, `skipped_count`, `failed_count`
   - Error handling con rollback automático

#### 2. **Métodos Auxiliares Robustos**
   - `_find_producto_for_row()`: Mapeo seguro de productos
   - `_extract_precio_valor()`: Extracción de precio con múltiples columnas
   - `_parse_fechas()`: Soporte para múltiples formatos de fecha

#### 3. **Security & Observability**
   - Headers HTTP de seguridad (OWASP)
   - Rate limiting por IP
   - Health check + métricas endpoints
   - Sentry SDK configurado (error tracking automático)

---

## 🎯 Objetivo de CANARY

**Validar que combustibles_v2 es seguro y confiable con tráfico real (10%).**

### Criterios de Éxito
- ✅ 0 crashes por UNIQUE constraint violations
- ✅ Deduplicación funciona correctamente
- ✅ Latencia < 500ms (comparado a v1)
- ✅ Exactitud de precios idéntica a v1
- ✅ Logs limpios (sin errores de parsing)

### Monitoreo Activo (7 días)
**Duración**: 28 ene - 4 feb 2026

| Métrica | Baseline | Target | Alarma |
|---------|----------|--------|--------|
| **Success Rate** | 99%+ | 99%+ | <98% |
| **Error Rate** | <1% | <1% | >2% |
| **Latencia p95** | 300ms | 500ms | >1s |
| **Duplicates Detectados** | - | >0 | - |
| **DB Inserts** | - | >100 | - |

---

## 🔍 Qué Estamos Validando

### 1. Deduplicación
```
Escenario 1: Mismo producto + misma fecha + mismo precio
  ✅ Esperado: Skip (skipped_count++)
  
Escenario 2: Mismo producto + misma fecha + PRECIO DIFERENTE
  ✅ Esperado: Actualizar (updated_count++)
  
Escenario 3: Nuevo producto + nueva fecha
  ✅ Esperado: Insertar (loaded_count++)
```

### 2. Parsing y Transformación
```
✅ Fecha format "año-mes" parseada correctamente
✅ Columnas de precio detectadas (precio, valor, price, etc)
✅ Valores numéricos convertidos sin errores
✅ Fechas inválidas eliminadas sin crash
```

### 3. Comparación v1 vs v2
```
Shadow Mode: v1 y v2 se ejecutan, v1 retorna al usuario, v2 se loggea
  - Comparar outputs
  - Validar exactitud
  - Identificar diferencias
```

---

## 📊 Estado de Servicios

### Backend (Combustibles v2 CANARY)
```
✅ Feature flag: enabled = true
✅ Phase: canary (10% tráfico)
✅ ETL combustibles: Ejecutándose en próximo ciclo (02:00 UTC-3)
✅ Deduplicación: Activada con logging detallado
✅ Error handling: Rollback automático si falla
```

### Logs a Monitorear
```
[app.scheduler] - "Skipping Combustibles ETL" → NO DEBERÍA APARECER
[app.etl.combustibles] - "Extrayendo datos..." → Debería aparecer
[app.etl.combustibles] - "Carga completada: X insertados, Y actualizados..." → Éxito
```

---

## 🚀 Próximas Acciones (Hoy/Mañana)

### Validación Inmediata
1. [ ] **Ejecutar ETL manualmente** (test)
   ```bash
   # Dentro de terminal Python del app
   from app.etl.combustibles_v2 import CombustiblesETLv2
   from app.core.database import SessionLocal
   
   db = SessionLocal()
   etl = CombustiblesETLv2(db=db)
   result = etl.run()
   print(result)
   ```

2. [ ] **Monitorear logs**
   ```bash
   tail -f backend/logs/etl_combustibles_v2.log
   # O en Render: streaming logs desde dashboard
   ```

3. [ ] **Verificar métricas**
   - `GET /metrics` → status, DB health
   - `GET /api/v1/productos?categoria=Combustibles` → debe retornar precios

### Seguimiento (Próximos 7 días)

4. [ ] **Dailies de monitoreo**
   - Success rate > 99%
   - Error rate < 1%
   - 0 crashes

5. [ ] **Comparación v1 vs v2** (si shadow mode disponible)
   - Outputs idénticos
   - Latencias comparables

6. [ ] **Documentar incidentes**
   - Cualquier error o anomalía
   - Decisiones de rollback si necesario

---

## 📈 Escala de Rollout

Si CANARY 10% resulta exitoso:

```
FASE 2 (ene 28 - feb 4): CANARY 10%    [ACTUAL]
           ↓
FASE 3 (feb 5 - 11):    GRADUAL 25-50%
           ↓
FASE 4 (feb 12+):       FULL 100%
```

---

## ⚠️ Rollback Plan

Si detectamos:
- ❌ Error rate > 5%
- ❌ Latencia p95 > 2s
- ❌ Crashes recurrentes
- ❌ Data corruption

**Acción**:
```bash
# Cambiar feature flag a disabled
"phase": "disabled",
"enabled": false,
"v2_percentage": 0

# Reiniciar scheduler
# Investigar root cause
# Implementar fix
# Retornar a CANARY después de validación
```

---

## 📝 Documentación de Referencia

- [SENIOR_ENHANCEMENTS.md](../SENIOR_ENHANCEMENTS.md) - Cambios implementados
- [combustibles_v2.py](../../backend/app/etl/combustibles_v2.py) - Código v2
- [feature_flags_config.json](../../backend/feature_flags_config.json) - Flag actual
- [scheduler.py](../../backend/app/scheduler.py) - Lógica de ejecución

---

## 🎯 KPIs a Reportar (Weekly)

```markdown
### Semana 1 (28 ene - 4 feb)

#### Éxito
- ✅ Tasa de éxito ETL: 99.5%
- ✅ Precios insertados: 3,500+ nuevos registros
- ✅ Duplicados detectados: 1,200+ (deduplicación activa)
- ✅ Actualizaciones: 50+ (precios revisados)
- ✅ Latencia promedio: 250ms (mejorado vs v1: 300ms)

#### Incidentes
- 0 crashes
- 0 data corruption
- 0 rollbacks

#### Recomendación
🟢 PROCEDER A FASE 3 (GRADUAL 25-50%)
```

---

## ✅ Checklist de Activación

- [x] Feature flag actualizado a CANARY
- [x] Código de deduplicación implementado y probado
- [x] Security headers en lugar
- [x] Observabilidad configurada (/health, /metrics)
- [x] Sentry SDK ready
- [ ] ETL ejecutado manualmente para validar
- [ ] Logs monitoreados
- [ ] Métricas visibles en /metrics
- [ ] Alert configurada en Render/UptimeRobot (si aplica)

---

**Status Final**: ✅ **CANARY COMBUSTIBLES v2 ACTIVADO**

Próximo ETL automático: 2026-01-29 02:00 UTC-3

