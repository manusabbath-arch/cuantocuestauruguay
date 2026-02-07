# TAREA 7: Gradual Rollout Plan - Migración v1 → v2

## 📋 Objetivo
Implementar un plan de migración seguro de 3 semanas (10% → 25% → 50% → 100%) con monitoreo continuo, alertas automáticas y rollback instantáneo si detectan anomalías.

---

## 🎯 Fases de Rollout

### **FASE 1: Canary Deployment (Semana 1 - 10% usuarios)**

**Período**: Días 1-7 de producción
**Audiencia**: 10% de usuarios seleccionados aleatoriamente por hash de user_id

```
RolloutPhase.CANARY → percentage: 10
```

**Actividades**:
- ✅ Activar feature flag en todos los ETLs (combustibles, ute, ose, antel)
- ✅ Shadow mode activo en paralelo (v1 + v2 concurrent)
- ✅ Monitoreo intensivo cada 1 hora
- ✅ Alertas en: Slack #etl-monitoring + email ops@

**Métricas a Monitorear**:
| Métrica | Baseline | Umbral Alerta |
|---------|----------|---------------|
| Error Rate | < 0.5% | > 2% |
| Response Time (p95) | 800ms | > 1.2s |
| Data Mismatches (v1 vs v2) | 0 | > 5 en 1 hora |
| Precio Records Inserted | avg ± 5% | ± 15% |
| Tariff History Matches | 100% | < 98% |

**Rollback Trigger**: Si 2+ métricas fallan en ventana de 30 min

---

### **FASE 2: Early Adopters (Semana 2 - 25% usuarios)**

**Período**: Días 8-14
**Audiencia**: 25% de usuarios seleccionados por hash

**Actividades**:
- ✅ Aumentar percentage a 25
- ✅ Mantener shadow mode paralelo
- ✅ Monitoreo cada 4 horas (menos intensivo, si todo ok)
- ✅ Validación manual de 5 recorridos de datos aleatorios

**Validación Manual**:
```python
# Ejemplo: Validar que un usuario específico obtenga mismo precio en v1 vs v2
GET /api/v1/etl/run?user_id=test_user_001&shadow_mode=true
# Verificar shadow logs que v1 y v2 devuelven precio idéntico
```

**Decisión**: ¿Continuar a Fase 3 o mantener 25% por más tiempo?
- **Continuar si**: 0 mismatches, response time < 1s, error rate < 0.1%
- **Hold si**: Anomalías menores (mantener 25% por +7 días, replay logs)

---

### **FASE 3: Majority Users (Semana 3 - 50% usuarios)**

**Período**: Días 15-21
**Audiencia**: 50% de usuarios

**Actividades**:
- ✅ Aumentar percentage a 50
- ✅ Shadow mode sigue activo (ya no esencial, pero útil para comparación)
- ✅ Monitoreo diario (1x/día a las 09:00 UTC)
- ✅ Performance benchmarking vs baseline

**Performance Check**:
```bash
# Backend: revisar logs de ejecución
backend/logs/shadow_logs.jsonl
# Buscar patrones:
# - v2 más rápida que v1 en p95?
# - Datos idénticos?
# - Errores nuevos?
```

**Decisión**: ¿Full deployment o rollback?
- **Full si**: 100% data match, p95 < 1s, error rate < 0.5%
- **Rollback si**: Problemas críticos detectados

---

### **FASE 4: Full Deployment (Semana 3 - 100% usuarios)**

**Período**: Días 20-21 EOD
**Audiencia**: 100% (v1 completamente deprecado)

**Actividades**:
- ✅ Cambiar RolloutPhase a FULL
- ✅ Desactivar shadow mode (opcional, puede mantener con {percentage: 0})
- ✅ Remover v1 de endpoints (gradualmente)
- ✅ Documentar lecciones aprendidas

**Validación Final**:
```python
# Confirmar que TODOS los endpoints usan v2
GET /api/v1/etl/feature-flags
# Esperado: todos en FULL phase, v2_enabled=true

# Última ejecución de shadow_logs
GET /api/v1/etl/shadow/logs?limit=100
# Esperado: últimas 100 ejecuciones con mismatches=0
```

---

## 🚨 Procedimientos de Rollback

### **Rollback Automático**

Trigger inmediato si se detecta:
```python
if (
    error_rate > 5% or
    response_time_p95 > 10% increase or
    data_mismatches > 10 in 1 hour or
    database_corruption_detected
):
    # Automático via Kubernetes/orchestrator
    feature_flags.set_phase(etl_name, RolloutPhase.DISABLED)
    alert("CRITICAL: Rollback activated for {etl_name}")
```

### **Rollback Manual**

```bash
# Opción 1: API endpoint
curl -X POST http://localhost:8000/api/v1/etl/feature-flags/combustibles \
  -H "Content-Type: application/json" \
  -d '{"phase": "DISABLED"}'

# Opción 2: Código
from app.core.feature_flags import feature_flags, RolloutPhase
feature_flags.set_phase("combustibles", RolloutPhase.DISABLED)
feature_flags.disable_v2("combustibles")
```

**Tiempo de Rollback**: < 5 minutos
**Validación**: Verificar que traffic se redirige 100% a v1

---

## 📊 Dashboard de Monitoreo

### **Endpoints Disponibles**

```
GET /api/v1/etl/feature-flags
└─ Devuelve estado actual de todas las flags

GET /api/v1/etl/shadow/logs?limit=50
└─ Últimos 50 registros de shadow mode

POST /api/v1/etl/feature-flags/{etl_name}
├─ body: {"phase": "CANARY", "percentage": 10}
└─ Actualiza flag sin reiniciar servidor
```

### **Métricas en Shadow Logs**

```json
{
  "timestamp": "2026-01-26T10:30:00Z",
  "etl_name": "combustibles",
  "v1_duration_seconds": 3.45,
  "v2_duration_seconds": 2.89,
  "v1_record_count": 1234,
  "v2_record_count": 1234,
  "mismatches": 0,
  "v1_error": null,
  "v2_error": null
}
```

---

## ✅ Checklist Diario

### **Cada Mañana (09:00 UTC)**

- [ ] Revisar error rates en logs (< 0.5%?)
- [ ] Verificar response times p95 (< 1s?)
- [ ] Buscar datos mismatches en shadow_logs.jsonl
- [ ] Confirmar que no hay corrupciones de datos
- [ ] Revisar alertas de Slack del día anterior

### **Antes de Cambiar de Fase**

- [ ] ✅ Ejecutar suite de tests (44 tests)
- [ ] ✅ Verificar datos históricos coinciden (TARIFF_HISTORY)
- [ ] ✅ Validar que shadow logs muestran 0 mismatches
- [ ] ✅ Confirmar performance > baseline
- [ ] ✅ Review pull request de cambios realizados
- [ ] ✅ Aprobación de stakeholder (ops + product)

---

## 📈 Escalación

### **Si error_rate > 2% en CANARY (10%)**
```
1. Alert → Slack #etl-critical
2. Ops investigates → 30 min window
3. Si no resuelto → Rollback automático
4. Revert feature flag a DISABLED
5. Postmortem + root cause analysis
6. Fix en main branch
7. Restart FASE 1 cuando listo
```

### **Si response_time_p95 > 1.2s en CANARY**
```
1. Revisar query performance en v2 vs v1
2. ¿Índices faltantes?
3. ¿N+1 queries?
4. Si < 2% de usuarios afectados → CONTINUE
5. Si > 2% afectados → Rollback
```

### **Si data_mismatches > 5 en 1 hora**
```
1. Compare v1 vs v2 en shadow logs
2. ¿Qué campo no coincide?
3. ¿Problema en extract? transform? load?
4. Si < 0.1% de registros → CONTINUE con fix
5. Si > 0.1% de registros → Rollback + fix
```

---

## 📝 Documentación Posterior

Una vez FASE 4 completada:

1. **ARCH-002_FINAL_SUMMARY.md**
   - Resumen de arquitectura alcanzada
   - Métricas de éxito (líneas de código, tests, performance)
   - Timeline real vs planificado

2. **MIGRATION_POSTMORTEM.md**
   - Qué salió bien / mal
   - Lecciones aprendidas
   - Recomendaciones para futuras migraciones

3. **DEPRECATION_PLAN.md**
   - Cuándo remover v1 (después de 30 días en FULL)
   - Archivación de código legacy
   - Actualización de documentación

---

## 🎬 Estado Actual (26 Jan 2026)

**Pre-TAREA 7**:
- ✅ Shadow mode infrastructure ready
- ✅ Feature flags implemented
- ✅ All v2 ETLs validated
- ✅ Endpoints integrated with flag routing
- ⏳ Rollout plan (THIS DOCUMENT) ready

**Start TAREA 7**: Implement gradual rollout per phases above
**Est. Duration**: 3 weeks (Phase 1: 1 week, Phase 2: 1 week, Phase 3: 1 week + full deployment EOD)

