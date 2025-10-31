param(
    [string]$LedgerPath = ".\ve_ledger.jsonl"
)
$pinned = '{"ts":"2025-10-31T02:50:00.0000000-04:00","actor":"VE_Helper","action":"init-ledger","hash_prev":"","hash_self":"94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546"}'
$pinned | Set-Content -Encoding UTF8 -NoNewline $LedgerPath
Write-Host "✅ pinned genesis written to $LedgerPath"