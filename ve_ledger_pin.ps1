param(
    [string]$LedgerPath = ".\ve_ledger.jsonl",
    [switch]$Force
)

$pinned = '{"ts":"2025-10-31T02:50:00.0000000-04:00","actor":"VE_Helper","action":"init-ledger","hash_prev":"","hash_self":"94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546"}'

if ((Test-Path -LiteralPath $LedgerPath) -and (Get-Item -LiteralPath $LedgerPath).Length -gt 0 -and -not $Force) {
    Write-Error "Ledger already exists and is non-empty. Use -Force only when intentionally reinitializing a disposable ledger."
    exit 1
}

$pinned | Set-Content -Encoding UTF8 -NoNewline $LedgerPath
Write-Host "Pinned genesis written to $LedgerPath"
