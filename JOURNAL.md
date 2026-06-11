# Vulpine Echo (VE) — Project Journal
**Project:** Echo Root OS / Vulpine Echo
**Author:** @BioAnkh84
**Started:** October 2025

---

## Standing Orders

```
DELIVERY    Clean zip for each release. No .bak, no artifacts, no logs.
VISION      Keep it small. Precision over breadth. Do not dilute.
LEDGER      Hash-chained JSONL. Every run traceable. No exceptions.
GATE        ρ/γ/Δ decide before execution. Always.
APPROVAL    @BioAnkh84 is sole authority on all releases and decisions.
```

---

## Current State

| Component | Version | Status |
|-----------|---------|--------|
| VE Kernel (PS) | v0.1b | WORKING |
| VE Kernel (Python) | v0.1a | WORKING |
| Gate check (ρ/γ/Δ) | v0.1a | WORKING |
| Ledger chain validator | v0.1a | WORKING |
| Write guard (ve_data/) | v0.1a | WORKING |
| Snapshot system | seq-0004→0021 | WORKING |
| GitHub Actions CI | Windows + Linux | WORKING |
| Policy spec | v1.0 | WORKING |

---

## Architecture

```
Input
  → Echo Gate (ρ ≥ 0.70, γ ≥ 0.70, Δ ≤ 0.30)
  → Redivous: PROCEED / PAUSE / ABORT
  → Bridge (route_hint contract)
  → VE Execution
  → JSONL Ledger (hash-chained, tamper-evident)
```

**Core property:** Decisions happen before execution. The ledger proves it.

---

## Open Items

| Priority | Item | Notes |
|----------|------|-------|
| DONE | Wire run_all.ps1 completely | Calls ve_fullstack.ps1 |
| DONE | Wire ve-pr-check.yml | Runs .github/ve_checks.py |
| MEDIUM | Formal threshold documentation | ρ/γ/Δ values need a spec file |
| DONE | eval() sandbox in ve_kernel.py | AST allowlist applied; see KNOWN_GAPS.md GAP-04 |
| LOW | Key rotation mechanism | See KNOWN_GAPS.md GAP-05 |
| LOW | Document seq-0001 through seq-0003 absence | Intentional? |
| LOW | Formal proof of thresholds | V0.2 work |

---

## Session Log

| # | Date | What |
|---|------|------|
| 1 | [2025-10] | Initial VE build — kernel, ledger, gate, guard |
| 2 | [2025-10] | Snapshot system. Multiple kernel .bak iterations (now archived) |
| 3 | [2025-10] | Artifact test runs (now archived) |
| 4 | [2026-05] | External audit. Structure fixed. WHAT_THIS_IS, KNOWN_GAPS, JOURNAL added. |
| 5 | [2026-05] | Post-audit cleanup. PR check wired, status script repaired, ledger pin guarded, py eval constrained. |
| 6 | [2026-06] | v0.1 license-readiness package added: receipt gate/replay, repo-map/delta receipts, release evidence, safety scan, and CI proof. |

---

## Decisions

| Date | Decision |
|------|----------|
| [2025-10] | Keep tiny — precision over feature breadth |
| [2025-10] | PowerShell-first, Python bridge second |
| [2025-10] | JSONL ledger, hash-chained |
| [2026-05] | .bak files archived, not deleted (history preserved in archive/) |
| [2026-05] | Artifact folders archived, .gitignore updated |
| [2026-05] | CI/runtime truth cleanup after audit findings |
| [2026-06] | Release branches must stay linear when `main` requires linear history; resolve README conflicts by preserving both public positioning and release proof paths, then rebase instead of merging. |

---

## What Was Fixed in Audit [2026-05]

- 26 `.bak` files moved to `archive/` (not deleted — history preserved)
- 3 artifact test run folders moved to `archive/test_runs/`
- `ve_ledger.lock` and run log moved to `archive/runtime/`
- `hello2.txt`, `payload.json`, `payload_diag.json` moved to `egs/`
- `.gitignore` updated to cover `*.lock`
- `WHAT_THIS_IS.md` added
- `KNOWN_GAPS.md` added
- `JOURNAL.md` added (this file)

*@BioAnkh84 — sole authority — updated every session*
