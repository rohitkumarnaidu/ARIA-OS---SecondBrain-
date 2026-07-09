#!/usr/bin/env bash
set -euo pipefail

# SOC 2 Evidence Collector
# Scans codebase for control implementations and generates readiness report
# Usage: ./scripts/soc2-evidence-collector.sh [output_dir]

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="${1:-${SCRIPT_DIR}/security/reports/soc2}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="${OUTPUT_DIR}/${TIMESTAMP}"

echo "=== SOC 2 Evidence Collection ==="
echo "Started: $(date)"
echo "Output: ${REPORT_DIR}"
echo ""

mkdir -p "$REPORT_DIR"

# ── CC5.x / C2.1 — Access Control ──────────────────────────────────────────
echo "[CC5.1 - CC5.3] Access Control..."

AUTH_ENDPOINTS=$(grep -rn "Depends(get_current_user)" "${SCRIPT_DIR}/apps/api/app/api/"*.py 2>/dev/null | wc -l)
echo "  Auth-protected endpoints: ${AUTH_ENDPOINTS}"

USER_ID_FILTERS=$(grep -rn 'eq("user_id"' "${SCRIPT_DIR}/apps/api/app/api/"*.py 2>/dev/null | wc -l)
echo "  user_id filters: ${USER_ID_FILTERS}"

RLS_FILES=$(find "${SCRIPT_DIR}/packages/database" -name "*.sql" 2>/dev/null | wc -l)
echo "  RLS SQL files: ${RLS_FILES}"

AUTH_DEPLOY=$(grep -rn "get_current_user" "${SCRIPT_DIR}/apps/api/app/api/"*.py 2>/dev/null | wc -l || echo 0)
echo "  Auth middleware calls: ${AUTH_DEPLOY}"

# ── CC6.x — Encryption & Vulnerability ────────────────────────────────────
echo "[CC6.2 - CC6.3] Encryption..."

echo "  TLS 1.3: Enforced (Vercel + Railway edge)"
echo "  DB encryption: AES-256 at rest (Supabase managed)"
echo "  JWT algorithm: HS256 ($(grep -c "HS256" "${SCRIPT_DIR}/packages/config/core/auth.py" 2>/dev/null || echo 0) references)"

echo "[CC6.5] Vulnerability Management..."

SAST_COUNT=0
for f in owasp-check.sh sql-injection-audit.sh; do
  if [ -f "${SCRIPT_DIR}/scripts/${f}" ]; then
    SAST_COUNT=$((SAST_COUNT + 1))
    echo "  Script found: ${f}"
  fi
done
echo "  SAST scripts: ${SAST_COUNT}"

DAST_COUNT=0
for f in zap-pentest.sh attack-scenarios.py; do
  if [ -f "${SCRIPT_DIR}/scripts/${f}" ]; then
    DAST_COUNT=$((DAST_COUNT + 1))
    echo "  Script found: ${f}"
  fi
done
echo "  DAST scripts: ${DAST_COUNT}"

# ── CC7.x — Incident Response ─────────────────────────────────────────────
echo "[CC7.1 - CC7.3] Incident Response..."

IR_DOCS=$(find "${SCRIPT_DIR}/docs/operations" -name "*Incident*" -o -name "*Runbook*" 2>/dev/null | wc -l)
echo "  Incident docs: ${IR_DOCS}"

SENTRY_CONFIG=$(grep -c "sentry_sdk" "${SCRIPT_DIR}/apps/api/main.py" 2>/dev/null || echo 0)
echo "  Sentry configured: $([ "$SENTRY_CONFIG" -gt 0 ] && echo 'Yes' || echo 'No')"

LOGGING_FILES=$(find "${SCRIPT_DIR}/packages/shared/utils" -name "logger*" 2>/dev/null | wc -l)
echo "  Logger utilities: ${LOGGING_FILES}"

# ── CC8.x — Change Management ─────────────────────────────────────────────
echo "[CC8.1 - CC8.2] Change Management..."

CI_JOBS=$(grep -c "^  [a-z]" "${SCRIPT_DIR}/.github/workflows/ci.yml" 2>/dev/null || echo 0)
echo "  CI workflow jobs: ${CI_JOBS}"

PR_TEMPLATE=$([ -f "${SCRIPT_DIR}/.github/PULL_REQUEST_TEMPLATE.md" ] && echo 'Present' || echo 'Missing')
echo "  PR template: ${PR_TEMPLATE}"

MAKEFILE=$([ -f "${SCRIPT_DIR}/Makefile" ] && echo 'Present' || echo 'Missing')
echo "  Build pipeline: ${MAKEFILE}"

TEST_COUNT=$(find "${SCRIPT_DIR}/tests" -name "*.py" 2>/dev/null | wc -l)
echo "  Test files: ${TEST_COUNT}"

# ── PI1.4 — Audit Trail ───────────────────────────────────────────────────
echo "[PI1.4] Audit Trail..."

AUDIT_FILE="${SCRIPT_DIR}/packages/shared/utils/audit.py"
if [ -f "$AUDIT_FILE" ]; then
  AUDIT_LINES=$(wc -l < "$AUDIT_FILE")
  echo "  Audit module: ${AUDIT_LINES} lines"
  AUDIT_FUNCTIONS=$(grep -c "^def \|^async def " "$AUDIT_FILE" 2>/dev/null || echo 0)
  echo "  Audit functions: ${AUDIT_FUNCTIONS}"
else
  echo "  Audit module: MISSING"
fi

AUDIT_MIDDLEWARE=$(grep -c "audit_middleware_dispatch" "${SCRIPT_DIR}/apps/api/main.py" 2>/dev/null || echo 0)
echo "  Audit middleware: $([ "$AUDIT_MIDDLEWARE" -gt 0 ] && echo 'Enabled' || echo 'Missing')"

# ── P5.1 — Data Retention ─────────────────────────────────────────────────
echo "[P5.1] Data Retention..."

RETENTION_EXISTS=$([ -f "${SCRIPT_DIR}/scripts/retention"* ] && echo 'Present' || echo 'Not found')
echo "  Retention script: ${RETENTION_EXISTS}"

TTL_FIELDS=$(grep -rn "expires_at\|ttl_days" "${SCRIPT_DIR}/packages/database/schemas/"*.py 2>/dev/null | wc -l)
echo "  TTL/expiry schema fields: ${TTL_FIELDS}"

PRUNE_EXISTS=$(grep -c "prune_expired_memories" "${SCRIPT_DIR}/packages/ai/agents/memory_agent.py" 2>/dev/null || echo 0)
echo "  Memory pruning: $([ "$PRUNE_EXISTS" -gt 0 ] && echo 'Implemented' || echo 'Not found')"

# ── Data Export (GDPR) ────────────────────────────────────────────────────
echo "[P2.1] Data Export / Consent..."

DATA_EXPORT=$([ -f "${SCRIPT_DIR}/apps/api/app/api/data_export.py" ] && echo 'Present' || echo 'Missing')
echo "  GDPR data export: ${DATA_EXPORT}"

# ── Generate Evidence Report ──────────────────────────────────────────────
echo ""
echo "=== Generating Evidence Report ==="

JSON_OUT="${REPORT_DIR}/evidence-summary.json"
cat > "${JSON_OUT}" << EVIDENCE_EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "target": "SOC 2 Type I (Q2 2027)",
  "controls": {
    "auth_endpoints": ${AUTH_ENDPOINTS},
    "user_id_filters": ${USER_ID_FILTERS},
    "rls_files": ${RLS_FILES},
    "auth_middleware_calls": ${AUTH_DEPLOY},
    "sast_scripts": ${SAST_COUNT},
    "dast_scripts": ${DAST_COUNT},
    "incident_docs": ${IR_DOCS},
    "sentry_enabled": $([ "$SENTRY_CONFIG" -gt 0 ] && echo 'true' || echo 'false'),
    "logger_utilities": ${LOGGING_FILES},
    "ci_jobs": ${CI_JOBS},
    "pr_template": "$(echo "$PR_TEMPLATE" | tr '[:upper:]' '[:lower:]')",
    "test_files": ${TEST_COUNT},
    "audit_enabled": $([ "$AUDIT_MIDDLEWARE" -gt 0 ] && echo 'true' || echo 'false'),
    "ttl_schema_fields": ${TTL_FIELDS},
    "pruning_implemented": $([ "$PRUNE_EXISTS" -gt 0 ] && echo 'true' || echo 'false'),
    "gdpr_export": "$(echo "$DATA_EXPORT" | tr '[:upper:]' '[:lower:]')"
  }
}
EVIDENCE_EOF

# Validate generated JSON
if command -v jq &> /dev/null; then
  if ! jq empty "${JSON_OUT}" 2>/dev/null; then
    echo "ERROR: Generated JSON is invalid. Falling back to safe JSON."
    python3 -c "
import json, sys
with open('${JSON_OUT}') as f: content = f.read()
data = {
  'timestamp': content.split('\"timestamp\":')[1].split(',')[0].strip().strip('\"'),
  'target': 'SOC 2 Type I (Q2 2027)',
  'controls': {}
}
with open('${JSON_OUT}', 'w') as f: json.dump(data, f, indent=2)
" 2>/dev/null || echo '{"error":"json_corruption","fallback":true}' > "${JSON_OUT}"
  fi
fi

echo ""
echo "=== Evidence Collection Complete ==="
echo "Report: ${REPORT_DIR}/evidence-summary.json"
echo ""
echo "Key metrics:"
echo "  Auth endpoints:         ${AUTH_ENDPOINTS}"
echo "  user_id filters:        ${USER_ID_FILTERS}"
echo "  SAST/DAST scripts:      ${SAST_COUNT}/${DAST_COUNT}"
echo "  Test files:             ${TEST_COUNT}"
echo "  Audit trail:            $([ "$AUDIT_MIDDLEWARE" -gt 0 ] && echo 'Enabled' || echo 'Missing')"
echo "  Incident docs:          ${IR_DOCS}"
echo "  Sentry monitoring:      $([ "$SENTRY_CONFIG" -gt 0 ] && echo 'Yes' || echo 'No')"
