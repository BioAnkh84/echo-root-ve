param(
    [string]$RepoRoot = "E:\Echo_Nexus_Data\repos\echo-root-ve",
    [string]$LedgerPath = "E:\Echo_Nexus_Data\ve_ledger.jsonl",
    [string]$PythonPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# UTF-8 output
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

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

if (-not (Test-Path -LiteralPath $RepoRoot)) { throw "RepoRoot not found: $RepoRoot" }
Set-Location $RepoRoot

$pyExe = Resolve-Python -PreferredPython $PythonPath -RepoRoot $RepoRoot

Write-Host "[reentry] RepoRoot=$RepoRoot"
Write-Host "[reentry] Python=$pyExe"
Write-Host "[reentry] Ledger=$LedgerPath"

# Run syscheck end-to-end (writes ledger + sysinfo + quickcheck)
& "$RepoRoot\ve_syscheck.ps1" -WriteLedger -LedgerPath $LedgerPath -PythonPath $pyExe
$rc = $LASTEXITCODE

Write-Host ""
Write-Host "[reentry] ve_syscheck rc=$rc"
exit $rc