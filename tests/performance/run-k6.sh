#!/usr/bin/env bash
set -euo pipefail

# k6 Load Test Runner
# Runs all load test scenarios against a target API
# Usage: ./tests/performance/run-k6.sh [target_url] [auth_token]

API_URL="${1:-http://localhost:8000}"
AUTH_TOKEN="${2:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="performance/reports/${TIMESTAMP}"

echo "=== k6 Load Test Runner ==="
echo "Target: $API_URL"
echo "Timestamp: $TIMESTAMP"
echo ""

mkdir -p "${OUTPUT_DIR}"

if ! command -v k6 &> /dev/null; then
    echo "ERROR: k6 is not installed."
    echo "Install: https://k6.io/docs/getting-started/installation/"
    echo "  macOS: brew install k6"
    echo "  Linux: apt install k6 (or snap install k6)"
    echo "  Windows: winget install k6"
    exit 1
fi

K6_ARGS="-e API_URL=${API_URL} -e AUTH_TOKEN=${AUTH_TOKEN}"

run_test() {
    local script="$1"
    local name="$2"
    echo ""
    echo "=== Running: ${name} ==="
    k6 run ${K6_ARGS} \
        --summary-export="${OUTPUT_DIR}/${name}-summary.json" \
        --out json="${OUTPUT_DIR}/${name}-raw.jsonl" \
        "tests/performance/${script}"
    echo "  Done -> ${OUTPUT_DIR}/${name}-summary.json"
}

run_test "load-test-auth.js" "auth"
run_test "load-test-crud.js" "crud"
run_test "load-test-ai.js" "ai"
run_test "load-test-spike.js" "spike"

# Generate consolidated report
echo ""
echo "=== Consolidated Results ==="
for f in "${OUTPUT_DIR}"/*-summary.json; do
    if [ -f "$f" ]; then
        name=$(basename "$f" -summary.json)
        echo ""
        echo "--- ${name} ---"
        if command -v jq &> /dev/null; then
            jq -r '"Thresholds: \(.metrics.http_req_duration.thresholds | to_entries | map("\(.key)=\(.value.ok // false)") | join(", "))" // "No threshold data"' "$f" 2>/dev/null || true
            jq -r '"P95: \(.metrics.http_req_duration.values?."p(95)" // "N/A") ms"' "$f" 2>/dev/null || true
            jq -r '"P99: \(.metrics.http_req_duration.values?."p(99)" // "N/A") ms"' "$f" 2>/dev/null || true
            jq -r '"Failed Reqs: \(.metrics.http_req_failed?.values?.rate // "N/A")"' "$f" 2>/dev/null || true
        fi
    fi
done

echo ""
echo "=== Load Testing Complete ==="
echo "Reports: ${OUTPUT_DIR}/"
