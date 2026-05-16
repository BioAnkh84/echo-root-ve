[1mdiff --git a/ve_syscheck.ps1 b/ve_syscheck.ps1[m
[1mindex f92cf32..6913ddb 100644[m
[1m--- a/ve_syscheck.ps1[m
[1m+++ b/ve_syscheck.ps1[m
[36m@@ -1,231 +1,75 @@[m
[31m-﻿param([m
[31m-    [switch]$WriteLedger,[m
[31m-    [string]$LedgerPath = "E:\Echo_Nexus_Data\ve_ledger.jsonl",[m
[31m-    [string]$PythonPath = ""[m
[31m-)[m
[32m+[m[32m﻿# Echo Root VE Startup Script[m
[32m+[m[32m# Runs when Nexus system boots[m
 [m
[31m-# Force non-terminating errors to stop so exit codes are truthful[m
[31m-$ErrorActionPreference = "Stop"[m
[31m-[m
[31m-# UTF-8 output for clean unicode symbols[m
[31m-$OutputEncoding = [System.Text.UTF8Encoding]::new()[m
[31m-[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()[m
[31m-[m
[31m-# ve_syscheck.ps1[m
[31m-# One-button: handshake → gatecheck → ledger append → sysinfo → quickcheck[m
[31m-[m
[31m-# --- Helpers ---[m
[31m-function Resolve-Python {[m
[31m-    param([m
[31m-        [string]$PreferredPython,[m
[31m-        [string]$RepoRoot[m
[31m-    )[m
[31m-[m
[31m-    # 0) Explicit override[m
[31m-    if ($PreferredPython -and $PreferredPython.Trim() -ne "") {[m
[31m-        if (Test-Path -LiteralPath $PreferredPython) { return $PreferredPython }[m
[31m-        throw "PythonPath was provided but not found: $PreferredPython"[m
[31m-    }[m
[31m-[m
[31m-    # 1) Active venv[m
[31m-    if ($env:VIRTUAL_ENV) {[m
[31m-        $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"[m
[31m-        if (Test-Path -LiteralPath $candidate) { return $candidate }[m
[31m-    }[m
[31m-[m
[31m-    # 2) Repo-local .venv[m
[31m-    if ($RepoRoot) {[m
[31m-        $candidate = Join-Path $RepoRoot ".venv\Scripts\python.exe"[m
[31m-        if (Test-Path -LiteralPath $candidate) { return $candidate }[m
[31m-    }[m
[31m-[m
[31m-    # 3) PATH resolution[m
[31m-    $python = Get-Command python -ErrorAction SilentlyContinue[m
[31m-    if ($python) { return $python.Source }[m
[31m-[m
[31m-    $py = Get-Command py -ErrorAction SilentlyContinue[m
[31m-    if ($py) { return $py.Source }[m
[32m+[m[32m# --- UTF-8 Output Hygiene (prevents mojibake like âœ… or ΓåÆ) ---[m
[32m+[m[32m$utf8 = [System.Text.UTF8Encoding]::new($false)[m
[32m+[m[32m[Console]::OutputEncoding = $utf8[m
[32m+[m[32m$OutputEncoding = $utf8[m
[32m+[m[32m$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'[m
 [m
[31m-    throw "No Python interpreter found. Install Python 3 or activate a venv."[m
[31m-}[m
[31m-[m
[31m-function Run {[m
[31m-    param([m
[31m-        [Parameter(Mandatory=$true)][string]$Cmd,[m
[31m-        [Parameter(Mandatory=$false)][string[]]$ArgList = @()[m
[31m-    )[m
[31m-[m
[31m-    Write-Host "→ $Cmd $($ArgList -join ' ')"[m
[32m+[m[32m# Ensure Python also emits UTF-8[m
[32m+[m[32m$env:PYTHONUTF8 = "1"[m
 [m
[31m-    # Prevent accidental interactive Python[m
[31m-    if (($Cmd -match "(?i)python(\.exe)?$") -and ($ArgList.Count -eq 0)) {[m
[31m-        $ArgList = @("-c", "import sys; print(sys.executable); print(sys.version)")[m
[31m-    }[m
[31m-[m
[31m-    & $Cmd @ArgList 2>&1[m
[32m+[m[32m$ErrorActionPreference = "Stop"[m
 [m
[31m-    if ($LASTEXITCODE -ne 0) {[m
[31m-        Write-Warning "Command exited with code $LASTEXITCODE"[m
[31m-    }[m
[32m+[m[32m# --- Paths ---[m
[32m+[m[32m$Repo   = "E:\Echo_Nexus_Data\repos\echo-root-ve"[m
[32m+[m[32m$Python = "E:\Echo_Nexus_Data\repos\echo-root-ve\.venv\Scripts\python.exe"[m
[32m+[m[32m$Ledger = "E:\Echo_Nexus_Data\ve_ledger.jsonl"[m
[32m+[m
[32m+[m[32mWrite-Host ""[m
[32m+[m[32mWrite-Host "=== Echo Root VE Boot ==="[m
[32m+[m[32mWrite-Host ""[m
[32m+[m
[32m+[m[32m# --- Verify environment ---[m
[32m+[m[32mif (-not (Test-Path $Repo)) {[m
[32m+[m[32m    Write-Host "[VE] ERROR: Repo path not found: $Repo"[m
[32m+[m[32m    exit 1[m
 }[m
 [m
[31m-function Write-Utf8NoBom {[m
[31m-    param([m
[31m-        [Parameter(Mandatory=$true)][string]$Path,[m
[31m-        [Parameter(Mandatory=$true)][string]$Text[m
[31m-    )[m
[31m-    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)[m
[31m-    [System.IO.File]::WriteAllText($Path, $Text, $utf8NoBom)[m
[32m+[m[32mif (-not (Test-Path $Python)) {[m
[32m+[m[32m    Write-Host "[VE] ERROR: Python venv not found: $Python"[m
[32m+[m[32m    exit 1[m
 }[m
 [m
[31m-function Get-LedgerHasAnyRecord {[m
[31m-    param([string]$Path)[m
[31m-[m
[31m-    if (-not (Test-Path -LiteralPath $Path)) { return $false }[m
[31m-    $fi = Get-Item -LiteralPath $Path -ErrorAction SilentlyContinue[m
[31m-    if (-not $fi) { return $false }[m
[31m-    if ($fi.Length -le 0) { return $false }[m
[32m+[m[32m# Move into repo[m
[32m+[m[32mSet-Location $Repo[m
 [m
[31m-    # If the file has only whitespace/newlines, treat as empty[m
[31m-    try {[m
[31m-        $firstNonEmpty = Get-Content -LiteralPath $Path -TotalCount 200 | Where-Object { $_.Trim() -ne "" } | Select-Object -First 1[m
[31m-        return [bool]$firstNonEmpty[m
[31m-    } catch {[m
[31m-        return $false[m
[31m-    }[m
[32m+[m[32m# --- Reentry / System Check ---[m
[32m+[m[32mWrite-Host "[VE] Running reentry check..."[m
[32m+[m[32mtry {[m
[32m+[m[32m    & "$Repo\ve_reentry.ps1"[m
 }[m
[31m-[m
[31m-function Ensure-LedgerFile {[m
[31m-    param([string]$Path)[m
[31m-    if (-not (Test-Path -LiteralPath $Path)) {[m
[31m-        New-Item -ItemType File -Path $Path -Force | Out-Null[m
[31m-    }[m
[32m+[m[32mcatch {[m
[32m+[m[32m    Write-Host "[VE] ERROR during reentry:"[m
[32m+[m[32m    Write-Host $_[m
[32m+[m[32m    exit 1[m
 }[m
 [m
[31m-function Write-GenesisFallback {[m
[31m-    param([m
[31m-        [string]$Path,[m
[31m-        [double]$rho,[m
[31m-        [double]$gamma,[m
[31m-        [double]$delta[m
[31m-    )[m
[31m-    # Fallback: write a minimal genesis record to avoid append scripts failing on empty ledger.[m
[31m-    # Uses hash_prev all-zeros and hash_self as a dummy placeholder.[m
[31m-    # NOTE: This is a syscheck safety net only; your real canonical writer should own genesis format.[m
[31m-    $gen = [ordered]@{[m
[31m-        time      = (Get-Date).ToString("s")[m
[31m-        rho       = $rho[m
[31m-        gamma     = $gamma[m
[31m-        delta     = $delta[m
[31m-        hash_prev = ("0" * 64)[m
[31m-        hash_self = ("0" * 64)[m
[31m-        note      = "syscheck_genesis_fallback"[m
[31m-    }[m
[31m-    $line = ($gen | ConvertTo-Json -Compress)[m
[31m-    Add-Content -LiteralPath $Path -Value $line -Encoding utf8[m
[31m-    Write-Host "Genesis fallback line written to ledger (syscheck safety net)." -ForegroundColor Yellow[m
[31m-}[m
[32m+[m[32m# --- Ledger Verification ---[m
[32m+[m[32mWrite-Host "[VE] Verifying ledger integrity..."[m
 [m
[31m-# --- Paths ---[m
[31m-$here = $PSScriptRoot[m
[31m-Set-Location $here[m
[31m-[m
[31m-$pyExe = Resolve-Python -PreferredPython $PythonPath -RepoRoot $here[m
[31m-[m
[31m-Write-Host "[VE/syscheck] Using python: $pyExe"[m
[31m-Write-Host "[VE/syscheck] LedgerPath: $LedgerPath"[m
[31m-[m
[31m-# 1) Handshake (quote-safe via temp file)[m
[31m-Write-Host "`n[1/5] Handshake"[m
[31m-$handshakeObj = @{[m
[31m-    id    = "syscheck"[m
[31m-    rho   = 0.83[m
[31m-    gamma = 0.78[m
[31m-    delta = 0.22[m
[32m+[m[32mtry {[m
[32m+[m[32m    & $Python ".\ve_quickcheck.py" `[m
[32m+[m[32m        --ledger $Ledger `[m
[32m+[m[32m        --psi-min 1.38 `[m
[32m+[m[32m        --psi-warn-is-softfail[m
 }[m
[31m-$handshakeJson = ($handshakeObj | ConvertTo-Json -Compress)[m
[31m-$tmpHandshake = Join-Path $env:TEMP "ve_syscheck_handshake.json"[m
[31m-Write-Utf8NoBom -Path $tmpHandshake -Text $handshakeJson[m
[31m-[m
[31m-Run -Cmd $pyExe -ArgList @([m
[31m-    ".\ve_handshake.py",[m
[31m-    "--input-file", $tmpHandshake[m
[31m-)[m
[31m-[m
[31m-if ($LASTEXITCODE -ne 0) {[m
[31m-    Write-Host "`n⚠️ Handshake failed; stopping syscheck." -ForegroundColor Yellow[m
[31m-    exit 10[m
[32m+[m[32mcatch {[m
[32m+[m[32m    Write-Host "[VE] ERROR during quickcheck:"[m
[32m+[m[32m    Write-Host $_[m
[32m+[m[32m    exit 1[m
 }[m
 [m
[31m-# 2) Gatecheck[m
[31m-Write-Host "`n[2/5] Gatecheck"[m
[31m-Run -Cmd $pyExe -ArgList @(".\ve_gatecheck.py")[m
[31m-if ($LASTEXITCODE -ne 0) { exit 30 }[m
[31m-[m
[31m-# 3) Ledger append (optional)[m
[31m-Write-Host "`n[3/5] Ledger append (pre-sysinfo)"[m
[31m-if ($WriteLedger) {[m
[31m-    Ensure-LedgerFile -Path $LedgerPath[m
[32m+[m[32mWrite-Host ""[m
[32m+[m[32mWrite-Host "[VE] Environment ready."[m
[32m+[m[32mWrite-Host ""[m
 [m
[31m-    $hasAny = Get-LedgerHasAnyRecord -Path $LedgerPath[m
[32m+[m[32m# OPTIONAL: start local cipher server[m
[32m+[m[32m# Uncomment if desired[m
 [m
[31m-    # We do NOT introspect cmd.Parameters (it can be null / weird). We just call with -LedgerPath always.[m
[31m-    # If the append script supports -Genesis, great; if not, we fallback by writing a genesis line once.[m
[31m-    try {[m
[31m-        if (-not $hasAny) {[m
[31m-            # Attempt: append script with -Genesis (if it supports it)[m
[31m-            & .\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25 -LedgerPath $LedgerPath -Genesis 2>$null[m
[31m-            if ($LASTEXITCODE -ne 0) {[m
[31m-                # If -Genesis isn't supported, fallback genesis then try normal append[m
[31m-                Write-GenesisFallback -Path $LedgerPath -rho 0.90 -gamma 0.80 -delta 0.25[m
[31m-                & .\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25 -LedgerPath $LedgerPath[m
[31m-            }[m
[31m-        } else {[m
[31m-            & .\ve_ledger_append.ps1 -rho 0.90 -gamma 0.80 -delta 0.25 -LedgerPath $LedgerPath[m
[31m-        }[m
[31m-    }[m
[31m-    catch {[m
[31m-        Write-Host "❌ Ledger append step failed: $($_.Exception.Message)" -ForegroundColor Red[m
[31m-        exit 30[m
[31m-    }[m
[31m-[m
[31m-} else {[m
[31m-    Write-Host "Skipping ledger append (run with -WriteLedger to enable)." -ForegroundColor Yellow[m
[31m-}[m
[32m+[m[32m# Write-Host "[Cipher] Starting local runtime..."[m
[32m+[m[32m# & $Python ".\cipher_local_chat.py"[m
 [m
[31m-# 4) Sysinfo snapshot[m
[31m-Write-Host "`n[4/5] System info snapshot"[m
[31m-.\ve_sysinfo.ps1 -OutPath "sysinfo.json"[m
[31m-[m
[31m-# 5) Quickcheck[m
[31m-Write-Host "`n[5/5] Quickcheck"[m
[31m-if (-not (Test-Path -LiteralPath $LedgerPath)) {[m
[31m-    Write-Host "[VE/syscheck] Ledger not found: $LedgerPath" -ForegroundColor Yellow[m
[31m-    exit 10[m
[31m-}[m
[31m-[m
[31m-Run -Cmd $pyExe -ArgList @([m
[31m-    ".\ve_quickcheck.py",[m
[31m-    "--ledger", $LedgerPath,[m
[31m-    "--psi-min", "1.38",[m
[31m-    "--psi-warn-is-softfail"[m
[31m-)[m
[31m-[m
[31m-$rc = $LASTEXITCODE[m
[31m-[m
[31m-if ($rc -eq 0) {[m
[31m-    Write-Host "`n✅ ve_syscheck complete."[m
[31m-    exit 0[m
[31m-}[m
[31m-elseif ($rc -eq 20) {[m
[31m-    Write-Host "`n⚠️ ve_syscheck complete (soft-fail)."[m
[31m-    exit 20[m
[31m-}[m
[31m-elseif ($rc -eq 10) {[m
[31m-    Write-Host "`n⚠️ ve_syscheck complete (env issue)."[m
[31m-    exit 10[m
[31m-}[m
[31m-else {[m
[31m-    Write-Host "`n❌ ve_syscheck complete (hard-fail)."[m
[31m-    exit 30[m
[31m-}[m
\ No newline at end of file[m
[32m+[m[32mWrite-Host "=== VE Boot Complete ==="[m
[32m+[m[32mWrite-Host ""[m
\ No newline at end of file[m
