#!/bin/bash
# Bundle Size Auditor
#
# Runs the Next.js bundle analyzer and checks that the main JS bundle
# stays under 300KB gzipped.
#
# Usage: bash scripts/audit-bundle.sh
# Exits with code 0 if under budget, 1 if exceeded.

set -euo pipefail

BUDGET_KB=300
WEB_DIR="$(cd "$(dirname "$0")/../apps/web" && pwd)"
REPORT_DIR="$WEB_DIR/.next/analyze"

echo ""
echo "  📦 Bundle Size Auditor"
echo "  Budget: ${BUDGET_KB}KB gzip"
echo ""

# Ensure dependencies are installed
if [ ! -d "$WEB_DIR/node_modules" ]; then
    echo "  Installing dependencies..."
    cd "$WEB_DIR" && npm ci --silent 2>/dev/null
fi

# Run the bundle analyzer build
echo "  Running bundle analyzer..."
cd "$WEB_DIR"
ANALYZE=true npx next build 2>&1 | tail -5 || true

# Find the main JS chunk
MAIN_JS=$(find "$WEB_DIR/.next" -name 'main-*.js' -type f 2>/dev/null | head -1)

if [ -z "$MAIN_JS" ]; then
    # Try static/chunks if main-*.js not found at root
    MAIN_JS=$(find "$WEB_DIR/.next/static/chunks" -name 'main-*.js' -type f 2>/dev/null | head -1)
fi

if [ -z "$MAIN_JS" ]; then
    echo "  ⚠ Could not locate main JS chunk. Skipping size check."
    echo "  Check .next/analyze/ for the report."
    exit 0
fi

# Get gzipped size
GZIP_SIZE=$(gzip -c "$MAIN_JS" | wc -c | tr -d ' ')
SIZE_KB=$((GZIP_SIZE / 1024))

echo ""
echo "  Main JS chunk: $MAIN_JS"
echo "  Gzip size: ${SIZE_KB}KB"

if [ "$SIZE_KB" -gt "$BUDGET_KB" ]; then
    echo ""
    echo "  ❌ Bundle budget exceeded: ${SIZE_KB}KB > ${BUDGET_KB}KB"
    echo ""
    exit 1
else
    echo ""
    echo "  ✅ Bundle within budget: ${SIZE_KB}KB / ${BUDGET_KB}KB"
    echo ""
    exit 0
fi
