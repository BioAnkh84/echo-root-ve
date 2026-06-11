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
| [2026-06] | Codex integration should start as receipt-backed observation: repo-local hooks can orient, gate, and log, but hook presence is not authority and hook receipts do not replace human approval. |
| [2026-06] | Codex scoring baseline should be explicit and tunable from lessons learned: raise rho through evidence, raise delta through authority change or drift, and let human correction recalibrate future trust. |
| [2026-06] | Calibration reasons belong beside scores in hook receipts so future reviews can see why rho/delta were chosen without changing the public receipt schema. |
| [2026-06] | Echo Root helps Codex most when its impact is testable: lifecycle receipts should prove orientation, PAUSE on authority change, ABORT on destructive posture, and calibration reason coverage. |
| [2026-06] | Score tuning should name difference makers explicitly: evidence makers raise rho, risk makers raise delta, and feedback makers update future calibration instead of being hand-waved. |
| [2026-06] | AI-facing docs should be operational packets, not essays: tell the next model what to read, what to run, what changes rho/delta, and when to pause. |
| [2026-06] | Hook payload handling should be shape-tolerant and privacy-aware: extract useful command/tool hints, store shape hashes, and avoid raw payload dumps. |
| [2026-06] | Live hook activation needs its own probe: simulated hook logic can pass while the current Codex session has not loaded or trusted repo-local hooks. |
| [2026-06] | If lifecycle hooks do not fire in a Codex surface, expose Echo Root as MCP tools so AI can call orientation, gate, receipt, verify, and probe functions directly. |
| [2026-06] | Project MCP loading is a separate proof step: built-in Codex tools can appear while repo-local `.codex/config.toml` has not loaded or been trusted yet. |
| [2026-06] | If repo/global MCP config remains visible-but-not-callable, package Echo Root VE as a personal Codex plugin with a skill and bundled MCP server config. |
| [2026-06] | Installed/configured MCP is still not callable proof: Codex Desktop/CLI `0.140.0-alpha.2` launched Echo Root's stdio server but closed stdin before `initialize`, so fallback commands remain the trusted path until live tools appear. |

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
