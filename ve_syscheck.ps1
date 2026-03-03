param(
    [switch]$WriteLedger,
    [string]$LedgerPath = "E:\Echo_Nexus_Data\ve_ledger.jsonl",
    [string]$PythonPath = ""
)

# UTF-8 output for clean unicode symbols
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# ve_syscheck.ps1
# One-button: handshake → gatecheck → ledger append → sysinfo → quickcheck

# --- Helpers ---
function Resolve-Python {
    param([string]$PreferredPython)

    # 0) Explicit override (caller passed -PythonPath)
    if ($PreferredPython -and $PreferredPython.Trim() -ne "") {
        if (Test-Path -LiteralPath $PreferredPython) { return $PreferredPython }
        throw "PythonPath was provided but not found: $PreferredPython"
    }

    # 1) Active venv (Windows)
    if ($env:VIRTUAL_ENV) {
        $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }

    # 2) Repo-local .venv
    $hereLocal = Split-Path -Parent $MyInvocation.MyCommand.Path
    $candidate = Join-Path $hereLocal ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $candidate) { return $candidate }

    # 3) PATH resolution
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }

    throw "No Python interpreter found. Install Python 3 or activate a venv (.venv) or pass -PythonPath."
}

function Run($cmd, $args) {
    Write-Host "→ $cmd $($args -join ' ')"
    # --- PATCH: prevent interactive Python ---
    if (($cmd -match "(?i)python(\.exe)?$") -and ($args.Count -eq 0)) {
        $args = @("-c", "import sys; print(sys.executable); print(sys.version)")
    }
    & $cmd @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Command exited with code $LASTEXITCODE"
    }
}

# --- Paths ---
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$pyExe = Resolve-Python -PreferredPython $PythonPath

# Echo runtime config (helpful in CI logs)
Write-Host "[VE/syscheck] Using python: $pyExe"
Write-Host "[VE/syscheck] LedgerPath: $LedgerPath"

# 1) Handshake
Write-Host "`n[1/5] Handshake"
Run $pyExe @(".\ve_handshake.py", "--input", '{"id":"syscheck","rho":0.83,"gamma":0.78,"delta":0.22}')

# 2) Gatecheck
Write-Host "`n[2/5] Gatecheck"
Run $pyExe @(".\ve_gatecheck.py")

# 3) Ledger append (pre-sysinfo)
Write-Host "`n[3/5] Ledger append (pre-sysinfo)"
if ($WriteLedger) {
    # NOTE: ve_ledger_append.ps1 may still write to repo-local ledger.jsonl depending on its own defaults.
    # If you want it to append to $LedgerPath too, paste that script next and I’ll wire it cleanly.
    .\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25
} else {
    Write-Host "Skipping ledger append (run with -WriteLedger to enable)." -ForegroundColor Yellow
}

# 4) Sysinfo snapshot
Write-Host "`n[4/5] System info snapshot"
.\ve_sysinfo.ps1 -OutPath "sysinfo.json"

# 5) Quickcheck
Write-Host "`n[5/5] Quickcheck"
if (-not (Test-Path -LiteralPath $LedgerPath)) {
    Write-Host "[VE/syscheck] Ledger not found: $LedgerPath" -ForegroundColor Yellow
    exit 10
}

Run $pyExe @(".\ve_quickcheck.py", "--ledger", $LedgerPath, "--psi-min", "1.38")

# If quickcheck sets a meaningful exit code, propagate it cleanly:
$rc = $LASTEXITCODE
if ($rc -eq 0) { Write-Host "`n✅ ve_syscheck complete."; exit 0 }
elseif ($rc -eq 20) { Write-Host "`n⚠️ ve_syscheck complete (soft-fail)."; exit 20 }
elseif ($rc -eq 10) { Write-Host "`n⚠️ ve_syscheck complete (env/missing file)."; exit 10 }
else { Write-Host "`n❌ ve_syscheck complete (hard-fail)."; exit 30 }