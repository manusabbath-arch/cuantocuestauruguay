#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-https://preciosregulados-api.onrender.com}"
TIMEOUT="${TIMEOUT:-10}"

log() { printf "[%s] %s\n" "$(date -Iseconds)" "$*"; }

check_endpoint() {
  local path="$1"
  local expect_key="$2"
  local url="${API_BASE}${path}"
  log "Checking ${url}"
  local resp
  resp=$(curl -s --max-time "${TIMEOUT}" "${url}" || true)
  if echo "${resp}" | grep -q "${expect_key}"; then
    log "OK ${path}: found '${expect_key}'"
  else
    log "FAIL ${path}: missing '${expect_key}'"
    log "Response: ${resp}"
    return 1
  fi
}

main() {
  log "API_BASE=${API_BASE}"
  check_endpoint "/api/v1/etl/status" "jobs" || return 1
  check_endpoint "/api/v1/etl/alerts" "summary" || return 1
  check_endpoint "/api/v1/etl/debug/db-stats" "combustibles" || return 1
  log "All ETL health checks passed"
}

main "$@"
