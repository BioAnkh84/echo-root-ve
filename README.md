# Vulpine Echo — VE Test Suite v0.1a

Lightweight sanity suite to validate the **telemetry ↔ trust ↔ ledger** loop on Windows.
Created: 2025-10-28 08:51 

## Contents
- `ve_handshake.ps1` — PowerShell→Python handshake (JSON echo with SHA-256)
- `ve_handshake.py` — Python side of the handshake
- `ve_gatecheck.py` — Quick ρ/γ/Δ gate simulation (PROCEED/PAUSE/ABORT)
- `ve_ledger_append.ps1` — Append entries to a hash-chained JSONL ledger (auto-GENESIS)
- `ve_quickcheck_stub.py` — Minimal ledger checker (hash continuity + ψ floor heuristic)

## Prereqs
- Windows PowerShell 5.1+ or PowerShell 7+
- Python 3.8+ on PATH (use `python` or adjust to `py` / `python3`)

## Quick Start

### 1) Handshake
```powershell
cd "/mnt/data/VE_Test_Suite_v0.1a"
.e_handshake.ps1
# or customize
.e_handshake.ps1 -Id "spike-001" -rho 0.84 -gamma 0.78 -delta 0.22
```

### 2) Gate simulation
```powershell
python ve_gatecheck.py
```

### 3) Ledger append
```powershell
# First run creates a GENESIS record
.e_ledger_append.ps1
# Run multiple times to grow the chain
.e_ledger_append.ps1 -rho 0.90 -gamma 0.71 -delta 0.28
```

### 4) Quickcheck
```powershell
python ve_quickcheck_stub.py --ledger ledger.jsonl --psi-min 1.38
```

## Notes
- `ve_ledger_append.ps1` uses .NET SHA256 (no external tools) and keeps each record as **one JSON line**.
- The stub ψ check uses `ψ_eff ≈ rho + gamma` **only** as a placeholder until your full `ve_quickcheck.py` is in place.
- All scripts are local and write to the working directory by default.
