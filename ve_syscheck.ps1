# ve_syscheck.ps1
# One-button: handshake → gatecheck → ledger append → sysinfo → quickcheck

# --- Helpers ---
function Resolve-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }
    throw "No Python interpreter found on PATH. Install Python 3, or add it to PATH."
}

function Run($cmd, $args) {
    Write-Host "→ $cmd $($args -join ' ')"
    & $cmd @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Command exited with code $LASTEXITCODE"
    }
}

# --- Paths ---
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$pyExe = Resolve-Python

# 1) Handshake
Write-Host "`n[1/5] Handshake"
Run $pyExe @(".\ve_handshake.py", "--input", '{"id":"syscheck","rho":0.83,"gamma":0.78,"delta":0.22}')

# 2) Gatecheck
Write-Host "`n[2/5] Gatecheck"
Run $pyExe @(".\ve_gatecheck.py")

# 3) Ledger append (pre-sysinfo)
Write-Host "`n[3/5] Ledger append (pre-sysinfo)"
.\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25

# 4) Sysinfo snapshot
Write-Host "`n[4/5] System info snapshot"
.\ve_sysinfo.ps1 -OutPath "sysinfo.json"

# 5) Quickcheck
Write-Host "`n[5/5] Quickcheck"
Run $pyExe @(".\ve_quickcheck_stub.py", "--ledger", "ledger.jsonl", "--psi-min", "1.38")

Write-Host "`n✅ ve_syscheck complete."
