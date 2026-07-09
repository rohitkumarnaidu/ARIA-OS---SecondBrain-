param([string]$Target = "http://localhost:8000")
$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

Write-Host "=== SQL Injection Audit ==="
$FAIL = 0

Write-Host "Checking for raw SQL patterns in Python backend..."
$rawSqlCount = Select-String -Path "$projectRoot\apps\api\*.py" -Pattern '\.execute\(' -SimpleMatch | Where-Object { $_ -notmatch 'test_' -and $_ -notmatch 'supabase\.' } | Measure-Object | Select-Object -ExpandProperty Count
if ($rawSqlCount -gt 0) { Write-Host "  WARN: Found $rawSqlCount execute() calls not using supabase SDK (verify)" }
else { Write-Host "  PASS: No raw SQL execution detected" }

Write-Host "`nChecking for f-string SQL patterns..."
$fsql = Select-String -Path "$projectRoot\apps\api\*.py" -Pattern 'f".*SELECT|f".*INSERT|f".*UPDATE|f".*DELETE|f".*DROP|f".*ALTER' | Where-Object { $_ -notmatch 'test_' } | Measure-Object | Select-Object -ExpandProperty Count
if ($fsql -gt 0) { Write-Host "  FAIL: $fsql f-string SQL patterns found (risk of injection)"; $FAIL++ }
else { Write-Host "  PASS: No f-string SQL patterns" }

Write-Host "`nChecking for string concatenation SQL..."
$concatSql = Select-String -Path "$projectRoot\apps\api\*.py" -Pattern '"SELECT.*" \+|"INSERT.*" \+|"UPDATE.*" \+|"DELETE.*" \+' | Where-Object { $_ -notmatch 'test_' } | Measure-Object | Select-Object -ExpandProperty Count
if ($concatSql -gt 0) { Write-Host "  FAIL: $concatSql string concat SQL patterns found"; $FAIL += 2 }
else { Write-Host "  PASS: No string concatenation SQL patterns" }

Write-Host "`nChecking frontend Supabase query patterns..."
$frontendInjection = Select-String -Path "$projectRoot\apps\web\*.ts", "$projectRoot\apps\web\*.tsx" -Pattern '\.rpc\(|\.sql\(|\.raw\(' -SimpleMatch | Where-Object { $_ -notmatch 'test_' -and $_ -notmatch 'node_modules' -and $_ -notmatch '\.next' } | Measure-Object | Select-Object -ExpandProperty Count
if ($frontendInjection -gt 0) { Write-Host "  WARN: $frontendInjection raw RPC/SQL calls in frontend (verify parameterized)" }
else { Write-Host "  PASS: No raw SQL/RPC calls in frontend" }

Write-Host "`n=== SQL Injection Audit Complete ==="
if ($FAIL -gt 0) { Write-Host "FAILURES: $FAIL"; exit 1 }
Write-Host "All checks passed."
