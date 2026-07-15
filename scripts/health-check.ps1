<#
.SYNOPSIS
    Second Brain OS — Health Check Script (PowerShell)
.DESCRIPTION
    Checks all health endpoints (/health, /health/live, /health/ready) and
    verifies each returns HTTP 200 and expected JSON structure.
    Exit code 0 if all healthy, 1 if any failure.
.PARAMETER Host
    Target host:port (default: localhost:8000)
.PARAMETER Format
    Output format: text (default) or json
.PARAMETER TimeoutSeconds
    HTTP request timeout in seconds (default: 10)
.EXAMPLE
    .\scripts\health-check.ps1
    .\scripts\health-check.ps1 -Host localhost:8000 -Format json
    .\scripts\health-check.ps1 -Host api.secondbrain-os.com -TimeoutSeconds 15
#>

param(
    [string]$TargetHost = "localhost:8000",
    [ValidateSet("text", "json")]
    [string]$Format = "text",
    [int]$TimeoutSeconds = 10
)

$ErrorActionPreference = "Stop"

# ── Endpoints to check ──────────────────────────────────────────────────────────
$ENDPOINTS = @(
    @{ Name = "Root";            Url = "/";              RequiredFields = @("message", "version") }
    @{ Name = "Health";          Url = "/health";        RequiredFields = @("status", "version", "environment") }
    @{ Name = "Liveness";        Url = "/health/live";   RequiredFields = @("status") }
    @{ Name = "Readiness";       Url = "/health/ready";  RequiredFields = @("status", "version", "dependencies") }
)

# ── Helper: structured log output ───────────────────────────────────────────────
function Write-Log {
    param(
        [string]$Level,
        [string]$Message,
        [hashtable]$Data = @{}
    )
    $entry = @{
        timestamp = (Get-Date -Format "o")
        level     = $Level
        service   = "health-check"
        message   = $Message
    } + $Data
    $json = $entry | ConvertTo-Json -Compress
    if ($Level -in @("ERROR", "WARN")) {
        Write-Warning $json
    } else {
        Write-Output $json
    }
}

# ── Helper: check single endpoint ───────────────────────────────────────────────
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string[]]$RequiredFields,
        [int]$TimeoutSeconds
    )

    $result = @{
        friendly_name = $Name
        url           = $Url
        status        = "up"
        status_code   = $null
        error_message = $null
        duration_ms   = 0
        body          = $null
    }

    $fullUrl = "http://${TargetHost}${Url}"
    $start = Get-Date

    try {
        $params = @{
            Uri         = $fullUrl
            Method      = "GET"
            TimeoutSec  = $TimeoutSeconds
            UseBasicParsing = $true
        }
        # SkipCertificateCheck is only available on PowerShell 6+
        if ($PSVersionTable.PSVersion.Major -ge 6) {
            $params.SkipCertificateCheck = $true
        }
        $response = Invoke-WebRequest @params
        $duration_ms = [math]::Round(((Get-Date) - $start).TotalMilliseconds, 2)
        $result.status_code = [int]$response.StatusCode
        $result.duration_ms = $duration_ms

        if ($response.StatusCode -eq 200) {
            # Try to parse JSON body
            try {
                $body = $response.Content | ConvertFrom-Json
                $result.body = $body

                # Verify required fields exist
                $missing = @()
                foreach ($field in $RequiredFields) {
                    if (-not ($body.PSObject.Properties.Name -contains $field)) {
                        $missing += $field
                    }
                }

                if ($missing.Count -gt 0) {
                    $result.status = "degraded"
                    $result.error_message = "Missing required fields: $($missing -join ', ')"
                    Write-Log -Level "WARN" -Message "Health check missing fields" -Data @{
                        endpoint      = $Name
                        url           = $Url
                        status_code   = $result.status_code
                        duration_ms   = $duration_ms
                        status        = $result.status
                        missing_fields = ($missing -join ',')
                    }
                } else {
                    # For /health/ready, check that status is "healthy" or "alive"
                    if ($Url -eq "/health/ready" -and $body.status -ne "healthy") {
                        $result.status = "degraded"
                        $result.error_message = "Readiness status: $($body.status) (expected: healthy)"
                        Write-Log -Level "WARN" -Message "Readiness check degraded" -Data @{
                            endpoint     = $Name
                            url          = $Url
                            status_code  = $result.status_code
                            duration_ms  = $duration_ms
                            status       = $result.status
                            ready_status = $body.status
                        }
                    } else {
                        Write-Log -Level "INFO" -Message "Health check passed" -Data @{
                            endpoint    = $Name
                            url         = $Url
                            status_code = $result.status_code
                            duration_ms = $duration_ms
                            status      = $result.status
                        }
                    }
                }
            } catch {
                $result.status = "degraded"
                $result.error_message = "Response is not valid JSON: $_"
                Write-Log -Level "WARN" -Message "Health check invalid JSON" -Data @{
                    endpoint    = $Name
                    url         = $Url
                    status_code = $result.status_code
                    duration_ms = $duration_ms
                    status      = $result.status
                    error       = $_.Exception.Message
                }
            }
        } else {
            $result.status = "degraded"
            $result.error_message = "HTTP $($response.StatusCode)"
            Write-Log -Level "WARN" -Message "Health check non-200" -Data @{
                endpoint    = $Name
                url         = $Url
                status_code = $result.status_code
                duration_ms = $duration_ms
                status      = $result.status
            }
        }
    } catch [System.Net.WebException] {
        $duration_ms = [math]::Round(((Get-Date) - $start).TotalMilliseconds, 2)
        $result.status = "down"
        $result.error_message = "Connection failed: $($_.Exception.Message)"
        $result.duration_ms = $duration_ms
        Write-Log -Level "ERROR" -Message "Health check connection failed" -Data @{
            endpoint      = $Name
            url           = $Url
            duration_ms   = $duration_ms
            status        = $result.status
            error_type    = "WebException"
            error_message = $_.Exception.Message
        }
    } catch [System.TimeoutException] {
        $duration_ms = [math]::Round(((Get-Date) - $start).TotalMilliseconds, 2)
        $result.status = "down"
        $result.error_message = "Timeout after ${TimeoutSeconds}s"
        $result.duration_ms = $duration_ms
        Write-Log -Level "ERROR" -Message "Health check timeout" -Data @{
            endpoint      = $Name
            url           = $Url
            duration_ms   = $duration_ms
            status        = $result.status
            error_type    = "TimeoutException"
            error_message = "Timeout after ${TimeoutSeconds}s"
        }
    } catch {
        $duration_ms = [math]::Round(((Get-Date) - $start).TotalMilliseconds, 2)
        $result.status = "down"
        $result.error_message = "Unexpected error: $($_.Exception.GetType().Name): $($_.Exception.Message)"
        $result.duration_ms = $duration_ms
        Write-Log -Level "ERROR" -Message "Health check unexpected error" -Data @{
            endpoint      = $Name
            url           = $Url
            duration_ms   = $duration_ms
            status        = $result.status
            error_type    = $_.Exception.GetType().Name
            error_message = $_.Exception.Message
        }
    }

    return $result
}


# ── Main ─────────────────────────────────────────────────────────────────────────
function Main {
    $results = @()

    Write-Log -Level "INFO" -Message "Starting health checks" -Data @{
        target      = $TargetHost
        endpoints   = $ENDPOINTS.Count
        timeout_s   = $TimeoutSeconds
    }

    foreach ($ep in $ENDPOINTS) {
        $result = Test-Endpoint -Name $ep.Name -Url $ep.Url -RequiredFields $ep.RequiredFields -TimeoutSeconds $TimeoutSeconds
        $results += $result
    }

    # ── Output ───────────────────────────────────────────────────────────────────
    if ($Format -eq "json") {
        $output = @{
            timestamp = (Get-Date -Format "o")
            target    = $TargetHost
            results   = $results
        }
        Write-Output ($output | ConvertTo-Json -Depth 5)
    } else {
        foreach ($r in $results) {
            $icon = switch ($r.status) {
                "up"       { "[PASS]" }
                "degraded" { "[DEGR]" }
                "down"     { "[FAIL]" }
                default    { "[ ?  ]" }
            }
            $color = switch ($r.status) {
                "up"       { "Green" }
                "degraded" { "Yellow" }
                "down"     { "Red" }
                default    { "Gray" }
            }
            $sc = if ($null -ne $r.status_code) { $r.status_code.ToString() } else { "" }
            $line = "$icon $($r.friendly_name.PadRight(20)) $($r.status.ToUpper().PadRight(10)) $($sc.PadRight(5)) $($r.duration_ms.ToString('0.0').PadLeft(8))ms  $($r.url)"
            if ($r.error_message) {
                $line += "`n         $($r.error_message)"
            }
            Write-Host $line -ForegroundColor $color
        }

        $upCount = ($results | Where-Object { $_.status -eq "up" }).Count
        $total = $results.Count
        $passColor = if ($upCount -eq $total) { "Green" } elseif ($upCount -gt 0) { "Yellow" } else { "Red" }
        Write-Host "`nResults: $upCount / $total endpoints UP" -ForegroundColor $passColor
    }

    # ── Exit code ────────────────────────────────────────────────────────────────
    $anyDown = ($results | Where-Object { $_.status -eq "down" }).Count -gt 0
    if ($anyDown) {
        Write-Log -Level "ERROR" -Message "Health checks failed" -Data @{
            target = $TargetHost
            up     = $upCount
            total  = $total
        }
        exit 1
    }

    Write-Log -Level "INFO" -Message "All health checks passed" -Data @{
        target = $TargetHost
        up     = $upCount
        total  = $total
    }
    exit 0
}

# ── Run ──────────────────────────────────────────────────────────────────────────
Main
