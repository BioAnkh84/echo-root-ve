param(
  [string]$Ledger = "ve_ledger.jsonl",
  [string]$TtlFile = "governance_ttl.json",
  [string]$PolicyHash = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=== Echo Root VE Health Check ===" -ForegroundColor Cyan
Write-Host "Repo:" (Get-Location)
git status -sb

if (Test-Path $TtlFile) {
  if ($PolicyHash -ne "") {
    python .\ve_quickcheck_stub.py --ledger $Ledger --show-phase --ttl-file $TtlFile --require-integrity-ok --policy-hash $PolicyHash
  } else {
    python .\ve_quickcheck_stub.py --ledger $Ledger --show-phase --ttl-file $TtlFile
  }
} else {
  Write-Host "[WARN] TTL file not found: $TtlFile (continuing without TTL)" -ForegroundColor Yellow
  python .\ve_quickcheck_stub.py --ledger $Ledger --show-phase
}
