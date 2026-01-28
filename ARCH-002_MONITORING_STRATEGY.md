# ARCH-002: Monitoring & Alert Strategy

## 📊 Overview

Real-time monitoring dashboard for ARCH-002 phased rollout with automated alerts and escalation procedures.

---

## 🎯 Phase 1: Canary (10% Users) - Intensive Monitoring

**Duration**: 7 days | **Monitoring Frequency**: Every 1 hour

### Key Metrics to Track

```
┌─────────────────────────────────────────────────────┐
│ METRIC                 │ BASELINE  │ ALERT THRESHOLD │
├─────────────────────────────────────────────────────┤
│ Error Rate (v1)        │ < 0.5%    │ > 2%           │
│ Error Rate (v2)        │ < 0.5%    │ > 2%           │
│ Response Time p95      │ 800ms     │ > 1.2s         │
│ Data Mismatches/hour   │ 0         │ > 5            │
│ Records Processed      │ avg ±5%   │ ± 15%          │
│ Database Connections   │ < 50      │ > 80           │
│ Memory Usage           │ 156MB     │ > 200MB        │
└─────────────────────────────────────────────────────┘
```

### Alert Actions

**Alert Level 1** (Minor - Single threshold exceeded):
```
1. Send to #etl-monitoring Slack
2. Log to monitoring system
3. Alert ops@company.com
4. Continue monitoring hourly
5. Investigate root cause in background
```

**Alert Level 2** (Major - 2+ thresholds exceeded in 30 min):
```
1. Page on-call engineer
2. Send to #etl-critical Slack
3. Alert VP Engineering
4. Begin investigation immediately
5. Prepare rollback if needed
```

**Alert Level 3** (Critical - Error rate > 5% or data mismatch > 10):
```
1. IMMEDIATE ROLLBACK to v1
   POST /api/v1/etl/feature-flags/combustibles?phase=DISABLED
2. Page CTO + VP Engineering
3. Create incident ticket
4. Begin root cause analysis
5. Plan fix before next attempt
```

---

## 📈 Hourly Health Check

### Automated Script (Runs every 60 minutes)

```bash
#!/bin/bash
# health_check_canary.sh

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LIMIT=100

# Get recent shadow logs
curl -s http://localhost:8000/api/v1/etl/shadow/logs?limit=$LIMIT > /tmp/shadow_logs.json

# Extract metrics
ERROR_RATE=$(jq '.logs | map(select(.v1_error != null)) | length / (.| length) * 100' /tmp/shadow_logs.json)
V2_ERROR_RATE=$(jq '.logs | map(select(.v2_error != null)) | length / (. | length) * 100' /tmp/shadow_logs.json)
MISMATCHES=$(jq '.logs | map(select(.mismatches > 0)) | length' /tmp/shadow_logs.json)
AVG_V2_DURATION=$(jq '.logs | map(.v2_duration_seconds) | add / length' /tmp/shadow_logs.json)

# Check thresholds
if (( $(echo "$ERROR_RATE > 2" | bc -l) )); then
  echo "⚠️  ALERT: Error rate $ERROR_RATE% exceeds threshold 2%"
  curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"⚠️  ALERT: Error rate $ERROR_RATE%\"}" \
    $SLACK_WEBHOOK_URL
fi

if (( $(echo "$MISMATCHES > 5" | bc -l) )); then
  echo "🚨 CRITICAL: Found $MISMATCHES data mismatches"
  curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"🚨 CRITICAL: $MISMATCHES data mismatches detected\"}" \
    $SLACK_WEBHOOK_CRITICAL
fi

# Log results
echo "$TIMESTAMP | Error Rate: ${ERROR_RATE}% | V2 Error: ${V2_ERROR_RATE}% | Mismatches: ${MISMATCHES} | Avg V2 Duration: ${AVG_V2_DURATION}s" >> /var/log/etl_monitoring.log
```

### Hourly Report Template

```
═══════════════════════════════════════════════════════════════
ARCH-002 CANARY PHASE - HOURLY REPORT
═══════════════════════════════════════════════════════════════
Timestamp: 2026-01-27T09:00:00Z

PHASE 1 HEALTH METRICS
├─ Users on v2: 10% (500K)
├─ Monitoring Period: Hour 17/168
├─ Shadow Logs Reviewed: 100 most recent

KEY METRICS
├─ Error Rate (v1): 0.2% ✅
├─ Error Rate (v2): 0.3% ✅
├─ Response Time p95: 820ms ✅
├─ Data Mismatches: 0 ✅
└─ Records Processed: 4,850 (within ±5%) ✅

INCIDENTS
├─ None detected ✅

DATABASE
├─ Connections: 42 ✅
├─ Memory Usage: 162MB ✅

RECOMMENDATION
└─ Continue to next monitoring cycle ✅

Report Generated: 2026-01-27T09:00:00Z
───────────────────────────────────────────────────────────────
```

---

## 📊 Phase 2: Early Adopters (25% Users) - Daily Monitoring

**Duration**: 7 days | **Monitoring Frequency**: Every 4 hours (6x/day)

### Daily Summary Template

```
═══════════════════════════════════════════════════════════════
ARCH-002 PHASE 2 - DAILY SUMMARY
═══════════════════════════════════════════════════════════════
Date: 2026-02-03

PHASE 2 PROGRESS
├─ Users on v2: 25% (1.25M)
├─ Days in Phase: 3/7
└─ Status: ✅ ON TRACK

24-HOUR METRICS (24 monitoring cycles)
├─ Average Error Rate: 0.1% ✅
├─ Peak Error Rate: 0.4% ✅
├─ Average Response Time: 815ms ✅
├─ Peak Response Time: 950ms ✅
├─ Total Mismatches: 0 ✅
└─ Total Records: 115,200 ✅

MANUAL VALIDATION (Daily)
├─ Sample 1: User-ID #12345 (v1=v2) ✅
├─ Sample 2: User-ID #67890 (v1=v2) ✅
├─ Sample 3: User-ID #24680 (v1=v2) ✅
├─ Sample 4: User-ID #13579 (v1=v2) ✅
└─ Sample 5: User-ID #97531 (v1=v2) ✅

DECISION
└─ Continue to Phase 3 on Day 7 ✅

───────────────────────────────────────────────────────────────
```

### Manual Validation Procedure

```python
# Daily validation: Test 5 random users

import requests
import json

# Sample 5 random user IDs
user_ids = ["usr_12345", "usr_67890", "usr_24680", "usr_13579", "usr_97531"]

for user_id in user_ids:
    # Call with shadow_mode=true
    response = requests.get(
        "http://localhost:8000/api/v1/etl/run?shadow_mode=true",
        headers={"X-User-ID": user_id}
    )
    
    # Check recent shadow logs
    logs = requests.get("http://localhost:8000/api/v1/etl/shadow/logs?limit=1")
    latest = logs.json()["logs"][0]
    
    if latest["mismatches"] == 0:
        print(f"✅ {user_id}: Data matches (v1 == v2)")
    else:
        print(f"❌ {user_id}: Data mismatch detected!")
        print(json.dumps(latest, indent=2))
```

---

## 📈 Phase 3: Majority (50% → 100%) - Daily Monitoring

**Duration**: 6 days | **Monitoring Frequency**: Once per day (09:00 UTC)

### Daily Checklist

```
DATE: 2026-02-10 (Phase 3, Day 1)
USERS ON V2: 50%

MORNING CHECK (09:00 UTC)
═══════════════════════════════════════════════════════════════

[✅] Error Rate (24h avg) < 0.5%
    └─ Actual: 0.1%

[✅] Response Time p95 < 1s
    └─ Actual: 815ms

[✅] Data Mismatches = 0
    └─ Actual: 0 mismatches in 24h

[✅] Database Integrity
    └─ Actual: All tables consistent

[✅] API Health Check
    └─ Actual: All endpoints responding

[✅] Shadow Logs Review
    └─ Actual: 0 discrepancies

DECISION FOR PHASE 4
───────────────────────────────────────────────────────────────
Current Metrics: ✅ All Green
Recommendation: PROCEED to 100% deployment EOD

Action Items:
- Notify team of Phase 4 proceeding
- Update status dashboard
- Prepare Phase 4 transition communication
- Schedule Phase 4 completion ceremony

SIGN-OFF
───────────────────────────────────────────────────────────────
Verified by: [Name], [Title]
Date: 2026-02-10 09:00 UTC
```

---

## 🎯 Rollback Decision Tree

```
Event Detected?
│
├─ Error Rate > 2% for 30 min
│  ├─ Investigate (15 min)
│  ├─ If root cause identified & fixable → Continue monitoring
│  ├─ If root cause unknown → Rollback to DISABLED
│  └─ Rollback Command: POST /api/v1/etl/feature-flags/combustibles?phase=DISABLED
│
├─ Error Rate > 5% for ANY duration
│  ├─ IMMEDIATE ROLLBACK (< 2 min decision time)
│  └─ Rollback Command: POST /api/v1/etl/feature-flags/combustibles?phase=DISABLED
│
├─ Response Time p95 > 10% increase (880ms → 968ms)
│  ├─ Investigate (10 min)
│  ├─ If query performance issue → Rollback
│  └─ Rollback Command: POST /api/v1/etl/feature-flags/combustibles?phase=DISABLED
│
├─ Data Mismatches > 5 in 1 hour
│  ├─ Compare v1 vs v2 in shadow logs
│  ├─ Identify which field is mismatching
│  ├─ If > 0.1% of records affected → Rollback
│  └─ Rollback Command: POST /api/v1/etl/feature-flags/combustibles?phase=DISABLED
│
├─ Database Corruption Detected
│  ├─ IMMEDIATE ROLLBACK (< 1 min decision time)
│  └─ Rollback Command: POST /api/v1/etl/feature-flags/combustibles?phase=DISABLED
│
└─ No Issues → Continue Monitoring
   └─ Next Check: [Phase-dependent interval]
```

---

## 📞 Escalation Procedures

### On-Call Escalation Path

```
Level 1: Alert Condition Detected
└─ Action: Send to #etl-monitoring
   └─ Wait: 5 minutes for on-call to acknowledge

Level 2: No Response in 5 minutes
└─ Action: Send to #etl-critical + page on-call engineer
   └─ Wait: 2 minutes for confirmation

Level 3: Critical Condition (error_rate > 5%)
└─ Action: IMMEDIATE ROLLBACK + Page CTO
   └─ Notify: VP Engineering, Tech Lead, Team
```

### Rollback Verification

```bash
#!/bin/bash
# Verify rollback completed successfully

# 1. Confirm flag disabled
curl -s http://localhost:8000/api/v1/etl/feature-flags | \
  jq '.flags.combustibles.phase' | grep -q "DISABLED"
if [ $? -eq 0 ]; then
  echo "✅ Feature flag is DISABLED"
else
  echo "❌ Feature flag NOT disabled - CRITICAL"
  exit 1
fi

# 2. Confirm traffic on v1
curl -s http://localhost:8000/api/v1/etl/run | \
  jq '.source' | grep -q "v1"
if [ $? -eq 0 ]; then
  echo "✅ Traffic on v1"
else
  echo "❌ Traffic NOT on v1 - CRITICAL"
  exit 1
fi

# 3. Monitor for recovery
for i in {1..5}; do
  ERROR_RATE=$(curl -s http://localhost:8000/api/v1/etl/shadow/logs?limit=20 | \
    jq '.logs | map(select(.v1_error != null)) | length / (. | length) * 100')
  echo "Check $i: Error Rate = ${ERROR_RATE}%"
  sleep 60
done

echo "✅ Rollback verification complete"
```

---

## 📊 Monitoring Dashboard Setup (Recommended Tools)

### Option 1: Grafana + Prometheus
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'arch-002-etl'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/etl/metrics'
    scrape_interval: 60s

# Alerts
groups:
  - name: arch-002
    rules:
      - alert: HighErrorRate
        expr: error_rate > 2
        for: 30m
      - alert: HighResponseTime
        expr: response_time_p95 > 1200ms
        for: 10m
      - alert: DataMismatch
        expr: increase(data_mismatches[1h]) > 5
```

### Option 2: CloudWatch (AWS)
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_alarm(
    AlarmName='ARCH-002-HighErrorRate',
    MetricName='ErrorRate',
    Namespace='ETL',
    Statistic='Average',
    Period=300,
    EvaluationPeriods=1,
    Threshold=2.0,
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=['arn:aws:sns:...']
)
```

### Option 3: Datadog
```python
from datadog import initialize, api

# Configure Datadog
options = {
    'api_key': 'YOUR_API_KEY',
    'app_key': 'YOUR_APP_KEY'
}
initialize(**options)

# Create monitor
api.Monitor.create(
    type='metric alert',
    query='avg:etl.error_rate{service:combustibles} > 2',
    name='ARCH-002 High Error Rate',
    message='Error rate exceeded {{threshold}} | {{comparator}}',
    tags=['arch-002', 'critical']
)
```

---

## 🎬 Post-Deployment Monitoring

### After Phase 4 (100% v2 deployment)

Continue monitoring for 7 days post-deployment:
- **Frequency**: Daily (09:00 UTC)
- **Duration**: 7 days
- **Alert Threshold**: Same as Phase 1 (error_rate > 2%)

After 7 days:
- Move to weekly monitoring
- Review shadow logs (should all show v1=v2)
- Prepare for v1 code deprecation

---

## 📝 Monitoring Checklist

### Daily (Every Day of Rollout)

- [ ] Review error rates (v1 and v2)
- [ ] Check response times (p95)
- [ ] Look for data mismatches
- [ ] Verify database health
- [ ] Check system resources
- [ ] Review Slack alerts
- [ ] Update status dashboard

### Before Phase Progression

- [ ] Review 7-day (or phase duration) metrics
- [ ] Confirm 0 mismatches in shadow logs
- [ ] Performance benchmarks acceptable
- [ ] No unresolved incidents
- [ ] Team approval for next phase
- [ ] Document decision & sign-off

### Weekly (During Rollout)

- [ ] Generate comprehensive report
- [ ] Present metrics to stakeholders
- [ ] Review and update alert thresholds
- [ ] Plan for next phase
- [ ] Update team on progress

---

## 🚀 Success Metrics

Phase is successful when:
- ✅ Error rate < 0.5% (both v1 and v2)
- ✅ Response time p95 < 1s
- ✅ Data mismatches = 0
- ✅ Database integrity maintained
- ✅ No production incidents
- ✅ Performance same or better than v1

---

**Document Version**: 1.0  
**Last Updated**: January 26, 2026  
**Status**: Ready for Implementation

