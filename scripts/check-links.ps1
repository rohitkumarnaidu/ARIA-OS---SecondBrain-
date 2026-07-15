param([switch]$Verbose)

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item (Join-Path $PSScriptRoot "..")).FullName
$date = Get-Date -Format "yyyy-MM-dd"

$linkRegex = [regex]'\[([^\]]*)\]\(([^)]+)\)'
$anchorRegex = [regex]'^([^#]+)(?:#.+)?$'

$scannedFiles = @()
$totalLinks = 0
$brokenLinks = @()

function Get-LinksFromFile {
    param($FilePath, $Content)
    $result = @()
    $lines = $Content -split "`n"
    $inCodeBlock = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $lineNum = $i + 1
        if ($line -match '^```') { $inCodeBlock = -not $inCodeBlock; continue }
        if ($inCodeBlock) { continue }
        $matches = $linkRegex.Matches($line)
        foreach ($match in $matches) {
            # Skip if link is inside backticks (inline code / template examples)
            $fullMatch = $match.Value
            $matchIndex = $match.Index
            $beforeMatch = $line.Substring(0, $matchIndex)
            $backtickCount = ($beforeMatch.ToCharArray() | Where-Object { $_ -eq '`' }).Count
            if ($backtickCount % 2 -eq 1) { continue }

            $text = $match.Groups[1].Value
            $target = $match.Groups[2].Value.Trim()
            if ($target -match '^https?://') { continue }
            if ($target -match '^/[^/]') { continue }
            if ($target -match '^mailto:') { continue }
            if ($target -match '^#') { continue }
            if ($target -match '^\[.*\]$') { continue }
            # Skip paths with illegal characters
            $skip = $false
            foreach ($ch in @('<', '>', '|', '"', '*', '?')) {
                if ($target.Contains($ch)) { $skip = $true; break }
            }
            if ($target.Contains(' ')) { $skip = $true }
            if ($target -match '%[0-9A-Fa-f]{2}') { $skip = $true }
            if (-not $skip) {
                $result += @{
                    Line = $lineNum
                    Text = $text
                    Target = $target
                }
            }
        }
    }
    return $result
}

function Resolve-LinkPath {
    param($SourceFile, $Target)
    $sourceDir = (Get-Item $SourceFile).Directory.FullName
    $stripMatch = $anchorRegex.Match($Target)
    $cleanPath = if ($stripMatch.Success) { $stripMatch.Groups[1].Value } else { $Target }
    $cleanPath = $cleanPath.Replace('\', '/')
    try {
        if ([System.IO.Path]::IsPathRooted($cleanPath)) {
            $resolved = $cleanPath
        } else {
            $resolved = Join-Path $sourceDir $cleanPath
            $resolved = $resolved.Replace('\', '/')
        }
        $fullPath = [System.IO.Path]::GetFullPath($resolved)
        return $fullPath
    } catch {
        return $null
    }
}

Write-Host "Scanning files..." -ForegroundColor Cyan

$rootMdFiles = Get-ChildItem -Path $repoRoot -Filter "*.md" -File | ForEach-Object FullName
$allFilesList = New-Object System.Collections.ArrayList
$allDirsList = New-Object System.Collections.ArrayList
$excludePattern = '\\node_modules\\|\\\.git\\|\\__pycache__\\|\\\.next\\|\\venv\\|\\\.venv\\|\\htmlcov\\|\\\.opencode\\|\\bower_components\\'
$folders = @("docs", "prompts", "monitoring", "logging", "infrastructure", "analytics", "apps", "packages", "services", "scripts", "tests", ".github", ".vscode")
foreach ($folder in $folders) {
    $folderPath = Join-Path $repoRoot $folder
    if (Test-Path $folderPath) {
        $items = Get-ChildItem -Path $folderPath -Recurse -File | Where-Object { $_.DirectoryName -notmatch $excludePattern } | ForEach-Object FullName
        foreach ($i in $items) { if ($i) { $null = $allFilesList.Add($i) } }
        $dirs = Get-ChildItem -Path $folderPath -Recurse -Directory | Where-Object { $_.FullName -notmatch $excludePattern } | ForEach-Object FullName
        foreach ($d in $dirs) { if ($d) { $null = $allDirsList.Add($d) } }
    }
}
foreach ($f in $rootMdFiles) { if ($f) { $null = $allFilesList.Add($f) } }
# Also add root-level non-md files (LICENSE, etc.)
$rootNonMdFiles = Get-ChildItem -Path $repoRoot -File | Where-Object { $_.Extension -ne '.md' -and $_.Name -notin @('.gitignore','.dockerignore','.env.example','.pre-commit-config.yaml','.editorconfig','.eslintrc.json','.prettierrc','.gitkeep','talosconfig') } | ForEach-Object FullName
foreach ($f in $rootNonMdFiles) { if ($f) { $null = $allFilesList.Add($f) } }

$allFiles = $allFilesList | Sort-Object -Unique
Write-Host ("  Found " + $allFiles.Count + " files to scan") -ForegroundColor Gray

$existingFiles = @{}
foreach ($f in $allFiles) {
    $normalized = $f.Replace('\', '/').ToLowerInvariant()
    $existingFiles[$normalized] = $true
}
$existingDirs = @{}
foreach ($d in $allDirsList) {
    $normalized = $d.Replace('\', '/').ToLowerInvariant()
    $existingDirs[$normalized] = $true
}

# Scan only .md files for links, but validate against ALL files
$mdFilesOnly = $allFiles | Where-Object { $_ -like '*.md' } | Sort-Object -Unique

$index = 0
foreach ($file in $mdFilesOnly) {
    $index++
    $percent = [math]::Round(($index / $mdFilesOnly.Count) * 100)
    $relPath = $file.Substring($repoRoot.Length + 1).Replace('\', '/')
    Write-Progress -Activity "Checking links" -Status $relPath -PercentComplete $percent

    try {
        $content = [System.IO.File]::ReadAllText($file)
    } catch { continue }
    $scannedFiles += $file

    $links = Get-LinksFromFile -FilePath $file -Content $content
    foreach ($link in $links) {
        $totalLinks++
        $resolved = Resolve-LinkPath -SourceFile $file -Target $link.Target
        if ($null -eq $resolved) { continue }
        $resolvedNormalized = $resolved.Replace('\', '/').ToLowerInvariant()
        $exists = $existingFiles.ContainsKey($resolvedNormalized)
        if (-not $exists -and -not $resolvedNormalized.EndsWith('.md')) {
            $exists = $existingFiles.ContainsKey($resolvedNormalized + '.md')
        }
        if (-not $exists -and $resolvedNormalized.EndsWith('.md')) {
            $withoutExt = $resolvedNormalized.Substring(0, $resolvedNormalized.Length - 3)
            $exists = $existingFiles.ContainsKey($withoutExt)
        }
        # Check if target is a directory
        if (-not $exists) {
            $dirCheckNoSlash = $resolvedNormalized.TrimEnd('/')
            $exists = $existingDirs.ContainsKey($dirCheckNoSlash)
        }

        if (-not $exists) {
            $resolvedLower = $resolvedNormalized
            $repoNormalized = $repoRoot.Replace('\', '/').ToLowerInvariant()
            if ($resolvedLower.StartsWith($repoNormalized)) {
                $brokenLinks += @{
                    Source = $file
                    Line = $link.Line
                    Text = $link.Text
                    Target = $link.Target
                    Resolved = $resolved
                }
            }
        }
    }
}

$grouped = $brokenLinks | Group-Object Source

Write-Host ""
Write-Host ("=" * 55) -ForegroundColor Cyan
Write-Host (" LINK CHECKER REPORT -- " + $date) -ForegroundColor Cyan
Write-Host ("=" * 55) -ForegroundColor Cyan
Write-Host ("Total files scanned: " + $scannedFiles.Count) -ForegroundColor Gray
Write-Host ("Total links checked: " + $totalLinks) -ForegroundColor Gray
$brokenColor = if ($brokenLinks.Count -eq 0) { 'Green' } else { 'Red' }
Write-Host ("Broken links found: " + $brokenLinks.Count) -ForegroundColor $brokenColor
Write-Host ""

if ($brokenLinks.Count -eq 0) {
    Write-Host " NO BROKEN LINKS FOUND" -ForegroundColor Green
} else {
    Write-Host " BROKEN LINKS:" -ForegroundColor Red
    Write-Host ("-" * 55) -ForegroundColor Yellow
    foreach ($group in $grouped) {
        $rawSource = $group.Name.Replace('\', '/')
        $relSource = $rawSource
        if ($relSource.StartsWith($repoRoot.Replace('\', '/'))) {
            $relSource = $relSource.Substring($repoRoot.Length + 1)
        }
        Write-Host (" Source: " + $relSource) -ForegroundColor Yellow
        foreach ($link in $group.Group) {
            $rawResolved = $link.Resolved.Replace('\', '/')
            $relResolved = $rawResolved
            if ($relResolved.StartsWith($repoRoot.Replace('\', '/'))) {
                $relResolved = $relResolved.Substring($repoRoot.Length + 1)
            }
            Write-Host ("   Line " + $link.Line + ": [" + $link.Text + "](" + $link.Target + ") -> " + $relResolved + " (does not exist)") -ForegroundColor Red
        }
    }
}

return @{
    ScannedFiles = $scannedFiles.Count
    TotalLinks = $totalLinks
    BrokenLinks = $brokenLinks.Count
    BrokenDetails = $brokenLinks
}
