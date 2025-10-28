# ve_make_artifacts.ps1
# Generate PASS and FAIL ledger artifacts, run checks, and summarize root causes.
# Usage (from your suite folder):
#   powershell -ExecutionPolicy Bypass -File .\ve_make_artifacts.ps1

param(
  [double]$psiMin = 1.38
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-Sha256([string]$text) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
  $sha = [System.Security.Cryptography.SHA256]::Create()
  $hash = $sha.ComputeHash($bytes)
  ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

function Write-NoBom([string]$Path, [string]$Text) {
  [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

# Ensure checker exists
if (-not (Test-Path .\ve_schema_check.py)) {
  Write-Error "ve_schema_check.py not found in current folder. Copy the Stability Pack files here first."
  exit 2
}

$ts = (Get-Date -Format "yyyyMMdd_HHmmss")
$artDir = Join-Path (Get-Location) ("artifacts_"+$ts)
New-Item -ItemType Directory -Path $artDir | Out-Null

# Helper: create GENESIS
function New-Genesis {
  param([string]$Path)
  $gen = @{
    time = (Get-Date).ToString("s")
    type = "GENESIS"
    actor = "VE"
    event = "INIT"
    consent = ""
    rho = 0.0; gamma = 0.0; delta = 0.0
    hash_prev = ("0" * 64)
  }
  $json = ($gen | ConvertTo-Json -Compress)
  $gen.hash_self = Get-Sha256($json)
  $line = ($gen | ConvertTo-Json -Compress)
  Write-NoBom $Path $line
  return $gen.hash_self
}

# Helper: append a valid entry
function Append-Valid {
  param([string]$Path, [string]$PrevHash, [double]$rho, [double]$gamma, [double]$delta, [string]$actor="VE", [string]$etype="EVENT")
  $entry = @{
    time = (Get-Date).ToString("s")
    type = $etype
    actor = $actor
    consent = ""
    rho = [double]::Parse("{0:N2}" -f $rho)
    gamma = [double]::Parse("{0:N2}" -f $gamma)
    delta = [double]::Parse("{0:N2}" -f $delta)
    hash_prev = $PrevHash
  }
  $json = ($entry | ConvertTo-Json -Compress)
  $entry.hash_self = Get-Sha256($json)
  $line = ($entry | ConvertTo-Json -Compress)
  Add-Content -Path $Path -Value $line -Encoding utf8
  return $entry.hash_self
}

# 1) PASS artifact
$passPath = Join-Path $artDir "pass_ledger.jsonl"
$prev = New-Genesis -Path $passPath
$prev = Append-Valid -Path $passPath -PrevHash $prev -rho 0.92 -gamma 0.82 -delta 0.21 -actor "VE" -etype "PASS"
$prev = Append-Valid -Path $passPath -PrevHash $prev -rho 0.90 -gamma 0.80 -delta 0.25 -actor "VE" -etype "PASS"

# 2) FAIL: hash chain broken (tamper last line's hash_prev)
$failHashPath = Join-Path $artDir "fail_hash.jsonl"
Copy-Item $passPath $failHashPath -Force
# Load, tamper, and rewrite last line without recomputing hash_self
$lines = Get-Content $failHashPath
$last = $lines[-1] | ConvertFrom-Json
$last.hash_prev = "deadbeef"*8  # 64 hex chars mismatch
# Re-serialize (this keeps hash_self stale → mismatch)
$lines[-1] = ($last | ConvertTo-Json -Compress)
[System.IO.File]::WriteAllLines($failHashPath, $lines, [System.Text.UTF8Encoding]::new($false))

# 3) FAIL: invalid JSON line
$failJsonPath = Join-Path $artDir "fail_json.jsonl"
Copy-Item $passPath $failJsonPath -Force
Add-Content -Path $failJsonPath -Value '{"bad":' -Encoding utf8  # truncated JSON

# 4) FAIL: psi floor violation (valid chain, low rho+gamma)
$failPsiPath = Join-Path $artDir "fail_psi.jsonl"
$prev = New-Genesis -Path $failPsiPath
$prev = Append-Valid -Path $failPsiPath -PrevHash $prev -rho 0.50 -gamma 0.60 -delta 0.10 -actor "VE" -etype "LOW_PSI"

# Run checks and capture reports
$reports = @()
$targets = @(
  @{ name="PASS"; path=$passPath },
  @{ name="FAIL_HASH"; path=$failHashPath },
  @{ name="FAIL_JSON"; path=$failJsonPath },
  @{ name="FAIL_PSI"; path=$failPsiPath }
)

foreach ($t in $targets) {
  $report = Join-Path $artDir ("{0}_report.txt" -f $t.name)
  $cmd = 'python'
  $py = (Get-Command python -ErrorAction SilentlyContinue).Source
  if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
  if ($py) { $cmd = $py }
  $args = @(".\ve_schema_check.py", "--ledger", $t.path, "--psi-min", "$psiMin")
  "== {0} ==" -f $t.name | Out-File -FilePath $report -Encoding utf8
  "Ledger: {0}" -f $t.path | Out-File -FilePath $report -Append -Encoding utf8
  & $cmd @args 2>&1 | Tee-Object -FilePath $report
  $reports += @{ name=$t.name; path=$t.path; report=$report }
}

# Summarize root causes (simple classifier based on report contents)
$summaryPath = Join-Path $artDir "summary.txt"
"Vulpine Echo — Artifact Summary ({0})" -f (Get-Date) | Out-File -FilePath $summaryPath -Encoding utf8
"psi_min = $psiMin" | Out-File -FilePath $summaryPath -Append -Encoding utf8
"" | Out-File -FilePath $summaryPath -Append -Encoding utf8

foreach ($r in $reports) {
  $txt = Get-Content $r.report -Raw
  $status = "PASS"
  $reasons = @()

  if ($txt -match '\[FAIL\]') { $status = "FAIL" }
  if ($txt -match 'invalid JSON') { $reasons += "DATA_ERROR: Invalid JSON syntax" }
  if ($txt -match 'hash_prev.*previous hash_self') { $reasons += "CHAIN_ERROR: Broken hash link" }
  if ($txt -match 'hash_self mismatch') { $reasons += "INTEGRITY_ERROR: hash_self mismatch" }
  if ($txt -match 'psi_eff=.*< psi_min') { $reasons += "POLICY_WARN: ψ below floor" }
  if ($reasons.Count -eq 0 -and $status -eq "PASS") { $reasons += "OK" }

  "{0}: {1}" -f $r.name, $status | Out-File -FilePath $summaryPath -Append -Encoding utf8
  foreach ($reason in $reasons) {
    "  - {0}" -f $reason | Out-File -FilePath $summaryPath -Append -Encoding utf8
  }
  "" | Out-File -FilePath $summaryPath -Append -Encoding utf8
}

"Done. Reports:" | Out-File -FilePath $summaryPath -Append -Encoding utf8
foreach ($r in $reports) {
  "  - {0}" -f $r.report | Out-File -FilePath $summaryPath -Append -Encoding utf8
}

Write-Host "✅ Artifacts created in: $artDir"
Get-ChildItem $artDir -File | Format-Table -AutoSize
