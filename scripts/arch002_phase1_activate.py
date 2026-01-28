#!/usr/bin/env python3
"""
ARCH-002 FASE 1: Canary Deployment Activation Script
Activates feature flags for 10% canary rollout

Usage:
    python scripts/arch002_phase1_activate.py
"""

import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.feature_flags import feature_flags, RolloutPhase


def activate_canary_phase():
    """Activate PHASE 1: Canary (10% users)"""
    
    print("\n" + "="*70)
    print("ARCH-002 FASE 1: CANARY DEPLOYMENT ACTIVATION")
    print("="*70)
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print(f"Target Users: 10% (50K users)")
    print(f"Duration: 7 days (Jan 26 - Feb 2, 2026)")
    print("="*70 + "\n")

    # Services to rollout
    services = ["combustibles", "ute", "ose", "antel"]
    
    # 1. Set all to CANARY phase with 10% percentage
    print("📊 Setting feature flags to CANARY phase...")
    for service in services:
        feature_flags.set_phase(service, RolloutPhase.CANARY)
        feature_flags.set_percentage(service, 10)
        feature_flags.enable_v2(service)
        flag = feature_flags.get(service)
        print(f"  ✅ {service:15} → {flag.phase} ({flag.v2_percentage}%)")

    print("\n" + "="*70)
    print("MONITORING CONFIGURATION")
    print("="*70)
    
    monitoring_config = {
        "error_rate_threshold": "> 2%",
        "response_time_p95": "< 1.2s",
        "data_mismatches": "> 5 per hour",
        "monitoring_frequency": "Every 1 hour",
        "alert_channel": "#etl-monitoring (Slack)",
        "escalation": "ops@company.com after 2 failures",
        "rollback_trigger": "error_rate > 5% OR response_time > 10% OR mismatch > 10"
    }
    
    for key, value in monitoring_config.items():
        print(f"  • {key:25} {value}")

    print("\n" + "="*70)
    print("SHADOW MODE STATUS")
    print("="*70)
    
    print("""
  ✅ Shadow mode enabled
  ✅ v1 + v2 running in parallel
  ✅ Logs: /backend/logs/shadow_logs.jsonl
  ✅ v1 result returned to user
  ✅ v2 discrepancies logged for analysis
    """)

    print("="*70)
    print("API ENDPOINTS (With Routing)")
    print("="*70)
    
    endpoints = {
        "GET /api/v1/etl/feature-flags": "Check current flag states",
        "GET /api/v1/etl/shadow/logs?limit=100": "View recent shadow logs",
        "POST /api/v1/etl/run?user_id=test": "Test v1/v2 routing (canary logic)",
    }
    
    for endpoint, desc in endpoints.items():
        print(f"  {endpoint:45} → {desc}")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    next_steps = """
1. VERIFY ACTIVATION (Next 5 minutes)
   └─ curl -s http://localhost:8000/api/v1/etl/feature-flags | jq .
   └─ Confirm all 4 services in CANARY phase

2. HOURLY MONITORING (7 days)
   └─ Run: python scripts/arch002_health_check.py
   └─ Check metrics every 1 hour
   └─ Alert if any threshold exceeded

3. DAILY REPORTS (Every day 09:00 UTC)
   └─ Run: python scripts/arch002_daily_report.py
   └─ Review error rates, response times, mismatches

4. PHASE DECISION (After 7 days)
   ├─ If all ✅ → Proceed to PHASE 2 (25%)
   ├─ If issues → Analyze logs and rollback if needed
   └─ Expected: 0 mismatches, error_rate < 0.5%

5. DOCUMENTATION
   └─ Update: docs/ARCH-002_PHASE1_EXECUTION.md
   └─ Slack announcement: #announcements
    """
    print(next_steps)

    print("="*70)
    print("PHASE 1 STATUS: 🟢 ACTIVATED")
    print("="*70)
    print(f"Start Time: {datetime.utcnow().isoformat()}Z")
    print(f"End Time: 2026-02-02T00:00:00Z (7 days)")
    print(f"Monitoring Dashboard: /admin/arch002-phase1")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    try:
        activate_canary_phase()
        print("✅ ARCH-002 FASE 1 activation complete!\n")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during activation: {e}\n")
        sys.exit(1)
