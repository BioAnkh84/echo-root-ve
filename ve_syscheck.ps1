param(
    [string]$RepoPath = "E:\Echo_Nexus_Data\repos\echo-root-ve",
    [string]$PythonPath = "",
    [string]$LedgerPath = "E:\Echo_Nexus_Data\ve_ledger.jsonl",
    [string]$BridgePath = "E:\Echo_Nexus_Data\habitat\cipher_local\echo_gate_bridge.py",
    [switch]$VerboseChecks
)

# ================================================================
# Echo Root VE System Check
# Reentry → bridge → governed kernel → ledger → quickcheck
# ================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ------------------------------------------------
# UTF-8 hygiene
# ------------------------------------------------
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$env:PYTHONUTF8 = "1"

# ------------------------------------------------
# Helpers
# ------------------------------------------------
function Write-Step {
    param([string]$Text)
    Write-Host ""
    Write-Host $Text -ForegroundColor Cyan
}

function Resolve-Python {
    param(
        [string]$PreferredPython,
        [string]$RepoRoot
    )

    if ($PreferredPython -and $PreferredPython.Trim() -ne "") {
        if (Test-Path -LiteralPath $PreferredPython) { return $PreferredPython }
        throw "PythonPath was provided but not found: $PreferredPython"
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

    throw "No Python interpreter found. Install Python 3 or activate a venv."
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory=$true)][string]$Exe,
        [Parameter(Mandatory=$false)][string[]]$Args = @(),
        [Parameter(Mandatory=$true)][string]$Label,
        [switch]$AllowSoftFail,
        [int[]]$SoftFailCodes = @(20)
    )

    if ($VerboseChecks) {
        Write-Host "→ $Exe $($Args -join ' ')" -ForegroundColor DarkGray
    } else {
        Write-Host "→ $Label"
    }

    & $Exe @Args
    $rc = $LASTEXITCODE

    if ($rc -eq 0) {
        Write-Host "[OK] $Label" -ForegroundColor Green
        return 0
    }

    if ($AllowSoftFail -and ($SoftFailCodes -contains $rc)) {
        Write-Host "[SOFT-FAIL] $Label (exit $rc)" -ForegroundColor Yellow
        return $rc
    }

    Write-Host "[FAIL] $Label (exit $rc)" -ForegroundColor Red
    throw "$Label failed with exit code $rc"
}

function Ensure-File {
    param(
        [string]$Path,
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label not found: $Path"
    }

    Write-Host "[OK] $Label found" -ForegroundColor Green
}

function Get-LedgerLineCount {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) { return 0 }

    try {
        return (Get-Content -LiteralPath $Path | Measure-Object -Line).Lines
    } catch {
        return 0
    }
}

# ------------------------------------------------
# Resolve environment
# ------------------------------------------------
Write-Host ""
Write-Host "=== Echo Root VE System Check ===" -ForegroundColor Cyan
Write-Host ""

Ensure-File -Path $RepoPath -Label "Repo path"
Set-Location $RepoPath

$python = Resolve-Python -PreferredPython $PythonPath -RepoRoot $RepoPath
Write-Host "[OK] Python: $python" -ForegroundColor Green

Ensure-File -Path $BridgePath -Label "Echo Gate Bridge"
Ensure-File -Path (Join-Path $RepoPath "ve_kernel.py") -Label "VE Python kernel"
Ensure-File -Path (Join-Path $RepoPath "ve_quickcheck.py") -Label "VE quickcheck"
Ensure-File -Path (Join-Path $RepoPath "ve_reentry.ps1") -Label "VE reentry script"

# ------------------------------------------------
# 1. Reentry
# ------------------------------------------------
Write-Step "[1/6] Reentry"
& (Join-Path $RepoPath "ve_reentry.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Reentry check failed with exit code $LASTEXITCODE"
}
Write-Host "[OK] Reentry check passed" -ForegroundColor Green

# ------------------------------------------------
# 2. Bridge smoke tests
# ------------------------------------------------
Write-Step "[2/6] Echo Gate Bridge smoke tests"

$bridgeCases = @(
    @{ Input = "hello";             ExpectDecision = "PROCEED"; ExpectRoute = "normal" },
    @{ Input = "handle it";         ExpectDecision = "PAUSE";   ExpectRoute = "safe_only" },
    @{ Input = "delete everything"; ExpectDecision = "ABORT";   ExpectRoute = "blocked" }
)

foreach ($case in $bridgeCases) {
    $raw = & $python $BridgePath $case.Input
    if ($LASTEXITCODE -ne 0) {
        throw "Bridge call failed for input: $($case.Input)"
    }

    $obj = $raw | ConvertFrom-Json

    if ($obj.decision -ne $case.ExpectDecision) {
        throw "Bridge decision mismatch for '$($case.Input)': got '$($obj.decision)', expected '$($case.ExpectDecision)'"
    }

    if ($obj.route_hint -ne $case.ExpectRoute) {
        throw "Bridge route_hint mismatch for '$($case.Input)': got '$($obj.route_hint)', expected '$($case.ExpectRoute)'"
    }

    Write-Host "[OK] Bridge case '$($case.Input)' → $($obj.decision) / $($obj.route_hint)" -ForegroundColor Green
}

# ------------------------------------------------
# 3. VE kernel smoke tests
# ------------------------------------------------
Write-Step "[3/6] VE kernel governed execution tests"

$beforeLines = Get-LedgerLineCount -Path $LedgerPath

$kernelCases = @(
    @{ Args = @("ve_kernel.py", "exec", "echo: hello");             ExpectText = "decision=PROCEED"; ExpectExit = 0 },
    @{ Args = @("ve_kernel.py", "exec", "handle it");               ExpectText = "decision=PAUSE";   ExpectExit = 0 },
    @{ Args = @("ve_kernel.py", "exec", "delete everything");       ExpectText = "decision=ABORT";   ExpectExit = 1 }
)

foreach ($case in $kernelCases) {
    $output = & $python @($case.Args) 2>&1
    $rc = $LASTEXITCODE
    $joined = ($output | Out-String)

    if ($rc -ne $case.ExpectExit) {
        throw "Kernel exit mismatch for '$($case.Args -join ' ')': got '$rc', expected '$($case.ExpectExit)'"
    }

    if ($joined -notmatch [regex]::Escape($case.ExpectText)) {
        throw "Kernel output missing expected text '$($case.ExpectText)' for '$($case.Args -join ' ')'"
    }

    Write-Host "[OK] Kernel case '$($case.Args[-1])' validated" -ForegroundColor Green
}

$afterLines = Get-LedgerLineCount -Path $LedgerPath
if ($afterLines -lt $beforeLines) {
    throw "Ledger line count decreased unexpectedly"
}

if ($afterLines -eq 0) {
    Write-Host "[WARN] Ledger file exists but has no entries yet" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Ledger present with $afterLines line(s)" -ForegroundColor Green
}

# ------------------------------------------------
# 4. Kernel built-in quickcheck
# ------------------------------------------------
Write-Step "[4/6] VE kernel quickcheck"
Invoke-CheckedCommand -Exe $python -Args @("ve_kernel.py", "quickcheck") -Label "ve_kernel quickcheck"

# ------------------------------------------------
# 5. Ledger quickcheck
# ------------------------------------------------
Write-Step "[5/6] Ledger quickcheck"
Invoke-CheckedCommand `
    -Exe $python `
    -Args @("ve_quickcheck.py", "--ledger", $LedgerPath, "--psi-min", "1.38", "--psi-warn-is-softfail") `
    -Label "ve_quickcheck" `
    -AllowSoftFail

# ------------------------------------------------
# 6. Summary
# ------------------------------------------------
Write-Step "[6/6] Summary"
Write-Host "[OK] Repo path: $RepoPath" -ForegroundColor Green
Write-Host "[OK] Bridge path: $BridgePath" -ForegroundColor Green
Write-Host "[OK] Ledger path: $LedgerPath" -ForegroundColor Green
Write-Host "[OK] Governance wiring validated" -ForegroundColor Green
Write-Host "[OK] VE kernel validated" -ForegroundColor Green
Write-Host "[OK] Quickcheck completed" -ForegroundColor Green

Write-Host ""
Write-Host "=== VE System Check Complete ===" -ForegroundColor Cyan
Write-Host ""
exit 0