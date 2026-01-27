#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
TIMEOUT="${TIMEOUT:-15}"

log() { printf "[%s] %s\n" "$(date -Iseconds)" "$*"; }
error() { log "ERROR: $*"; return 1; }

smoke_test_alerts() {
  log "Starting ETL alerts smoke tests"
  log "API_BASE=${API_BASE}"
  
  # Test 1: Check baseline alerts (should be empty or few)
  log "Test 1: Checking baseline alerts..."
  BASELINE=$(curl -s --max-time "${TIMEOUT}" "${API_BASE}/api/v1/etl/alerts" || echo '{"summary":{}}')
  BASELINE_COUNT=$(echo "${BASELINE}" | grep -o '"total"' | wc -l)
  log "Baseline alerts retrieved: $(echo ${BASELINE} | jq -r '.summary.total // 0')"
  
  # Test 2: Try forcing an ETL failure (simulate with bad input)
  # Note: This is a placeholder - actual test requires DB manipulation or fake endpoint
  log "Test 2: Simulating ETL execution..."
  ETLSTATUS=$(curl -s --max-time "${TIMEOUT}" "${API_BASE}/api/v1/etl/status" || echo '{}')
  log "ETL status: $(echo ${ETLSTATUS} | jq -r '.message // "N/A"')"
  
  # Test 3: Check alerts after ETL run
  log "Test 3: Checking alerts post-ETL..."
  ALERTS=$(curl -s --max-time "${TIMEOUT}" "${API_BASE}/api/v1/etl/alerts" || echo '{"summary":{}}')
  ALERT_TOTAL=$(echo "${ALERTS}" | jq -r '.summary.total // 0')
  log "Total alerts: ${ALERT_TOTAL}"
  
  # Test 4: Validate alert structure
  log "Test 4: Validating alert structure..."
  HAS_SUMMARY=$(echo "${ALERTS}" | jq 'has("summary")')
  HAS_RECENT=$(echo "${ALERTS}" | jq 'has("recent_alerts")')
  
  if [[ "${HAS_SUMMARY}" == "true" ]] && [[ "${HAS_RECENT}" == "true" ]]; then
    log "✓ Alert structure valid"
  else
    error "Alert structure invalid"
  fi
  
  # Test 5: Healthcheck should still pass
  log "Test 5: Verifying healthcheck still passes..."
  HC=$(curl -s --max-time "${TIMEOUT}" "${API_BASE}/api/v1/etl/status" || echo '{}')
  if echo "${HC}" | grep -q "jobs"; then
    log "✓ Healthcheck passed"
  else
    error "Healthcheck failed"
  fi
  
  log "All smoke tests completed successfully!"
}

main() {
  smoke_test_alerts "$@"
}

main "$@"
