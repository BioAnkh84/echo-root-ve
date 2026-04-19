param(
    [string]$RepoRoot   = "E:\Echo_Nexus_Data\repos\echo-root-ve",
    [string]$LedgerPath = "E:\Echo_Nexus_Data\ve_ledger.jsonl",
    [string]$PythonPath = "",
    [string]$BridgePath = "E:\Echo_Nexus_Data\habitat\cipher_local\echo_gate_bridge.py"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ------------------------------------------------
# UTF-8 output hygiene
# ------------------------------------------------
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$env:PYTHONUTF8 = "1"

# ------------------------------------------------
# Resolve Python
# ------------------------------------------------
function Resolve-Python {
    param([string]$PreferredPython, [string]$RepoRoot)

    if ($PreferredPython -and $PreferredPython.Trim() -ne "") {
        if (Test-Path -LiteralPath $PreferredPython) { return $PreferredPython }
        throw "PythonPath provided but not found: $PreferredPython"
    }

    if ($env:VIRTUAL_ENV) {
        $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }

    if ($RepoRoot) {
        $candidate = Join-Path $RepoRoot ".venv\Scripts\python.exe"
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }

    throw "No Python found. Install Python or activate the venv."
}

# ------------------------------------------------
# Validate repo
# ------------------------------------------------
if (-not (Test-Path -LiteralPath $RepoRoot)) {
    Write-Host "[reentry] ERROR: RepoRoot not found: $RepoRoot"
    exit 1
}

Set-Location $RepoRoot

# ------------------------------------------------
# Resolve Python
# ------------------------------------------------
try {
    $pyExe = Resolve-Python -PreferredPython $PythonPath -RepoRoot $RepoRoot
}
catch {
    Write-Host "[reentry] ERROR: $_"
    exit 1
}

# ------------------------------------------------
# Header
# ------------------------------------------------
Write-Host "[reentry] RepoRoot=$RepoRoot"
Write-Host "[reentry] Python=$pyExe"
Write-Host "[reentry] Ledger=$LedgerPath"
Write-Host "[reentry] Bridge=$BridgePath"

# ------------------------------------------------
# Lightweight checks (NO recursion)
# ------------------------------------------------
$checksPassed = $true

# --- Kernel ---
if (-not (Test-Path -LiteralPath ".\ve_kernel.py")) {
    Write-Host "[reentry] ERROR: ve_kernel.py missing"
    $checksPassed = $false
} else {
    Write-Host "[reentry] Kernel OK"
}

# --- Quickcheck ---
if (-not (Test-Path -LiteralPath ".\ve_quickcheck.py")) {
    Write-Host "[reentry] ERROR: ve_quickcheck.py missing"
    $checksPassed = $false
} else {
    Write-Host "[reentry] Quickcheck OK"
}

# --- Bridge (external system) ---
if (-not (Test-Path -LiteralPath $BridgePath)) {
    Write-Host "[reentry] ERROR: echo_gate_bridge.py missing at $BridgePath"
    $checksPassed = $false
} else {
    Write-Host "[reentry] Bridge OK"
}

# --- Ledger ---
if (-not (Test-Path -LiteralPath $LedgerPath)) {
    Write-Host "[reentry] WARN: Ledger not found yet (will be created on first run)"
} else {
    Write-Host "[reentry] Ledger OK"
}

# ------------------------------------------------
# Result
# ------------------------------------------------
Write-Host ""

if ($checksPassed) {
    Write-Host "[reentry] OK"
    exit 0
}
else {
    Write-Host "[reentry] FAILED"
    exit 1
}