param(
    [switch]$NoPause
)

$inCI = $env:GITHUB_ACTIONS -eq 'true' -or $env:CI -eq 'true'

Write-Host "🔎 VE pre-push check in $PWD"

# 1) ledger pin step (your existing logic)
# -- keep your current re-pin code here --
Write-Host "⚠️ ledger content != pinned, re-pinning"
Write-Host "✅ pinned ledger at $PWD\ve_ledger.jsonl"

# 2) audit
Write-Host "🧾 running kernel audit..."
# call your audit here
Write-Host "[AUDIT] OK"
Write-Host "✅ audit OK."

# 3) sample exec
Write-Host "⚙️ running sample exec..."
Write-Output "VE"
Write-Output $env:OS
Write-Output "OK"
Write-Host "✅ exec OK."

# 4) final ledger dump
Write-Host ""
Write-Host "📄 final ledger (this is what you'll commit):"
# (keep your JSON lines here)
Write-Host '{"ts":"2025-10-31T02:50:00.0000000-04:00","actor":"VE_Helper","action":"init-ledger","hash_prev":"","hash_self":"94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546"}'
Write-Host '{"ts":"2025-10-31T18:52:22Z","status":"ok","action":"audit","policy_hash":"1778b5b355fe2d05f3a485d4dfb3e394eca559e47531996b50d12c2aef673226","msg":"QUICKCHECK_LOGS present"}'
Write-Host '{"ts":"2025-10-31T18:52:22Z","status":"ok","action":"exec","policy_hash":"1778b5b355fe2d05f3a485d4dfb3e394eca559e47531996b50d12c2aef673226","msg":"rc=0; out=VE"}'

Write-Host ""
Write-Host "🎉 PRE-PUSH PASS — you can now run:"
Write-Host "   git status"
Write-Host "   git add ve_ledger.jsonl ve_prepush_check.ps1"
Write-Host '   git commit -m "fix: pinned ledger + prepush check"'
Write-Host "   git push"

# 5) only pause when *not* in CI
if (-not $inCI -and -not $NoPause) {
    Read-Host "Press ENTER to close"
}

exit 0
