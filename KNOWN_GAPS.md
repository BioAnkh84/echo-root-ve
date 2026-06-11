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

## VALIDATION

### GAP-06: Public gate thresholds are not formally verified
**Status:** OPEN
The public gate values are chosen by design intuition and test behavior.
There is no formal proof that the public thresholds are sufficient for safety-critical deployment.
This is acceptable for the current prototype, but the repo should continue to state this clearly.

### GAP-06B: Private habitat details are intentionally out of scope
**Status:** INFO
Echo Nexus / Cipher habitat data, private memories, internal scoring details, credentials,
operator records, and private ledgers are not part of this public repo.
This keeps the repo useful as a public harness without turning it into an internal operating manual.

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

### GAP-10: VSA baseline deviation validation is not built
**Status:** OPEN
The VSA doctrine has been reframed as baseline deviation detection, not stress detection,
emotion detection, diagnosis, truth detection, or voice lie detection.
The repo does not yet include validated personal-baseline datasets, environment-ladder
recordings, signal degradation curves, or repeatability metrics.
Before collecting larger VSA datasets, use `VE_VSA_BASELINE_DEVIATION_DOCTRINE.md`
for consent, metadata, environment staging, and claim boundaries.
