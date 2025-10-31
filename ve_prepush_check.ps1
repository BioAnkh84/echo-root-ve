# ve_prepush_check.ps1
# normalize ledger → run audit/exec → tell you if it's safe to git push
param(
    [string]$Base = "C:\VE_Test_Suite_v0.1a",
    [switch]$ForcePin
)

Write-Host "🔎 VE pre-push check in $Base" -ForegroundColor Cyan

$ledgerPath  = Join-Path $Base "ve_ledger.jsonl"
$kernelPath  = Join-Path $Base "ve_kernel.ps1"
$pinnedJson  = '{"ts":"2025-10-31T02:50:00.0000000-04:00","actor":"VE_Helper","action":"init-ledger","hash_prev":"","hash_self":"94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546"}'

$ok = $true

# 1) make sure we're in the right folder
try {
    Set-Location $Base -ErrorAction Stop
} catch {
    Write-Host "❌ cannot cd to $Base" -ForegroundColor Red
    $ok = $false
}

if ($ok) {
    # 2) Ledger normalization
    $needPin = $false
    if ($ForcePin -or -not (Test-Path $ledgerPath)) {
        $needPin = $true
    } else {
        $raw = Get-Content $ledgerPath -Raw -Encoding UTF8
        if ($raw.Trim() -ne $pinnedJson.Trim()) {
            Write-Host "⚠️ ledger content != pinned, re-pinning" -ForegroundColor Yellow
            $needPin = $true
        }
    }

    if ($needPin) {
        $pinnedJson | Set-Content -Encoding UTF8 -NoNewline $ledgerPath
        Write-Host "✅ pinned ledger at $ledgerPath"
    } else {
        Write-Host "✅ ledger already pinned"
    }

    # 3) run kernel checks
    if (Test-Path $kernelPath) {
        Write-Host "🧾 running kernel audit..." -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File $kernelPath audit
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ audit failed (exit $LASTEXITCODE)" -ForegroundColor Red
            $ok = $false
        } else {
            Write-Host "✅ audit OK."
        }

        Write-Host "⚙️ running sample exec..." -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File $kernelPath exec 'Write-Output "VE Windows OK"'
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ exec failed (exit $LASTEXITCODE)" -ForegroundColor Red
            $ok = $false
        } else {
            Write-Host "✅ exec OK."
        }
    } else {
        Write-Host "⚠️ ve_kernel.ps1 not found — skipping audit/exec" -ForegroundColor Yellow
    }

    # 4) show final ledger
    Write-Host "`n📄 final ledger (this is what you'll commit):" -ForegroundColor Cyan
    Get-Content $ledgerPath -Encoding UTF8 | Out-Host
}

# 5) final message
if ($ok) {
    Write-Host "`n🎉 PRE-PUSH PASS — you can now run:" -ForegroundColor Green
    Write-Host "   cd `"$Base`""
    Write-Host "   git status"
    Write-Host "   git add ve_ledger.jsonl ve_prepush_check.ps1"
    Write-Host "   git commit -m `"fix: pinned ledger + prepush check`""
    Write-Host "   git push"
} else {
    Write-Host "`n🚫 PRE-PUSH FAIL — check the errors above." -ForegroundColor Red
}

# keep window open if double-clicked
if ($Host.Name -eq 'ConsoleHost') {
    Write-Host ""
    Read-Host "Press ENTER to close"
}
