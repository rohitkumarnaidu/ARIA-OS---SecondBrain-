#!/usr/bin/env bash
set -euo pipefail

echo "=== SQL Injection Audit ==="
echo ""

cd "$(dirname "$0")/.."

FAIL=0

# Check all supabase queries use parameterized patterns (eq, text_search, match)
echo "Checking for raw SQL patterns in Python backend..."
RAW_SQL_COUNT=$(grep -rn "\.execute(" apps/api --include="*.py" | grep -v "test_" | grep -v "__pycache__" | grep -v "supabase\." | wc -l)
if [ "$RAW_SQL_COUNT" -gt 0 ]; then
    echo "  WARN: Found $RAW_SQL_COUNT execute() calls not using supabase SDK (verify)"
    grep -rn "\.execute(" apps/api --include="*.py" | grep -v "test_" | grep -v "__pycache__" | grep -v "supabase\." || true
else
    echo "  PASS: No raw SQL execution detected"
fi

# Check for Python string formatting in queries (f-strings with SQL)
echo ""
echo "Checking for f-string SQL patterns..."
FSTRING_SQL=$(grep -rn 'f".*SELECT\|f".*INSERT\|f".*UPDATE\|f".*DELETE\|f".*DROP\|f".*ALTER' apps/api --include="*.py" | grep -v "test_" | wc -l)
if [ "$FSTRING_SQL" -gt 0 ]; then
    echo "  FAIL: $FSTRING_SQL f-string SQL patterns found (risk of injection)"
    FAIL=$((FAIL + 1))
else
    echo "  PASS: No f-string SQL patterns"
fi

# Check for string concatenation in SQL
echo ""
echo "Checking for string concatenation SQL..."
CONCAT_SQL=$(grep -rn '".*SELECT.*" + \|".*INSERT.*" + \|".*UPDATE.*" + \|".*DELETE.*" + ' apps/api --include="*.py" | grep -v "test_" | wc -l)
if [ "$CONCAT_SQL" -gt 0 ]; then
    echo "  FAIL: $CONCAT_SQL string concat SQL patterns found"
    FAIL=$((FAIL + 2))
else
    echo "  PASS: No string concatenation SQL patterns"
fi

# Check frontend Supabase queries
echo ""
echo "Checking frontend Supabase query patterns..."
FRONTEND_INJECTION=$(grep -rn "\.rpc\|\.sql\|\.raw" apps/web --include="*.ts" --include="*.tsx" | grep -v "test_" | grep -v "node_modules" | grep -v ".next" | wc -l)
if [ "$FRONTEND_INJECTION" -gt 0 ]; then
    echo "  WARN: $FRONTEND_INJECTION raw RPC/SQL calls in frontend (verify they are parameterized)"
else
    echo "  PASS: No raw SQL/RPC calls in frontend"
fi

echo ""
echo "=== SQL Injection Audit Complete ==="
if [ "$FAIL" -gt 0 ]; then
    echo "FAILURES: $FAIL"
    exit 1
fi
echo "All checks passed."
