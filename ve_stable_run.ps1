# ve_stable_run.ps1
# Hardened runner: file-based handshake + atomic ledger + schema check

param(
    [string]$Ledger = "ledger.jsonl",
    [double]$rho = 0.90,
    [double]$gamma = 0.80,
    [double]$delta = 0.25,
    [double]$psiMin = 1.38,
    [string]$actor = "VE",
    [string]$etype = "RUN",
    [string]$consent = ""
)

. "$PSScriptRoot\ve_atomic_io.ps1"

function Resolve-Python {
    $p = Get-Command python -ErrorAction SilentlyContinue
    if ($p) { return $p.Source }
    $p = Get-Command py -ErrorAction SilentlyContinue
    if ($p) { return $p.Source }
    throw "Python not found"
}

$pyExe = Resolve-Python
Write-Host "Python at: $pyExe"

# Create payload.json
$payload = @{ id="stable"; rho=$rho; gamma=$gamma; delta=$delta } | ConvertTo-Json -Compress
[System.IO.File]::WriteAllText(".\payload.json",$payload,[System.Text.UTF8Encoding]::new($false))

# Ensure handshake helper exists
if (-not (Test-Path ".\ve_handshake_file.py")) {
@'
import json, argparse, hashlib, time, sys
p = argparse.ArgumentParser()
p.add_argument("--file", required=True)
args = p.parse_args()
raw = open(args.file, "r", encoding="utf-8").read()
print("RAW_PAYLOAD:", raw)
data = json.loads(raw)
data["timestamp"] = time.time()
data["hash_self"] = hashlib.sha256(raw.encode()).hexdigest()
print(json.dumps(data, indent=2, sort_keys=True))
'@ | Set-Content ".\ve_handshake_file.py" -Encoding utf8
}

# Handshake
& "$pyExe" ".\ve_handshake_file.py" "--file" ".\payload.json"
if ($LASTEXITCODE -ne 0) { throw "Handshake failed" }

# Append ledger atomically with mutex and metadata
& ".\ve_ledger_append_atomic.ps1" -LedgerPath $Ledger -rho $rho -gamma $gamma -delta $delta -actor $actor -etype $etype -consent $consent
if ($LASTEXITCODE -ne 0) { throw "Ledger append failed" }

# Schema + chain check
& "$pyExe" ".\ve_schema_check.py" "--ledger" $Ledger "--psi-min" "$psiMin"
if ($LASTEXITCODE -ne 0) { Write-Warning "Schema check emitted warnings/errors." } else { Write-Host "[OK] Stability checks passed." }

