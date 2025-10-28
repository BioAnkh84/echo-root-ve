# ve_fullstack.ps1
<#
Vulpine Echo — Full Stack Runner v0.2
One file to rule the quick test loop:
  1) Unblock local .ps1 files
  2) Ensure helper Python scripts exist (write minimal versions if missing)
  3) Detect Python (python or py)
  4) Handshake → Gatecheck → Ledger Append → Sysinfo → Quickcheck
  5) Write a clean log (ve_run_YYYYMMDD_HHMMSS.log)

Usage:
  - If policy blocks execution, launch with:
      powershell -ExecutionPolicy Bypass -File .\ve_fullstack.ps1

Output files (in current folder):
  - ledger.jsonl
  - sysinfo.json
  - ve_run_TIMESTAMP.log
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------- Utilities ----------

function Write-Section($title) {
    $line = "-" * ($title.Length + 4)
    Write-Host "`n$line"
    Write-Host "| $title |"
    Write-Host "$line`n"
}

function Resolve-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return $py.Source }
    throw "No Python interpreter found on PATH. Install Python 3.8+ or add it to PATH."
}

function Ensure-File($path, [string]$content) {
    if (-not (Test-Path -Path $path)) {
        $dir = Split-Path -Parent $path
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
        $content | Out-File -FilePath $path -Encoding utf8 -Force
        Write-Host "Created $path"
    }
}

function Get-Sha256([string]$text) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

# ---------- Unblock local scripts (best-effort) ----------
try {
    Get-ChildItem . -Filter *.ps1 -ErrorAction SilentlyContinue | Unblock-File
} catch { }

# ---------- Paths ----------
$here = Get-Location
$logName = "ve_run_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss")
$logPath = Join-Path $here.Path $logName

# Begin logging
"Vulpine Echo Full Stack v0.2  ::  {0}" -f (Get-Date) | Out-File -FilePath $logPath -Encoding utf8

function Log($msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $msg
    $line | Tee-Object -FilePath $logPath -Append
}

# ---------- Ensure helper scripts exist (minimal versions) ----------

$py_handshake = @'
import json, argparse, hashlib, time

p = argparse.ArgumentParser(description="PowerShell→Python JSON handshake test")
p.add_argument("--input", required=True, help="JSON string")
args = p.parse_args()

data = json.loads(args.input)
data["timestamp"] = time.time()
data["hash_self"] = hashlib.sha256(args.input.encode()).hexdigest()
print(json.dumps(data, indent=2, sort_keys=True))
'@

$py_gatecheck = @'
import random, json

def gate(rho, gamma, delta):
    if rho>=0.70 and gamma>=0.70 and delta<=0.30:
        return "PROCEED"
    elif delta>0.40 or gamma<0.65:
        return "ABORT"
    else:
        return "PAUSE"

sample = [{"rho":round(random.uniform(0.5,1),2),
           "gamma":round(random.uniform(0.5,1),2),
           "delta":round(random.uniform(0,0.5),2)} for _ in range(5)]
for s in sample:
    s["decision"] = gate(**s)
print(json.dumps(sample, indent=2))
'@

$ps_ledger_append = @'
param(
    [string]$LedgerPath = "ledger.jsonl",
    [double]$rho = 0.81,
    [double]$gamma = 0.77,
    [double]$delta = 0.29
)

function Get-Sha256([string]$text) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = $sha.ComputeHash($bytes)
    ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

if (-not (Test-Path -Path $LedgerPath)) {
    $genesis = @{
        time = (Get-Date).ToString("s")
        type = "GENESIS"
        rho = 0.0; gamma = 0.0; delta = 0.0
        hash_prev = ("0" * 64)
    }
    $genesis.hash_self = Get-Sha256(($genesis | ConvertTo-Json -Compress))
    ($genesis | ConvertTo-Json -Compress) | Out-File -FilePath $LedgerPath -Encoding utf8
}

$lastLine = Get-Content $LedgerPath -Tail 1
$lastObj = $lastLine | ConvertFrom-Json
$prevHash = $lastObj.hash_self
if (-not $prevHash) { $prevHash = ("0" * 64) }

$entry = @{
    time = (Get-Date).ToString("s")
    rho = [double]::Parse("{0:N2}" -f $rho)
    gamma = [double]::Parse("{0:N2}" -f $gamma)
    delta = [double]::Parse("{0:N2}" -f $delta)
    hash_prev = $prevHash
}
$json = ($entry | ConvertTo-Json -Compress)
$entry.hash_self = Get-Sha256($json)
$jsonFinal = ($entry | ConvertTo-Json -Compress)
Add-Content -Path $LedgerPath -Value $jsonFinal
Write-Host "Appended entry with hash_prev=$prevHash"
Write-Host "hash_self=$($entry.hash_self)"
'@

$py_quickcheck = @'
import argparse, json, hashlib, sys

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

ap = argparse.ArgumentParser()
ap.add_argument("--ledger", default="ledger.jsonl")
ap.add_argument("--psi-min", type=float, default=1.38)
args = ap.parse_args()

ok = True
prev_hash = None
line_num = 0

with open(args.ledger, "r", encoding="utf-8") as f:
    for line in f:
        line_num += 1
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as e:
            print(f"[ERROR] Line {line_num}: invalid JSON: {e}")
            ok = False
            continue

        if prev_hash is not None and obj.get("hash_prev") != prev_hash:
            print(f"[ERROR] Line {line_num}: hash_prev mismatch")
            ok = False

        check_obj = {k:v for k,v in obj.items() if k != "hash_self"}
        recomputed = sha256(json.dumps(check_obj, separators=(',',':'), ensure_ascii=False))
        if obj.get("hash_self") != recomputed:
            print(f"[ERROR] Line {line_num}: hash_self mismatch")
            ok = False

        prev_hash = obj.get("hash_self")

        if "rho" in obj and "gamma" in obj:
            psi_eff = obj["rho"] + obj["gamma"]
            if psi_eff < args.psi_min:
                print(f"[WARN] Line {line_num}: psi_eff={psi_eff:.2f} < psi_min {args.psi_min:.2f}")

if ok:
    print("[OK] Ledger checks passed.")
    sys.exit(0)
else:
    print("[FAIL] One or more checks failed.")
    sys.exit(2)
'@

$ps_sysinfo = @'
param([string]$OutPath = "sysinfo.json")
$sys = @{
    Computer = $env:COMPUTERNAME
    User     = $env:USERNAME
    OS       = (Get-CimInstance Win32_OperatingSystem).Caption
    Version  = (Get-CimInstance Win32_OperatingSystem).Version
    Build    = (Get-CimInstance Win32_OperatingSystem).BuildNumber
    CPU      = (Get-CimInstance Win32_Processor).Name
    Cores    = (Get-CimInstance Win32_Processor).NumberOfCores
    RAM_GB   = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
    GPU      = (Get-CimInstance Win32_VideoController | Select-Object -First 1 -ExpandProperty Name)
    Date     = (Get-Date).ToString("s")
}
$sys | ConvertTo-Json -Depth 4 | Out-File -Encoding utf8 $OutPath
Write-Host "System snapshot -> $OutPath"
'@

Ensure-File -path "ve_handshake.py" -content $py_handshake
Ensure-File -path "ve_gatecheck.py" -content $py_gatecheck
Ensure-File -path "ve_ledger_append.ps1" -content $ps_ledger_append
Ensure-File -path "ve_quickcheck_stub.py" -content $py_quickcheck
Ensure-File -path "ve_sysinfo.ps1" -content $ps_sysinfo

# ---------- Detect Python ----------
$pyExe = Resolve-Python
Log "Python at: $pyExe"

# ---------- 1) Handshake ----------
Write-Section "1/5 Handshake"
$payload = (@{ id="fullstack"; rho=0.84; gamma=0.79; delta=0.23 } | ConvertTo-Json -Compress)
Log "Calling handshake with payload: $payload"
$hOut = & "$pyExe" ".\ve_handshake.py" "--input" "$payload" 2>&1
$hOut | Tee-Object -FilePath $logPath -Append
if ($LASTEXITCODE -ne 0) { throw "Handshake failed (exit $LASTEXITCODE)" }

# ---------- 2) Gatecheck ----------
Write-Section "2/5 Gatecheck"
$gOut = & "$pyExe" ".\ve_gatecheck.py" 2>&1
$gOut | Tee-Object -FilePath $logPath -Append
if ($LASTEXITCODE -ne 0) { throw "Gatecheck failed (exit $LASTEXITCODE)" }

# ---------- 3) Ledger append ----------
Write-Section "3/5 Ledger Append"
$laOut = & ".\ve_ledger_append.ps1" -rho 0.90 -gamma 0.80 -delta 0.25 2>&1
$laOut | Tee-Object -FilePath $logPath -Append

# ---------- 4) Sysinfo ----------
Write-Section "4/5 System Info"
$siOut = & ".\ve_sysinfo.ps1" -OutPath "sysinfo.json" 2>&1
$siOut | Tee-Object -FilePath $logPath -Append

# ---------- 5) Quickcheck ----------
Write-Section "5/5 Quickcheck"
$qcOut = & "$pyExe" ".\ve_quickcheck_stub.py" "--ledger" "ledger.jsonl" "--psi-min" "1.38" 2>&1
$qcOut | Tee-Object -FilePath $logPath -Append
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Quickcheck returned $LASTEXITCODE (see log for details)"
}

Write-Host "`n✅ Full stack run complete."
Log "Full stack complete."
