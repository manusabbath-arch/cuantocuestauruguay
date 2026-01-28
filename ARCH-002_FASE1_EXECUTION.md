# ARCH-002 FASE 1: Canary Deployment Execution Log

**Status**: 🟢 **ACTIVE**  
**Start Date**: January 26, 2026 (00:00 UTC)  
**End Date**: February 2, 2026 (23:59 UTC)  
**Duration**: 7 days  
**Target**: 10% of users (≈50,000 users)  

---

## 🎯 Phase 1 Objectives

✅ Test v2 implementations in production with minimal risk  
✅ Validate data equivalence (v1 vs v2)  
✅ Monitor performance metrics  
✅ Detect and resolve issues before PHASE 2  

---

## 📊 Deployment Configuration

### Feature Flags Activated

```
Service          Phase      v2 Percentage    Status
─────────────────────────────────────────────────────
combustibles     CANARY     10%              ✅ Active
ute              CANARY     10%              ✅ Active
ose              CANARY     10%              ✅ Active
antel            CANARY     10%              ✅ Active
```

### Routing Logic

Users are selected deterministically via hash:
```
hash(user_id) % 100 < 10  →  Route to v2
Otherwise  →  Route to v1
```

This ensures:
- ✅ Consistent experience per user (same user always gets same version)
- ✅ Deterministic 10% split
- ✅ No need for session/cookie tracking

### Shadow Mode

Enabled concurrently:
- **v1 + v2** run in parallel
- **v1 result** returned to user
- **v2 discrepancies** logged for analysis
- **Location**: `/backend/logs/shadow_logs.jsonl`

---

## 📋 Monitoring Strategy

### Hourly Checks (0:00, 1:00, 2:00, ... UTC)

```bash
# Check feature flag status
python scripts/arch002_health_check.py

# Verify shadow logs
curl -s http://localhost:8000/api/v1/etl/shadow/logs?limit=100 | jq
```

### Daily Reports (09:00 UTC)

```bash
# Generate comprehensive daily report
python scripts/arch002_daily_report.py
```

### Metrics to Monitor

| Metric | Baseline | Alert Threshold | Status |
|--------|----------|-----------------|--------|
| Error Rate (v1) | < 0.5% | > 2% | ✅ |
| Error Rate (v2) | < 0.5% | > 2% | ✅ |
| Response Time p95 | 800ms | > 1.2s | ✅ |
| Data Mismatches | 0 | > 5/hour | ✅ |
| Records Processed | avg ±5% | ±15% | ✅ |
| Success Rate | > 99.5% | < 99% | ✅ |

---

## 📅 Daily Execution Log

### Day 1 - January 26, 2026

**Activation Time**: 00:00 UTC

```
✅ 00:00 Feature flags set to CANARY 10%
✅ 00:05 Health check #1 - All systems green
✅ 01:00 Health check #2 - Routing working
✅ 02:00 Health check #3 - No errors detected
✅ 03:00 Health check #4 - Shadow logs flowing
...
✅ 09:00 Daily Report #1 - No data yet (fresh start)
   └─ Next report: Jan 27 09:00 UTC
```

### Day 2 - January 27, 2026

**Expected Activities**:
```
⏳ 09:00 Daily Report #2
   ├─ Analyze 24h of shadow logs
   ├─ Check error rates
   ├─ Verify data mismatches = 0
   └─ Decision: Continue if ✅ all green

⏳ Every hour: Spot checks
   └─ Sample shadow logs for anomalies
```

### Day 3-6 - January 28-31, 2026

**Routine Monitoring**:
```
⏳ Daily 09:00 UTC: Generate comprehensive report
⏳ Hourly spot checks: Alert on threshold breach
⏳ Document any anomalies for investigation
```

### Day 7 - February 1, 2026

**Pre-Transition Review**:
```
✅ 09:00 Final daily report for PHASE 1
✅ 10:00 Decision review meeting
   ├─ If all ✅ → Approve PHASE 2 (25%)
   ├─ If issues → Analyze and plan fixes
   └─ If critical → Rollback to v1
```

### Day 8 - February 2, 2026

**Transition or Continue**:
```
Option A (Expected): Proceed to PHASE 2
  └─ Update feature flags to 25%
  └─ Extend monitoring 7 more days

Option B (If issues): Resolve and restart
  └─ Keep PHASE 1 active 7 more days
  └─ Fix identified issues

Option C (If critical): Rollback
  └─ Set all flags to DISABLED
  └─ Route 100% traffic back to v1
  └─ Analyze root causes
```

---

## 🔧 Quick Reference Commands

### Check Feature Flags Status

```bash
curl -s http://localhost:8000/api/v1/etl/feature-flags | jq
```

**Expected Output**:
```json
{
  "flags": {
    "combustibles": {
      "phase": "CANARY",
      "percentage": 10,
      "v2_enabled": true
    },
    "ute": { "phase": "CANARY", "percentage": 10, "v2_enabled": true },
    "ose": { "phase": "CANARY", "percentage": 10, "v2_enabled": true },
    "antel": { "phase": "CANARY", "percentage": 10, "v2_enabled": true }
  }
}
```

### View Recent Shadow Logs

```bash
# Get last 20 shadow logs
curl -s http://localhost:8000/api/v1/etl/shadow/logs?limit=20 | jq '.logs[] | {
  timestamp,
  etl_name,
  v1_error,
  v2_error,
  mismatches,
  v1_duration_seconds,
  v2_duration_seconds
}'
```

### Test Canary Routing (Manual)

```bash
# Test with specific user_id (canary)
curl -X POST http://localhost:8000/api/v1/etl/run?user_id=test_user_1 | jq '.source'
# Expected: "v2" (if hash routes to v2) or "v1" (if routes to v1)

# Test with shadow mode enabled
curl -X POST http://localhost:8000/api/v1/etl/run?shadow_mode=true | jq
# Expected: v1 result with v2 logged separately
```

### Generate Health Check Report

```bash
python scripts/arch002_health_check.py
```

### Generate Daily Report

```bash
python scripts/arch002_daily_report.py
```

---

## ⚠️ Rollback Procedures

### Scenario 1: Minor Issue (error_rate 1-2%)

```
1. Alert team → #etl-critical
2. Investigate for 30 minutes
3. If root cause found → Deploy fix
4. If unknown → Escalate to Scenario 2
```

### Scenario 2: Major Issue (error_rate 2-5%)

```
1. IMMEDIATE alert → ops@company.com
2. Page on-call engineer
3. Begin investigation (1 hour window)
4. If not resolved → Execute Scenario 3
```

### Scenario 3: Critical (error_rate > 5%)

```
1. EXECUTE ROLLBACK (< 2 min decision time)
   curl -X POST \
     http://localhost:8000/api/v1/etl/feature-flags/combustibles?phase=DISABLED \
     && curl -X POST \
     http://localhost:8000/api/v1/etl/feature-flags/ute?phase=DISABLED \
     && curl -X POST \
     http://localhost:8000/api/v1/etl/feature-flags/ose?phase=DISABLED \
     && curl -X POST \
     http://localhost:8000/api/v1/etl/feature-flags/antel?phase=DISABLED

2. Verify rollback: 100% traffic back to v1
3. Create incident ticket
4. Begin root cause analysis
5. Plan fix and retry when ready
```

---

## 📞 Escalation Contacts

| Level | Contact | Notification |
|-------|---------|--------------|
| 🟡 Alert (threshold > 80%) | ops@company.com | Email + Slack |
| 🔴 Critical (error_rate > 5%) | CTO + VP Eng | Page + Email + Slack |
| 🟣 Incident (data loss) | All Engineering | All channels |

---

## ✅ Success Criteria

PHASE 1 is successful if:
- ✅ **Zero data mismatches** throughout 7 days
- ✅ **Error rate < 0.5%** for both v1 and v2
- ✅ **Response time p95 < 1.2s** (or within 10% of baseline)
- ✅ **No production incidents**
- ✅ **No emergency rollbacks**
- ✅ **Team approval** to proceed to PHASE 2

---

## 📝 Daily Updates Template

Use this template for daily Slack updates:

```
🔄 ARCH-002 FASE 1 - Day X Update

Metrics (24h):
├─ Error Rate v1: X%  [✅/⚠️/❌]
├─ Error Rate v2: X%  [✅/⚠️/❌]
├─ Response Time p95: Xms  [✅/⚠️/❌]
├─ Data Mismatches: X  [✅/⚠️/❌]
└─ Status: 🟢 HEALTHY / 🟡 CAUTION / 🔴 ALERT

Incidents: None / [List]

Next: Continue monitoring / Escalate / Proceed to PHASE 2

Report: [Link to full report]
```

---

## 📊 Documents Referenced

- 📖 [TAREA_7_ROLLOUT_PLAN.md](../TAREA_7_ROLLOUT_PLAN.md) - Full rollout strategy
- 📖 [ARCH-002_MONITORING_STRATEGY.md](../ARCH-002_MONITORING_STRATEGY.md) - Detailed monitoring
- 📖 [ARCH-002_COMPREHENSIVE_SUMMARY.md](../ARCH-002_COMPREHENSIVE_SUMMARY.md) - Project overview

---

## 🎬 Status Timeline

```
Jan 26, 00:00 UTC: PHASE 1 START (10% canary) ✅
Jan 27, 09:00 UTC: Daily Report #1
Jan 28, 09:00 UTC: Daily Report #2
Jan 29, 09:00 UTC: Daily Report #3
Jan 30, 09:00 UTC: Daily Report #4
Jan 31, 09:00 UTC: Daily Report #5
Feb 01, 09:00 UTC: Daily Report #6 + DECISION REVIEW
Feb 01, 10:00 UTC: Team decision → PHASE 2 or Continue/Rollback
Feb 02, 00:00 UTC: PHASE 1 END (or continue if issues)
```

---

**Document Version**: 1.0  
**Last Updated**: January 26, 2026  
**Status**: 🟢 ACTIVE  

