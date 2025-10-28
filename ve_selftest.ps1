param([switch]$Clean)

$base   = (Get-Location).Path
$kernel = Join-Path $base 've_kernel.ps1'
$guard  = Join-Path $base 've_guard.ps1'
$ledger = Join-Path $base 've_ledger.jsonl'
$data   = Join-Path $base 've_data'
$snap   = Join-Path $base '.ve_snapshots'

if ($Clean) {
  Remove-Item -LiteralPath $data -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath $snap -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath $ledger -Force -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath (Join-Path $base 've_guard_log.jsonl') -Force -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Path $data -Force | Out-Null
  & $kernel status | Out-Null
  & $kernel snap -Seq 1 2>$null | Out-Null
  Write-Host "Cleaned and seeded."
}

New-Item -ItemType Directory -Path $data -Force | Out-Null

# Allow path via guard → snapshot + audit
.\ve_guard.ps1 -- 'Set-Content -Path ".\ve_data\hello.txt" -Value "selftest"'
$lines = (Get-Content $ledger | Measure-Object -Line).Lines
& $kernel audit -VerifySeq $lines

# Deny path via guard → should block
.\ve_guard.ps1 -- 'Remove-Item -Path ".\ve_data\hello.txt"' ; $rc=$LASTEXITCODE

# Print a compact summary
$latestSnap = Join-Path $base ('.ve_snapshots\seq-{0:d4}\manifest.json' -f $lines)
$ok = Test-Path -LiteralPath $latestSnap
$val = Get-Content .\ve_data\hello.txt -ErrorAction SilentlyContinue
[pscustomobject]@{
  GuardAllow_LastSeq = $lines
  VerifyManifestOK   = $ok
  FileValue          = $val
  DenyExitCode       = $rc
} | Format-List
