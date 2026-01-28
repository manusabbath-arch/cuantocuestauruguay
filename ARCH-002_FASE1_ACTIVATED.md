# 🚀 ARCH-002 FASE 1: Canary Deployment - ACTIVATED

**Status**: ✅ **LIVE**  
**Activation Time**: January 26, 2026, 00:00 UTC  
**Target**: 10% of users (≈50,000)  
**Duration**: 7 days (Jan 26 - Feb 2, 2026)

---

## ✅ What Just Happened

### **Feature Flags Activated**

All 4 ETL services now running in **CANARY mode (10%)**:

```
✅ combustibles   CANARY  10%
✅ ute            CANARY  10%
✅ ose            CANARY  10%
✅ antel          CANARY  10%
```

### **Routing Logic Active**

- **90% of users** → v1 (original, proven)
- **10% of users** → v2 (new, being validated)
- **Selection**: Deterministic by `hash(user_id) % 100 < 10`
- **Consistency**: Same user always gets same version

### **Shadow Mode Enabled**

- v1 + v2 run in **parallel** for every request
- **v1 result** returned to user (safe)
- **v2 execution** logged separately
- **Discrepancies** trigger alerts

---

## 📊 What We're Monitoring

### **7-Day Monitoring Plan**

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Error Rate | > 2% | Page on-call |
| Response Time p95 | > 1.2s | Investigate |
| Data Mismatches | > 5/hour | Alert team |
| Success Rate | < 99% | Escalate |

### **Daily Reports**

Generated automatically at **09:00 UTC** each day:
- Error rates comparison (v1 vs v2)
- Performance metrics
- Data quality validation
- Recommendation (continue/escalate/rollback)

---

## 🔧 Available Commands

### **Check Current Status**

```bash
curl -s http://localhost:8000/api/v1/etl/feature-flags | jq
```

### **View Shadow Logs** (v1 vs v2 comparison)

```bash
curl -s http://localhost:8000/api/v1/etl/shadow/logs?limit=20 | jq
```

### **Test Canary Routing** (Manual)

```bash
# Will route to v1 or v2 depending on user_id hash
curl -X POST http://localhost:8000/api/v1/etl/run?user_id=test_user_1
```

### **Generate Health Report** (Anytime)

```bash
python scripts/arch002_health_check.py
```

### **Generate Daily Report** (Anytime)

```bash
python scripts/arch002_daily_report.py
```

---

## 📋 Key Documents

- **[ARCH-002_FASE1_EXECUTION.md](../ARCH-002_FASE1_EXECUTION.md)** - Daily execution log
- **[TAREA_7_ROLLOUT_PLAN.md](../TAREA_7_ROLLOUT_PLAN.md)** - Full 3-week strategy
- **[ARCH-002_MONITORING_STRATEGY.md](../ARCH-002_MONITORING_STRATEGY.md)** - Detailed monitoring

---

## 📅 Week-by-Week Plan

### **Days 1-6: Monitoring Phase**

```
Every Hour:     Health check (automated)
Every Day:      Daily report (09:00 UTC)
Actions:        Alert if thresholds exceeded
```

### **Day 7: Decision Review**

```
Feb 1, 09:00 UTC: Final report generation
Feb 1, 10:00 UTC: Team decision meeting

Options:
├─ All ✅ green  → PROCEED TO PHASE 2 (25%)
├─ Some issues   → Continue PHASE 1 (+7 days)
└─ Critical      → ROLLBACK to v1
```

---

## 🚀 Success Criteria

PHASE 1 is successful if:

- ✅ **Zero data mismatches** throughout 7 days
- ✅ **Error rate < 0.5%** for both v1 and v2
- ✅ **Response time p95 < 1.2s** (within 10% of baseline)
- ✅ **No production incidents**
- ✅ **No emergency rollbacks**

---

## 🔴 Rollback Scenarios

### **When Error Rate > 5%**

```
AUTOMATIC ROLLBACK TRIGGERED
├─ All flags → DISABLED
├─ 100% traffic → v1
├─ Time: < 2 minutes
└─ Incident: Investigation starts
```

### **When Data Mismatches > 10**

```
ALERT + INVESTIGATION
├─ Identify which field mismatches
├─ If > 0.1% of records → Rollback
└─ If < 0.1% → Continue with fix
```

### **When Response Time > 10% Increase**

```
INVESTIGATE
├─ Check query performance
├─ Compare v1 vs v2 logs
└─ Decision: Continue or Rollback
```

---

## 📞 Contact Info

**Monitoring Channel**: `#etl-monitoring` (Slack)  
**Alert Email**: `ops@company.com`  
**Escalation**: `CTO + VP Engineering` (if critical)

---

## 📊 Live Dashboards

```
API Status:
├─ GET /api/v1/etl/feature-flags        (Flag status)
├─ GET /api/v1/etl/shadow/logs?limit=100 (Recent logs)
└─ POST /api/v1/etl/run                 (Test routing)

Reports:
├─ scripts/arch002_health_check.py      (Hourly)
└─ scripts/arch002_daily_report.py      (Daily 09:00 UTC)
```

---

## 🎬 Timeline

```
Jan 26, 00:00 UTC: ✅ PHASE 1 START
Jan 27, 09:00 UTC: 📊 Report #1
Jan 28, 09:00 UTC: 📊 Report #2
Jan 29, 09:00 UTC: 📊 Report #3
Jan 30, 09:00 UTC: 📊 Report #4
Jan 31, 09:00 UTC: 📊 Report #5
Feb  1, 09:00 UTC: 📊 Report #6 + Decision
Feb  1, 10:00 UTC: 🎯 Team Review
Feb  2, 00:00 UTC: 🚀 PHASE 2 or Continue/Rollback
```

---

## ✨ What Happens Next

### **In 7 Days (Best Case)**

```
✅ All metrics green
✅ Zero incidents
✅ Data matches 100%
✅ Performance improved

→ PROCEED TO PHASE 2 (25% users)
```

### **In 7 Days (If Issues)**

```
⚠️  Some metrics exceeded
⚠️  Identified root cause
⚠️  Fix deployed

→ CONTINUE PHASE 1 (+7 days)
```

### **If Critical**

```
🔴 Error rate > 5%
🔴 Data corruption detected
🔴 Instant rollback triggered

→ ROLLBACK to v1 + Investigation
```

---

**Status**: 🟢 **PHASE 1 ACTIVE**  
**Next Check**: Every hour (automated)  
**Daily Report**: 09:00 UTC  
**Final Decision**: February 1, 2026

