# Mirror configured skill sources into this repo (later source wins on name conflict).
# Skips empty folders. Edit $sources below for your machine.

$ErrorActionPreference = "Stop"
$dest = $PSScriptRoot

$exclude = @(
    "cavecrew", "caveman", "caveman-commit", "caveman-compress", "caveman-help",
    "caveman-review", "caveman-stats", "find-skills"
)

$sources = @(
    "$env:USERPROFILE\MiraGameDev\griddungeon-design-docs\.cursor\skills",
    "$env:USERPROFILE\.cursor\skills"
)

foreach ($src in $sources) {
    if (-not (Test-Path $src)) {
        Write-Warning "Skip missing source index $($sources.IndexOf($src))"
        continue
    }

    Write-Host "=== syncing ===" -ForegroundColor Cyan
    Get-ChildItem $src -Directory | ForEach-Object {
        if ($exclude -contains $_.Name) {
            Write-Host "  skip (excluded): $($_.Name)" -ForegroundColor DarkYellow
            return
        }

        $files = Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue
        if ($files.Count -eq 0) {
            Write-Host "  skip (empty): $($_.Name)" -ForegroundColor DarkYellow
            return
        }

        $target = Join-Path $dest $_.Name
        robocopy $_.FullName $target /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
        if ($LASTEXITCODE -ge 8) {
            throw "robocopy failed for $($_.Name) (exit $LASTEXITCODE)"
        }

        Write-Host "  ok: $($_.Name) ($($files.Count) files)"
    }
}

Write-Host "`nSkills mirrored:" -ForegroundColor Green
Get-ChildItem $dest -Directory | Sort-Object Name | ForEach-Object {
    $n = (Get-ChildItem $_.FullName -Recurse -File).Count
    Write-Host "  $($_.Name) ($n)"
}
