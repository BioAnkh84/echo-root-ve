# WHAT THIS IS
## Vulpine Echo (VE) — Echo Root OS Execution Harness

**One sentence:** VE is the execution and audit layer that sits beneath Echo Root's governance.

---

## The System

```
Input
  → Echo Gate (ρ/γ/Δ scoring)     — should I proceed?
  → Redivous (decision)           — PROCEED / PAUSE / ABORT
  → Bridge (route_hint contract)  — where does this go?
  → VE Execution                  — do the work
  → Ledger (JSONL, hash-chained)  — prove it happened
```

**Gate thresholds:**
- ρ ≥ 0.70 — confidence
- γ ≥ 0.70 — intent alignment
- Δ ≤ 0.30 — drift tolerance

**Key property:** The ledger is tamper-evident. Every run is traceable. You cannot quietly undo what happened.

---

## Key Files

| File | Role |
|------|------|
| `ve_kernel.ps1` | Core entrypoint |
| `ve_kernel.py` | Python bridge |
| `ve_gatecheck.py` | Gate logic (ρ/γ/Δ) |
| `ve_schema_check.py` | Ledger chain validator |
| `ve_quickcheck.py` | Integrity checker |
| `ve_manifest_verify.py` | File manifest verification |
| `ve_guard.ps1` | Write guard (ve_data/ only) |
| `policy.ve.psl` | Policy spec |
| `Modules/VE.Guard/` | PowerShell module |
| `.ve_snapshots/` | Snapshot sequence |

---

## Contact
GitHub: @BioAnkh84
