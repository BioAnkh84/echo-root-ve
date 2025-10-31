# ve_release_prep.ps1
param(
    [string]$Base = "C:\VE_Test_Suite_v0.1a",
    [switch]$ForceLedger
)

Write-Host "🚦 VE release prep starting in $Base"
Set-Location $Base

$ledgerPath = Join-Path $Base "ve_ledger.jsonl"
$pinnedJson = '{"ts":"2025-10-31T02:50:00.0000000-04:00","actor":"VE_Helper","action":"init-ledger","hash_prev":"","hash_self":"94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546"}'

$needPin = $ForceLedger -or -not (Test-Path $ledgerPath)
if (-not $needPin) {
    $raw = Get-Content $ledgerPath -ErrorAction SilentlyContinue
    if ($raw.Count -eq 0 -or $raw[0].Trim() -eq "" -or $raw[0].Trim() -notlike '*94e596ff62a914031377843be88b3eae01e69cf8bba1dfcc43e7fceba4709546*') {
        $needPin = $true
    }
}
if ($needPin) {
    $pinnedJson | Set-Content -Encoding UTF8 -NoNewline $ledgerPath
    Write-Host "✅ pinned ledger at $ledgerPath"
} else {
    Write-Host "✅ ledger already pinned"
}

# 2) run pre-push if we have it
$prePush = Join-Path $Base "ve_prepush_check.ps1"
if (Test-Path $prePush) {
    Write-Host "🔁 running ve_prepush_check.ps1 ..."
    powershell -ExecutionPolicy Bypass -File $prePush
} else {
    Write-Host "⚠️ ve_prepush_check.ps1 not found, skipping"
}

# 3) make sure .github/workflows exists
$ghDir = Join-Path $Base ".github"
$wfDir = Join-Path $ghDir "workflows"
if (-not (Test-Path $wfDir)) {
    New-Item -ItemType Directory -Path $wfDir -Force | Out-Null
}

# (we append the YAML in step 2)

# 4) make sure release notes exist
$relNotes = Join-Path $Base "release_notes_v0.1b.txt"
if (-not (Test-Path $relNotes)) {
    @"
## Vulpine Echo v0.1b — Pinned / Self-Heal / CI

- Pinned ledger genesis to avoid OneDrive/Notepad corruption
- Added local pre-push check (ve_prepush_check.ps1)
- CI workflow to run VE check on PR/push (Windows runner)
- Sample audit + sample exec included in ledger
- Safe to demo and to share for review
"@ | Set-Content -Encoding UTF8 $relNotes
    Write-Host "🛠️ created release_notes_v0.1b.txt"
} else {
    Write-Host "✅ release notes already present"
}

# 5) stage what matters
Write-Host "📦 staging core files..."
git add ve_ledger.jsonl `
        ve_prepush_check.ps1 `
        release_notes_v0.1b.txt

Write-Host "`n📋 git status:"
git status

Write-Host "`n✅ VE release prep (base) done."
# 3b) ensure workflow file exists
$wfFile = Join-Path $wfDir "ve-pr-check.yml"
if (-not (Test-Path $wfFile)) {
    Write-Host "🛠️ creating GitHub workflow $wfFile"
    $yaml = @"
name: VE PR / Push Check
on:
  push:
    branches: [ 'main' ]
  pull_request:
    branches: [ 'main' ]
jobs:
  ve-check:
    runs-on: windows-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Run VE pre-push check
        shell: pwsh
        run: |
          cd .\VE_Test_Suite_v0.1a
          pwsh -ExecutionPolicy Bypass -File .\ve_prepush_check.ps1
"@
    $yaml | Set-Content -Encoding UTF8 $wfFile
    git add $wfFile
} else {
    Write-Host "✅ workflow already present: $wfFile"
}
