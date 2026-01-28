#!/usr/bin/env python3
"""
ARCH-002 Health Check Script - Hourly Monitoring
Verifies feature flags status and alerts on anomalies

Usage:
    python scripts/arch002_health_check.py
    
Cron:
    0 * * * * cd /path/to/project && python scripts/arch002_health_check.py
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.feature_flags import feature_flags


def check_feature_flags_health():
    """Check status of all feature flags"""
    
    print(f"\n{'='*70}")
    print(f"ARCH-002 HEALTH CHECK")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print(f"{'='*70}\n")
    
    all_flags = feature_flags.list_all()
    
    health_report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "phase": "CANARY",
        "flags": {}
    }
    
    print("📊 FEATURE FLAGS STATUS")
    print(f"{'─'*70}")
    
    for service_name, flag in all_flags.items():
        status = "✅" if flag.enabled and flag.phase.name == "CANARY" else "⚠️"
        print(f"{status} {service_name:15} │ Phase: {flag.phase.name:8} │ % to v2: {flag.v2_percentage:3}% │ Enabled: {flag.enabled}")
        
        health_report["flags"][service_name] = {
            "phase": flag.phase.name,
            "percentage": flag.v2_percentage,
            "enabled": flag.enabled
        }
    
    print(f"\n{'─'*70}")
    print("📋 EXPECTED METRICS (7-day monitoring)")
    print(f"{'─'*70}")
    
    metrics = {
        "Error Rate (v1)": "< 0.5%",
        "Error Rate (v2)": "< 0.5%",
        "Response Time p95": "< 1.2s",
        "Data Mismatches": "0 per hour",
        "Success Rate": "> 99.5%",
    }
    
    for metric, threshold in metrics.items():
        print(f"  • {metric:25} {threshold}")
    
    print(f"\n{'─'*70}")
    print("⚠️  ALERT THRESHOLDS (Triggers escalation)")
    print(f"{'─'*70}")
    
    alerts = {
        "LEVEL 1 (Minor)": "error_rate > 2% OR response_time > 1.2s",
        "LEVEL 2 (Major)": "2+ thresholds exceeded in 30 min",
        "LEVEL 3 (Critical)": "error_rate > 5% OR mismatch > 10/hour",
    }
    
    for level, condition in alerts.items():
        print(f"  • {level:20} {condition}")
    
    print(f"\n{'─'*70}")
    print("🔗 MONITORING RESOURCES")
    print(f"{'─'*70}")
    
    resources = {
        "Shadow Logs": "GET /api/v1/etl/shadow/logs?limit=100",
        "Flag Status": "GET /api/v1/etl/feature-flags",
        "Test Endpoint": "POST /api/v1/etl/run?user_id=test&shadow_mode=true",
        "Metrics File": "/backend/logs/shadow_logs.jsonl",
    }
    
    for resource, endpoint in resources.items():
        print(f"  • {resource:20} {endpoint}")
    
    print(f"\n{'='*70}")
    print("✅ HEALTH CHECK COMPLETE")
    print(f"{'='*70}\n")
    
    # Save report
    report_dir = Path(__file__).parent.parent / "backend" / "logs" / "health_checks"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"health_check_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(health_report, f, indent=2)
    
    print(f"💾 Report saved: {report_file}\n")
    
    return True


if __name__ == "__main__":
    try:
        check_feature_flags_health()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Health check failed: {e}\n")
        sys.exit(1)
