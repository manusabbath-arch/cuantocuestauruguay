#!/usr/bin/env python3
"""
ARCH-002 Daily Report Generator
Summarizes 24-hour metrics for FASE 1 monitoring

Usage:
    python scripts/arch002_daily_report.py
    
Cron:
    0 9 * * * cd /path/to/project && python scripts/arch002_daily_report.py >> logs/arch002_daily_reports.log
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


def parse_shadow_logs():
    """Parse shadow_logs.jsonl and extract metrics"""
    
    log_file = Path(__file__).parent.parent / "backend" / "logs" / "shadow_logs.jsonl"
    
    if not log_file.exists():
        print("⚠️  No shadow logs found yet. Starting fresh monitoring.")
        return None
    
    metrics = {
        "total_runs": 0,
        "v1_errors": 0,
        "v2_errors": 0,
        "mismatches": 0,
        "total_mismatches": 0,
        "v1_durations": [],
        "v2_durations": [],
        "by_etl": defaultdict(lambda: {"runs": 0, "errors": 0, "mismatches": 0})
    }
    
    # Read last 24 hours of logs
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                
                # Check if within 24h window
                entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                if entry_time < cutoff_time:
                    continue
                
                metrics["total_runs"] += 1
                etl_name = entry.get("etl_name", "unknown")
                metrics["by_etl"][etl_name]["runs"] += 1
                
                if entry.get("v1_error"):
                    metrics["v1_errors"] += 1
                    metrics["by_etl"][etl_name]["errors"] += 1
                
                if entry.get("v2_error"):
                    metrics["v2_errors"] += 1
                
                if entry.get("mismatches", 0) > 0:
                    metrics["mismatches"] += 1
                    metrics["total_mismatches"] += entry["mismatches"]
                    metrics["by_etl"][etl_name]["mismatches"] += entry["mismatches"]
                
                if entry.get("v1_duration_seconds"):
                    metrics["v1_durations"].append(entry["v1_duration_seconds"])
                
                if entry.get("v2_duration_seconds"):
                    metrics["v2_durations"].append(entry["v2_duration_seconds"])
            
            except json.JSONDecodeError:
                continue
    
    return metrics


def generate_daily_report():
    """Generate and print daily report"""
    
    print("\n" + "="*80)
    print("ARCH-002 FASE 1: DAILY MONITORING REPORT")
    print("="*80)
    print(f"Report Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Coverage: Last 24 hours")
    print("="*80 + "\n")
    
    metrics = parse_shadow_logs()
    
    if metrics is None or metrics["total_runs"] == 0:
        print("📊 No data collected yet (monitoring just started)")
        print("   Next report will be available tomorrow.\n")
        return
    
    # Overall Health
    print("📊 OVERALL HEALTH (24h)")
    print("─" * 80)
    
    v1_error_rate = (metrics["v1_errors"] / metrics["total_runs"] * 100) if metrics["total_runs"] > 0 else 0
    v2_error_rate = (metrics["v2_errors"] / metrics["total_runs"] * 100) if metrics["total_runs"] > 0 else 0
    mismatch_rate = (metrics["total_mismatches"] / metrics["total_runs"] * 100) if metrics["total_runs"] > 0 else 0
    
    print(f"  Total ETL Runs:        {metrics['total_runs']:>6}")
    print(f"  v1 Error Rate:         {v1_error_rate:>6.2f}% {'✅' if v1_error_rate < 0.5 else '⚠️'}")
    print(f"  v2 Error Rate:         {v2_error_rate:>6.2f}% {'✅' if v2_error_rate < 0.5 else '⚠️'}")
    print(f"  Data Mismatches:       {metrics['total_mismatches']:>6} {'✅' if metrics['total_mismatches'] == 0 else '⚠️'}")
    print(f"  Mismatch Rate:         {mismatch_rate:>6.2f}% {'✅' if mismatch_rate == 0 else '⚠️'}")
    
    # Performance
    if metrics["v1_durations"]:
        v1_avg = sum(metrics["v1_durations"]) / len(metrics["v1_durations"])
    else:
        v1_avg = 0
    
    if metrics["v2_durations"]:
        v2_avg = sum(metrics["v2_durations"]) / len(metrics["v2_durations"])
    else:
        v2_avg = 0
    
    print("\n⚡ PERFORMANCE (24h Average)")
    print("─" * 80)
    
    if v1_avg > 0:
        print(f"  v1 Avg Duration:       {v1_avg:>6.2f}s")
    if v2_avg > 0:
        print(f"  v2 Avg Duration:       {v2_avg:>6.2f}s")
        if v1_avg > 0:
            improvement = ((v1_avg - v2_avg) / v1_avg * 100)
            print(f"  v2 Improvement:        {improvement:>6.1f}% {'🚀' if improvement > 0 else ''}")
    
    # Per-ETL breakdown
    print("\n📋 PER-SERVICE BREAKDOWN (24h)")
    print("─" * 80)
    print(f"  {'Service':<15} {'Runs':>6} {'Errors':>6} {'Mismatches':>10} {'Status':>10}")
    print("  " + "─" * 76)
    
    for etl_name in ["combustibles", "ute", "ose", "antel"]:
        if etl_name in metrics["by_etl"]:
            data = metrics["by_etl"][etl_name]
            status = "✅ OK" if data["errors"] == 0 and data["mismatches"] == 0 else "⚠️  WARNING"
            print(f"  {etl_name:<15} {data['runs']:>6} {data['errors']:>6} {data['mismatches']:>10} {status:>10}")
    
    # Status Assessment
    print("\n🎯 PHASE 1 STATUS ASSESSMENT")
    print("─" * 80)
    
    assessment = {
        "v1_stable": v1_error_rate < 0.5,
        "v2_stable": v2_error_rate < 0.5,
        "data_valid": metrics['total_mismatches'] == 0,
        "performance_ok": v2_avg > 0 and v2_avg < 1.2,
    }
    
    if all(assessment.values()):
        status = "🟢 HEALTHY - All metrics within thresholds"
    elif sum(assessment.values()) >= 3:
        status = "🟡 CAUTION - Review failed metrics"
    else:
        status = "🔴 ALERT - Multiple thresholds exceeded"
    
    print(f"  Overall Status:        {status}")
    print(f"  v1 Stability:          {'✅' if assessment['v1_stable'] else '❌'}")
    print(f"  v2 Stability:          {'✅' if assessment['v2_stable'] else '❌'}")
    print(f"  Data Validity:         {'✅' if assessment['data_valid'] else '❌'}")
    print(f"  Performance OK:        {'✅' if assessment['performance_ok'] else '❌'}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("─" * 80)
    
    if all(assessment.values()):
        print("  ✅ Continue Phase 1 monitoring")
        print("  ✅ All metrics within expected thresholds")
        print("  ⏳ Proceed to Phase 2 (25%) if no issues in 7 days")
    else:
        print("  ⚠️  Investigate failed metrics")
        print("  ⚠️  Check shadow logs for discrepancies")
        print("  ⚠️  Consider rollback if error_rate > 5%")
    
    print("\n" + "="*80)
    print("END OF REPORT")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        generate_daily_report()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Report generation failed: {e}\n")
        sys.exit(1)
