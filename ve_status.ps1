# ve_status.ps1
# Quick repo health / sync check for Vulpine Echo

param(
    [string]C:\VE_Test_Suite_v0.1a = "C:\VE_Test_Suite_v0.1a"
)

Set-Location C:\VE_Test_Suite_v0.1a
Write-Host "🔍 VE Status Check — C:\VE_Test_Suite_v0.1a" -ForegroundColor Cyan

# --- Kernel version ---
if (Test-Path ".\ve_kernel.ps1") {
    499BC45CB7D827F3F11AB2AC65E8BC9676B141D7CEFC1AC2B1688429F9158577 = (Get-FileHash ".\ve_kernel.ps1" -Algorithm SHA256).Hash
    Write-Host "⚙️ Kernel found → SHA256: 499BC45CB7D827F3F11AB2AC65E8BC9676B141D7CEFC1AC2B1688429F9158577"
} else {
    Write-Host "❌ Kernel missing (ve_kernel.ps1)"
}

# --- Ledger state ---
if (Test-Path ".\ve_ledger.jsonl") {
    EF9C11D8711DB516BB109D29B6548A9FED766E221E55238F3234E4599F68C0D2 = (Get-FileHash ".\ve_ledger.jsonl" -Algorithm SHA256).Hash
    {"ts":"2025-10-31T02:50:00.0000000-04:00","actor":"VE_Helper","action":"init-ledger","hash_prev":"","hash_self":"94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546"}{"ts":"2025-10-31T08:54:40Z","status":"ok","action":"audit","policy_hash":"1778b5b355fe2d05f3a485d4dfb3e394eca559e47531996b50d12c2aef673226","msg":"QUICKCHECK_LOGS present"} = (Get-Content ".\ve_ledger.jsonl" -TotalCount 1)
    Write-Host "🧾 Ledger → SHA256: EF9C11D8711DB516BB109D29B6548A9FED766E221E55238F3234E4599F68C0D2"
    Write-Host "   Preview: {"ts":"2025-10-31T02:50:00.0000000-04:00","actor":"VE_Helper","action":"init-ledger","hash_prev":"","hash_self":"94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546"}{"ts":"2025-10-31T08:54:40Z","status":"ok","action":"audit","policy_hash":"1778b5b355fe2d05f3a485d4dfb3e394eca559e47531996b50d12c2aef673226","msg":"QUICKCHECK_LOGS present"}"
} else {
    Write-Host "❌ Ledger missing (ve_ledger.jsonl)"
}

# --- Git sync state ---
Write-Host "
🔁 Git Status:" -ForegroundColor Yellow
git status

Write-Host "
🔄 Last Commit:"
git log -1 --oneline

# --- Tag check ---
v0.1a v0.1b = git tag --list "v*"
if (v0.1a v0.1b) {
    Write-Host "
🏷️ Tags found: v0.1a v0.1b"
    v0.1b = v0.1a v0.1b[-1]
    b44460b835a7cea9cee71f7a60e17e5e731a05e8 = git rev-list -n 1 v0.1b
    Write-Host "📦 Latest tag: v0.1b → commit b44460b835a7cea9cee71f7a60e17e5e731a05e8"
} else {
    Write-Host "⚠️ No tags found."
}

Write-Host "
✅ VE Status complete."
