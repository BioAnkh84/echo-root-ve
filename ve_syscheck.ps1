param(
    [switch]$WriteLedger,
    [string]$LedgerPath = "E:\Echo_Nexus_Data\ve_ledger.jsonl",
    [string]$PythonPath = ""
)

# Force non-terminating errors to stop so exit codes are truthful
$ErrorActionPreference = "Stop"

# UTF-8 output for clean unicode symbols
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# ve_syscheck.ps1
# One-button: handshake → gatecheck → ledger append → sysinfo → quickcheck

# --- Helpers ---
function Resolve-Python {
    param(
        [string]$PreferredPython,
        [string]$RepoRoot
    )

    # 0) Explicit override
    if ($PreferredPython -and $PreferredPython.Trim() -ne "") {
        if (Test-Path -LiteralPath $PreferredPython) { return $PreferredPython }
        throw "PythonPath was provided but not found: $PreferredPython"
    }

    # 1) Active venv
    if ($env:VIRTUAL_ENV) {
        $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }

    # 2) Repo-local .venv
    if ($RepoRoot) {
        $candidate = Join-Path $RepoRoot ".venv\Scripts\python.exe"
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }

    # 3) PATH resolution
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }

    throw "No Python interpreter found. Install Python 3 or activate a venv."
}

function Run {
    param(
        [Parameter(Mandatory=$true)][string]$Cmd,
        [Parameter(Mandatory=$false)][string[]]$ArgList = @()
    )

    Write-Host "→ $Cmd $($ArgList -join ' ')"

    # Prevent accidental interactive Python
    if (($Cmd -match "(?i)python(\.exe)?$") -and ($ArgList.Count -eq 0)) {
        $ArgList = @("-c", "import sys; print(sys.executable); print(sys.version)")
    }

    & $Cmd @ArgList 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Command exited with code $LASTEXITCODE"
    }
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Text
    )
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Text, $utf8NoBom)
}

function Get-LedgerHasAnyRecord {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $fi = Get-Item -LiteralPath $Path -ErrorAction SilentlyContinue
    if (-not $fi) { return $false }
    if ($fi.Length -le 0) { return $false }

    # If the file has only whitespace/newlines, treat as empty
    try {
        $firstNonEmpty = Get-Content -LiteralPath $Path -TotalCount 200 | Where-Object { $_.Trim() -ne "" } | Select-Object -First 1
        return [bool]$firstNonEmpty
    } catch {
        return $false
    }
}

function Ensure-LedgerFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType File -Path $Path -Force | Out-Null
    }
}

function Write-GenesisFallback {
    param(
        [string]$Path,
        [double]$rho,
        [double]$gamma,
        [double]$delta
    )
    # Fallback: write a minimal genesis record to avoid append scripts failing on empty ledger.
    # Uses hash_prev all-zeros and hash_self as a dummy placeholder.
    # NOTE: This is a syscheck safety net only; your real canonical writer should own genesis format.
    $gen = [ordered]@{
        time      = (Get-Date).ToString("s")
        rho       = $rho
        gamma     = $gamma
        delta     = $delta
        hash_prev = ("0" * 64)
        hash_self = ("0" * 64)
        note      = "syscheck_genesis_fallback"
    }
    $line = ($gen | ConvertTo-Json -Compress)
    Add-Content -LiteralPath $Path -Value $line -Encoding utf8
    Write-Host "Genesis fallback line written to ledger (syscheck safety net)." -ForegroundColor Yellow
}

# --- Paths ---
$here = $PSScriptRoot
Set-Location $here

$pyExe = Resolve-Python -PreferredPython $PythonPath -RepoRoot $here

Write-Host "[VE/syscheck] Using python: $pyExe"
Write-Host "[VE/syscheck] LedgerPath: $LedgerPath"

# 1) Handshake (quote-safe via temp file)
Write-Host "`n[1/5] Handshake"
$handshakeObj = @{
    id    = "syscheck"
    rho   = 0.83
    gamma = 0.78
    delta = 0.22
}
$handshakeJson = ($handshakeObj | ConvertTo-Json -Compress)
$tmpHandshake = Join-Path $env:TEMP "ve_syscheck_handshake.json"
Write-Utf8NoBom -Path $tmpHandshake -Text $handshakeJson

Run -Cmd $pyExe -ArgList @(
    ".\ve_handshake.py",
    "--input-file", $tmpHandshake
)

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n⚠️ Handshake failed; stopping syscheck." -ForegroundColor Yellow
    exit 10
}

# 2) Gatecheck
Write-Host "`n[2/5] Gatecheck"
Run -Cmd $pyExe -ArgList @(".\ve_gatecheck.py")
if ($LASTEXITCODE -ne 0) { exit 30 }

# 3) Ledger append (optional)
Write-Host "`n[3/5] Ledger append (pre-sysinfo)"
if ($WriteLedger) {
    Ensure-LedgerFile -Path $LedgerPath

    $hasAny = Get-LedgerHasAnyRecord -Path $LedgerPath

    # We do NOT introspect cmd.Parameters (it can be null / weird). We just call with -LedgerPath always.
    # If the append script supports -Genesis, great; if not, we fallback by writing a genesis line once.
    try {
        if (-not $hasAny) {
            # Attempt: append script with -Genesis (if it supports it)
            & .\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25 -LedgerPath $LedgerPath -Genesis 2>$null
            if ($LASTEXITCODE -ne 0) {
                # If -Genesis isn't supported, fallback genesis then try normal append
                Write-GenesisFallback -Path $LedgerPath -rho 0.90 -gamma 0.80 -delta 0.25
                & .\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25 -LedgerPath $LedgerPath
            }
        } else {
            & .\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25 -LedgerPath $LedgerPath
        }
    }
    catch {
        Write-Host "❌ Ledger append step failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 30
    }

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

Run -Cmd $pyExe -ArgList @(
    ".\ve_quickcheck.py",
    "--ledger", $LedgerPath,
    "--psi-min", "1.38",
    "--psi-warn-is-softfail"
)

$rc = $LASTEXITCODE

if ($rc -eq 0) {
    Write-Host "`n✅ ve_syscheck complete."
    exit 0
}
elseif ($rc -eq 20) {
    Write-Host "`n⚠️ ve_syscheck complete (soft-fail)."
    exit 20
}
elseif ($rc -eq 10) {
    Write-Host "`n⚠️ ve_syscheck complete (env issue)."
    exit 10
}
else {
    Write-Host "`n❌ ve_syscheck complete (hard-fail)."
    exit 30
}