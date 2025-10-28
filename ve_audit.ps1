param(
  [string]$Ledger = ".\ve_ledger.jsonl",
  [string]$Policy = ".\policy.ve.psl",
  [switch]$StrictPsi
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ledgerAbs  = (Resolve-Path (Join-Path $scriptDir $Ledger)).Path
$checkerAbs = (Resolve-Path (Join-Path $scriptDir "ve_schema_check.py")).Path
$policyAbs  = (Resolve-Path (Join-Path $scriptDir $Policy)).Path

if (-not (Test-Path $checkerAbs)) { Write-Error "Missing checker: $checkerAbs"; exit 2 }
if (-not (Test-Path $ledgerAbs))  { Write-Error "Missing ledger : $ledgerAbs";  exit 2 }

function Get-PsiFloor([string]$path){
  $floor = 1.38
  if (Test-Path $path) {
    $txt = Get-Content $path -Raw
    $m = [regex]::Match($txt,'(?ms)^\[psi\].*?floor\s*=\s*([0-9\.]+)')
    if ($m.Success) { $floor = [double]$m.Groups[1].Value }
  }
  return $floor
}

$psiMin = Get-PsiFloor $policyAbs
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $py) { Write-Error "Python not found (FAIL_ENV)"; exit 2 }

$argsList = @($checkerAbs,'--ledger',$ledgerAbs,'--psi-min',$psiMin.ToString())
if ($StrictPsi) { $argsList += '--strict-psi' }

Write-Host "Audit cmd:" -NoNewline; Write-Host " $py $($argsList -join ' ')" -ForegroundColor Cyan
& $py @argsList
exit $LASTEXITCODE