# ve_diag.ps1
# Environment diagnostics for stability

param([switch]$VerboseMode)

function Info($m){ Write-Host "[INFO] $m" }
function Warn($m){ Write-Warning $m }
function Err($m){ Write-Error $m }

Info "ExecutionPolicy (CurrentUser): $(Get-ExecutionPolicy -Scope CurrentUser)"
Info "ExecutionPolicy (LocalMachine): $(Get-ExecutionPolicy -Scope LocalMachine)"

# Python
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
if ($py) { Info "Python: $py" } else { Err "Python not found on PATH." }

# Path health
$cwd = (Get-Location).Path
Info "Working dir: $cwd"
if ($cwd -match "OneDrive") { Warn "Path contains OneDrive; syncing can lock files. Ensure sync is complete." }
if ($cwd -match "\s") { Info "Path contains spaces (OK, but quoting matters)."

}

# Write test
try {
    "{0}" -f (Get-Date) | Out-File ".\write_test.tmp" -Encoding utf8
    Remove-Item ".\write_test.tmp" -Force
    Info "Write test: OK"
} catch { Err "Write test failed: $_" }

# JSON roundtrip
$payload = @{ id="diag"; rho=0.8; gamma=0.75; delta=0.2 } | ConvertTo-Json -Compress
try {
    $tmp = ".\payload_diag.json"
    $payload | Set-Content $tmp -Encoding utf8
    Info "JSON roundtrip: wrote $tmp"
} catch { Err "JSON write failed: $_" }

Info "Diag complete."
