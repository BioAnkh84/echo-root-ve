# ve_start.ps1 — Echo Root VE operator helper (user-run)
# VE repo = governance/kernel tools
# Cipher/HUD = habitat services under E:\Echo_Nexus_Data\habitat\cipher_local

[CmdletBinding()]
param(
  [switch]$ReentryOnly,
  [switch]$StartDevCipher,
  [switch]$StartHud,
  [switch]$StartAll,
  [switch]$OpenHud,
  [switch]$Status,
  [switch]$StopAll,
  [switch]$TailLogs,
  [int]$ApiPort = 5000,
  [int]$HudPort = 5001
)

# --- UTF-8 Output Hygiene ---
$utf8 = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$env:PYTHONUTF8 = "1"

$ErrorActionPreference = "Stop"

# --- Canonical paths ---
$VeRepo     = "E:\Echo_Nexus_Data\repos\echo-root-ve"
$VePython   = Join-Path $VeRepo ".venv\Scripts\python.exe"
$Ledger     = "E:\Echo_Nexus_Data\ve_ledger.jsonl"

$DataRoot   = "E:\Echo_Nexus_Data"
$LogRoot    = Join-Path $DataRoot "logs"
$StatusDir  = Join-Path $DataRoot "status"
$StatusFile = Join-Path $StatusDir "ve_status.json"

# --- Cipher/HUD habitat (external to VE repo) ---
$CipherHabitat = "E:\Echo_Nexus_Data\habitat\cipher_local"
$HudServerPy   = Join-Path $CipherHabitat "dashboard_server.py"
$HudHtmlPath   = Join-Path $CipherHabitat "hud.html"

# Dev Cipher candidate scripts (best-effort autodetect)
$DevCipherCandidates = @(
  (Join-Path $CipherHabitat "cipher_local_chat.py"),
  (Join-Path $CipherHabitat "cipher_local_api.py"),
  (Join-Path $CipherHabitat "cipher_local.py")
)

# HUD URL (adjust if your server uses a different route)
$HudUrl = "http://127.0.0.1:$HudPort/hud"

# --- Ensure folders exist (PS-compatible) ---
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
New-Item -ItemType Directory -Force -Path $StatusDir | Out-Null

function Write-Section([string]$t) { Write-Host ""; Write-Host "=== $t ===" }
function Warn([string]$m) { Write-Host "[WARN] $m" }
function Info([string]$m) { Write-Host "[INFO] $m" }
function Ok([string]$m)   { Write-Host "[OK]  $m" }
function Fail([string]$m) { Write-Host "[ERR] $m"; throw $m }

function Require-Path([string]$p, [string]$label) {
  if (-not (Test-Path $p)) { Fail "$label not found: $p" }
}

function Get-ProcsByNeedle([string]$needle) {
  try {
    $procs = Get-CimInstance Win32_Process -ErrorAction Stop
    return $procs | Where-Object { $_.CommandLine -and $_.CommandLine.ToLower().Contains($needle.ToLower()) }
  } catch { return @() }
}

function Start-Py([string]$pyExe, [string]$scriptPath, [string]$args, [string]$tag, [string]$workDir) {
  if (-not (Test-Path $scriptPath)) { Warn "$tag script not found: $scriptPath"; return }

  $needle = [IO.Path]::GetFileName($scriptPath)
  $running = Get-ProcsByNeedle $needle
  if ($running.Count -gt 0) { Ok "$tag already running ($($running.Count) proc)."; return }

  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $outLog = Join-Path $LogRoot ("{0}_{1}_out.log" -f $tag, $stamp)
  $errLog = Join-Path $LogRoot ("{0}_{1}_err.log" -f $tag, $stamp)

  Info "Starting $tag..."
  Info "  Script: $scriptPath"
  Info "  Args:   $args"
  Info "  Out:    $outLog"
  Info "  Err:    $errLog"

  Start-Process -FilePath $pyExe `
    -ArgumentList "`"$scriptPath`" $args" `
    -WorkingDirectory $workDir `
    -WindowStyle Normal `
    -RedirectStandardOutput $outLog `
    -RedirectStandardError  $errLog
}

function Stop-ByNeedle([string]$needle, [string]$tag) {
  $procs = Get-ProcsByNeedle $needle
  if ($procs.Count -eq 0) { Ok "$tag not running."; return }
  foreach ($p in $procs) {
    try { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop; Ok "Stopped $tag pid=$($p.ProcessId)" }
    catch { Warn "Failed stopping $tag pid=$($p.ProcessId): $_" }
  }
}

function Tail-Latest([string]$prefix) {
  $latestOut = Get-ChildItem $LogRoot -Filter "${prefix}_*_out.log" -ErrorAction SilentlyContinue |
               Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $latestErr = Get-ChildItem $LogRoot -Filter "${prefix}_*_err.log" -ErrorAction SilentlyContinue |
               Sort-Object LastWriteTime -Descending | Select-Object -First 1

  if ($latestOut) {
    Write-Section "Tail OUT: $($latestOut.Name)"
    Get-Content -Path $latestOut.FullName -Tail 60
  } else {
    Warn "No OUT logs found for prefix: $prefix"
  }

  if ($latestErr) {
    Write-Section "Tail ERR: $($latestErr.Name)"
    Get-Content -Path $latestErr.FullName -Tail 60
  } else {
    Warn "No ERR logs found for prefix: $prefix"
  }
}

function Write-StatusFile {
  $now = (Get-Date).ToString("s")
  $status = [ordered]@{
    updated_local = $now
    ve_repo = $VeRepo
    ve_python = $VePython
    ledger = $Ledger
    cipher_habitat = $CipherHabitat
    api_port = $ApiPort
    hud_port = $HudPort
    hud_url = $HudUrl
    running = @{
      hud_backend = (Get-ProcsByNeedle "dashboard_server.py" | Select-Object ProcessId,CommandLine)
      dev_cipher  = (Get-ProcsByNeedle "cipher_local" | Select-Object ProcessId,CommandLine)
    }
  }
  $status | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path $StatusFile
  Ok "Wrote status: $StatusFile"
}

function Show-Status {
  Write-Section "Echo Root VE Operator Status"
  Info "VE Repo:     $VeRepo"
  Info "VE Python:   $VePython"
  Info "Ledger:      $Ledger"
  Info "Habitat:     $CipherHabitat"
  Info "Ports:       API=$ApiPort HUD=$HudPort"
  Info "HUD URL:     $HudUrl"
  Info "Status file: $StatusFile"
  Write-Host ""

  $hb = Get-ProcsByNeedle "dashboard_server.py"
  if ($hb.Count -gt 0) { Ok "HUD backend running ($($hb.Count) proc)"; } else { Warn "HUD backend not running"; }

  $dc = Get-ProcsByNeedle "cipher_local"
  if ($dc.Count -gt 0) { Ok "Dev Cipher appears running ($($dc.Count) proc)"; } else { Warn "Dev Cipher not running"; }
}

# --- Validate VE core paths ---
Require-Path $VeRepo "VE Repo"
Require-Path $VePython "VE venv python"
Require-Path $Ledger "VE ledger"

# --- Export useful env ---
$env:VE_REPO     = $VeRepo
$env:VE_PYTHON   = $VePython
$env:VE_LEDGER   = $Ledger
$env:VE_API_PORT = "$ApiPort"
$env:VE_HUD_PORT = "$HudPort"

Set-Location $VeRepo

Write-Section "Echo Root VE Start"
Info "Operator mode (user-run). SYSTEM boot uses E:\Echo_Nexus_Data\service\echo_boot.ps1"

if ($StopAll) {
  Write-Section "Stopping operator-session services"
  Stop-ByNeedle "dashboard_server.py" "HudBackend"
  Stop-ByNeedle "cipher_local" "DevCipher"
  Write-StatusFile
  return
}

if ($Status) {
  Show-Status
  Write-StatusFile
  return
}

# 1) VE reentry
Write-Section "VE Reentry (syscheck + quickcheck)"
try {
  & ".\ve_reentry.ps1"
  if ($LASTEXITCODE -eq 0) { Ok "Reentry rc=0 (clean pass)" }
  else { Warn "Reentry rc=$LASTEXITCODE (check output above)" }
} catch {
  Warn "Reentry threw: $_"
}

if ($ReentryOnly) {
  Write-StatusFile
  return
}

if ($StartAll) {
  $StartDevCipher = $true
  $StartHud = $true
  $OpenHud = $true
}

# 2) Start HUD backend (external habitat)
if ($StartHud) {
  Write-Section "Start HUD Backend"
  Require-Path $CipherHabitat "Cipher habitat"
  Require-Path $HudServerPy "HUD server script (dashboard_server.py)"

  $hudArgs = "--port $HudPort"
  Start-Py -pyExe $VePython -scriptPath $HudServerPy -args $hudArgs -tag "hud_backend" -workDir $CipherHabitat
}

# 3) Start Dev Cipher (external habitat)
if ($StartDevCipher) {
  Write-Section "Start Dev Cipher"
  Require-Path $CipherHabitat "Cipher habitat"

  $dev = $DevCipherCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
  if (-not $dev) {
    Warn "No dev cipher script found in habitat. Checked:`n - $($DevCipherCandidates -join "`n - ")"
  } else {
    $devArgs = "--port $ApiPort"
    Start-Py -pyExe $VePython -scriptPath $dev -args $devArgs -tag "dev_cipher" -workDir $CipherHabitat
  }
}

if ($OpenHud) {
  Write-Section "Open HUD"
  Info "Opening: $HudUrl"
  Start-Process $HudUrl | Out-Null
}

if ($TailLogs) {
  Tail-Latest "hud_backend"
  Tail-Latest "dev_cipher"
}

Show-Status
Write-StatusFile

Write-Host ""
Ok "Environment ready."
Write-Host ""