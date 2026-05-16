# KNOWN GAPS — Vulpine Echo (VE)
## v0.1b | May 2026

Honest list of what is open. Nothing hidden.

---

## STRUCTURAL

### GAP-01: run_all.ps1 is incomplete
**Status:** FIXED in this audit
The file comment says it chains the full pipeline. It only runs `ve_syscheck.ps1`.
Either complete the chain or rename the file to match what it actually does.

### GAP-02: ve-pr-check.yml is a stub
**Status:** FIXED after review
```yaml
echo "TODO: wire in extra checks (docs, schema, etc.)."
```
PR check workflow now runs `.github/ve_checks.py`.

### GAP-03: Genesis sequence gap
**Status:** INFO
`.ve_snapshots/` starts at seq-0004. seq-0001 through seq-0003 are absent.
May be intentional (deleted early experiments). Worth documenting if so.

---

## SECURITY

### GAP-04: ve_kernel.py eval() with weak sandbox
**Status:** MITIGATED after review
`do_exec("py: ...")` calls `eval()` with `__builtins__: {}`.
This sandbox is bypassable via attribute access chains.
For a governance harness, execution of arbitrary Python expressions is worth constraining further.
**Mitigation applied:** `py:` now parses expressions with `ast` and allows only literal/arithmetic/string-format expression nodes. Statement execution was removed.

### GAP-05: Shared key in secrets/ is not rotated by default
**Status:** INFO
`ve_shared.key` is generated once. No rotation mechanism exists.
For production use with multiple operators, key rotation should be defined.

---

## FORMAL PROOF

### GAP-06: ρ/γ/Δ thresholds are not formally verified
**Status:** OPEN
The values (0.70 / 0.70 / 0.30) are chosen by design intuition.
No formal proof that these thresholds are sufficient for the stated safety properties.
This is acceptable for v0.1. Should be addressed before any safety-critical deployment.

---

## ENVIRONMENT

### GAP-07: PowerShell 5.1 vs 7.x compatibility
**Status:** PARTIAL
README says PS 5.1-safe. Some modules use features that behave differently in PS 7.
CI runs on windows-latest (PS 7). Local dev may differ.

---

*Nothing is hidden. Everything is timestamped.*
*@BioAnkh84 — last updated May 2026*

### GAP-08: ve_status.ps1 has hardcoded path
**Status:** FIXED after review
`ve_status.ps1` sets `Set-Location C:\VE_Test_Suite_v0.1a` — a hardcoded absolute path
that will fail on any machine where the project lives elsewhere.
→ Replace with `$PSScriptRoot` to make it portable.

### GAP-09: ve_ledger_pin.ps1 overwrites the ledger
**Status:** FIXED after review
`ve_ledger_pin.ps1` uses `Set-Content` which **overwrites** the entire ledger with a genesis entry.
This destroys existing audit history.
Only use this to initialize a fresh ledger, never on an existing one.
→ Add a guard: fail if ledger already exists and is non-empty.
