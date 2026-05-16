# RECOMMENDATIONS — Vulpine Echo (VE)
## External Review | May 2026

These are suggestions only. This is your project. Take what fits, leave what doesn't.

---

## IMMEDIATE — Do These Now

### 1. Fix run_all.ps1 ✓ DONE IN THIS AUDIT
Currently only runs `ve_syscheck.ps1`. Either complete the chain:
```powershell
# Suggested chain
.\ve_syscheck.ps1
.\ve_selftest.ps1
.\ve_audit.ps1 -Ledger .\ve_ledger.jsonl
```
Or rename it to `run_syscheck.ps1` to match what it does.
**This was fixed — run_all.ps1 now calls ve_fullstack.ps1.**

### 2. Wire ve-pr-check.yml ✓ DONE AFTER REVIEW
Replace the TODO stub with real checks. Minimum viable:
```yaml
- name: Schema check
  run: python ve_schema_check.py --ledger ve_ledger.jsonl --psi-min 1.38
- name: Quickcheck
  run: python ve_quickcheck.py --ledger ve_ledger.jsonl
```
This was fixed — `ve-pr-check.yml` now runs `.github/ve_checks.py`.

### 3. Document ρ/γ/Δ thresholds formally
The values are in the README but not in a spec file.
A `THRESHOLDS.md` or extension to `policy.ve.psl` would make them authoritative:
```
ρ (rho)   ≥ 0.70  confidence floor
γ (gamma) ≥ 0.70  intent alignment floor
Δ (delta) ≤ 0.30  drift ceiling
ABORT:    Δ > 0.40 OR γ < 0.65
PAUSE:    anything between PROCEED and ABORT
```

---

## MEDIUM — Consider for v0.2

### 4. eval() constraint in ve_kernel.py
The `py:` prefix allows arbitrary Python expressions with a weak sandbox.
If this is intentional for power users, document it clearly.
If it's a convenience that shouldn't be in a governance harness, consider removing it
or replacing with an allowlist of safe operations (math, string ops).
This was mitigated after review — `py:` now uses an AST allowlist for simple expressions and no longer executes statements.

### 5. Formal threshold spec
Right now ρ/γ/Δ = 0.70/0.70/0.30 by design intuition. Before any safety-critical
deployment, these should be documented with the reasoning — why 0.70 and not 0.65?
What failure mode does each threshold protect against?
This doesn't have to be Z3 proofs. A one-page argument is enough for v0.2.

### 6. Tests/ folder is thin
`Tests/VE.Guard.Tests.ps1` is the only test file. The kernel, gate logic,
ledger chain, and manifest verification all lack dedicated test files.
Suggest: one test file per core module, minimum happy path + one failure case each.

---

## ARCHITECTURE OBSERVATION — What You Already Have Is Good

**Keep the tiny philosophy.** The instinct to stay small is correct.
Most projects bloat because they add features before understanding what they have.
You understand what you have. The gate is clean. The ledger is clean. The guard is clean.

**What you have that most projects don't:**
- Hash-chained ledger (tamper-evident by design)
- Write guard that limits blast radius to `ve_data/`
- Snapshot system with manifest verification
- Cross-platform (PS + Python + bash)
- Real CI on both Windows and Linux

**The gap between where you are and production-ready is small:**
The structural issues were surface-level (bak files, artifacts). The core is solid.

---

## IF IT WERE OUR PROJECT

We would add exactly three things and nothing else:

1. A `THRESHOLDS.md` specifying ρ/γ/Δ with reasoning
2. `Tests/` coverage for gate logic and ledger chain
3. Wire run_all.ps1 to actually run all

Everything else can wait for v1.0.

The system's identity — governed execution, tamper-evident ledger, tiny surface area —
is already defined and working. Additions should extend that identity, not dilute it.

---

*This review was conducted with respect for your vision.*
*The project stays yours. These are observations, not directives.*

---

## ADDITIONAL FINDINGS

### Fix ve_status.ps1 hardcoded path
```powershell
# Replace:
Set-Location C:\VE_Test_Suite_v0.1a

# With:
Set-Location $PSScriptRoot
```
This makes the script portable to any machine.
This was fixed after review.

### Guard ve_ledger_pin.ps1 against overwriting existing ledger
```powershell
if ((Test-Path $LedgerPath) -and (Get-Item $LedgerPath).Length -gt 0) {
    Write-Error "Ledger already exists and is non-empty. Aborting."
    exit 1
}
```
One line prevents accidental history destruction.
This was fixed after review; `-Force` is now required to intentionally overwrite a non-empty ledger.
