#!/usr/bin/env bash
set -euo pipefail

# SOC 2 Readiness Score Calculator
# Runs evidence collector and scores readiness by TSC category
# Usage: ./scripts/soc2-readiness-score.sh

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/security/reports/soc2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="${OUTPUT_DIR}/${TIMESTAMP}"

echo "=== SOC 2 Readiness Score ==="
echo ""

# Run evidence collector
bash "${SCRIPT_DIR}/scripts/soc2-evidence-collector.sh" "${REPORT_DIR}" 2>/dev/null

EVIDENCE="${REPORT_DIR}/evidence-summary.json"
if [ ! -f "$EVIDENCE" ]; then
  echo "ERROR: Evidence collection failed"
  exit 1
fi

# Extract metrics using grep (avoid jq dependency)
AUTH=$(grep -o '"auth_endpoints": [0-9]*' "$EVIDENCE" | grep -o '[0-9]*')
UID_FILTERS=$(grep -o '"user_id_filters": [0-9]*' "$EVIDENCE" | grep -o '[0-9]*')
SAST=$(grep -o '"sast_scripts": [0-9]*' "$EVIDENCE" | grep -o '[0-9]*')
DAST=$(grep -o '"dast_scripts": [0-9]*' "$EVIDENCE" | grep -o '[0-9]*')
TESTS=$(grep -o '"test_files": [0-9]*' "$EVIDENCE" | grep -o '[0-9]*')
CI=$(grep -o '"ci_jobs": [0-9]*' "$EVIDENCE" | grep -o '[0-9]*')
AUDIT=$(grep -o '"audit_enabled": [a-z]*' "$EVIDENCE" | grep -o '[a-z]*')
SENTRY=$(grep -o '"sentry_enabled": [a-z]*' "$EVIDENCE" | grep -o '[a-z]*')
GDPR=$(grep -o '"gdpr_export": "[a-z]*"' "$EVIDENCE" | grep -o '[a-z]*' | tr -d '"')

# ── Category Scoring ──────────────────────────────────────────────────────

# Security (CC1-CC9): auth coverage + SAST/DAST + audit + CI
SCORE_AUTH=$([ "$AUTH" -ge 50 ] && echo 100 || echo $((AUTH * 2)))
SCORE_UID=$([ "$UID_FILTERS" -ge 20 ] && echo 100 || echo $((UID_FILTERS * 5)))
SCORE_SAST=$([ "$SAST" -ge 2 ] && echo 100 || echo $((SAST * 50)))
SCORE_DAST=$([ "$DAST" -ge 1 ] && echo 50 || echo 0)
SCORE_AUDIT=$([ "$AUDIT" = "true" ] && echo 100 || echo 0)
SCORE_CI=$([ "$CI" -ge 5 ] && echo 100 || echo $((CI * 20)))
SCORE_TESTS=$([ "$TESTS" -ge 50 ] && echo 100 || echo $((TESTS * 2)))
SCORE_SENTRY=$([ "$SENTRY" = "true" ] && echo 100 || echo 0)

SECURITY_SCORE=$(( (SCORE_AUTH + SCORE_UID + SCORE_SAST + SCORE_DAST + SCORE_AUDIT + SCORE_CI + SCORE_TESTS + SCORE_SENTRY) / 8 ))

# Availability (A1): CI + monitoring + tests
AVAIL_SCORE=$(( (SCORE_CI + SCORE_SENTRY + SCORE_TESTS) / 3 ))

# Confidentiality (C1-C2): auth + UID filters
CONF_SCORE=$(( (SCORE_AUTH + SCORE_UID) / 2 ))

# Processing Integrity (PI1): audit + tests
PI_SCORE=$(( (SCORE_AUDIT + SCORE_TESTS) / 2 ))

# Privacy (P1-P6): GDPR + audit
PRIV_SCORE=$SCORE_AUDIT
[ "$GDPR" = "present" ] && PRIV_SCORE=$((PRIV_SCORE + 100)) || PRIV_SCORE=$((PRIV_SCORE + 0))
PRIV_SCORE=$((PRIV_SCORE / 2))

# ── Overall ───────────────────────────────────────────────────────────────
OVERALL=$(( (SECURITY_SCORE * 40 + AVAIL_SCORE * 20 + CONF_SCORE * 15 + PI_SCORE * 15 + PRIV_SCORE * 10) / 100 ))

# ── Report ────────────────────────────────────────────────────────────────
cat > "${REPORT_DIR}/readiness-report.json" << REPORT_EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "target": "SOC 2 Type I (Q2 2027)",
  "scores": {
    "security_cc": ${SECURITY_SCORE},
    "availability_a1": ${AVAIL_SCORE},
    "confidentiality_c": ${CONF_SCORE},
    "processing_integrity_pi": ${PI_SCORE},
    "privacy_p": ${PRIV_SCORE},
    "overall": ${OVERALL}
  },
  "gaps": {
    "auth_endpoints": $([ "$AUTH" -ge 50 ] && echo 'null' || echo '"Need 50+ auth endpoints"'),
    "sast_scripts": $([ "$SAST" -ge 2 ] && echo 'null' || echo '"Need 2+ SAST scripts"'),
    "dast_scripts": $([ "$DAST" -ge 1 ] && echo 'null' || echo '"Need DAST automation"'),
    "tests": $([ "$TESTS" -ge 50 ] && echo 'null' || echo '"Need 50+ test files"')
  },
  "raw_evidence": $(cat "$EVIDENCE")
}
REPORT_EOF

echo ""
echo "=== Readiness Score Report ==="
echo ""
printf "  %-30s %s\n" "Category" "Score"
printf "  %-30s %s\n" "------------------------------" "-----"
printf "  %-30s %d%%\n" "Security (CC1-CC9)" "$SECURITY_SCORE"
printf "  %-30s %d%%\n" "Availability (A1)" "$AVAIL_SCORE"
printf "  %-30s %d%%\n" "Confidentiality (C1-C2)" "$CONF_SCORE"
printf "  %-30s %d%%\n" "Processing Integrity (PI1)" "$PI_SCORE"
printf "  %-30s %d%%\n" "Privacy (P1-P6)" "$PRIV_SCORE"
printf "  %-30s %s\n" "------------------------------" "-----"
printf "  %-30s %d%%\n" "OVERALL READINESS" "$OVERALL"
echo ""

# Gap alerts
echo "=== Gaps to Address ==="
[ "$SAST" -lt 2 ] && echo "  ! SAST scripts: ${SAST}/2 needed"
[ "$DAST" -lt 1 ] && echo "  ! DAST/pen test: missing"
[ "$AUDIT" != "true" ] && echo "  ! Audit logging: not enabled"
[ "$SENTRY" != "true" ] && echo "  ! Sentry monitoring: not configured"

echo ""
echo "Report saved: ${REPORT_DIR}/readiness-report.json"
