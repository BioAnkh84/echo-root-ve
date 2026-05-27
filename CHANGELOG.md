# Changelog — Vulpine Echo (VE)

## Public Profile Alignment — May 2026

### Updated
- Reworked `README.md` into a public-facing project overview matching the Team PURP lab standard.
- Reworked `WHAT_THIS_IS.md` to describe the public execution harness shape without exposing private habitat details.
- Clarified `KNOWN_GAPS.md` around validation limits and private habitat scope.
- Expanded `SECURITY.md` with guidance against submitting private ledgers, memories, credentials, operator data, or unreleased internal details.

## Codex Post-Audit Cleanup — May 2026

### Fixed
- `.github/ve_checks.py` now references `ve_quickcheck.py` instead of missing `ve_quickcheck_stub.py`.
- `.github/ve_checks.py` no longer runs a raw git check at module import time.
- `.github/workflows/ve-pr-check.yml` now runs the VE PR check harness instead of a TODO stub.
- `ve_fullstack.ps1` now uses `ve_quickcheck.py` instead of generating/running `ve_quickcheck_stub.py`.
- `ve_status.ps1` now uses `$PSScriptRoot` by default and no longer contains pasted hash/json fragments as invalid PowerShell.
- `ve_ledger_pin.ps1` now refuses to overwrite a non-empty ledger unless `-Force` is explicitly supplied.
- `ve_kernel.py` replaced raw `eval()`/`exec()` behavior with an AST allowlist for simple `py:` expressions.

### Updated
- `KNOWN_GAPS.md` and `JOURNAL.md` were brought into alignment with the repaired state.

## External Audit Session — May 2026

### Fixed
- `run_all.ps1` — now properly calls `ve_fullstack.ps1` (the complete pipeline)
  Previously only called `ve_syscheck.ps1`. Added `--Quick` flag for dev loop.

### Added
- `WHAT_THIS_IS.md` — one-page orientation for any new reader
- `KNOWN_GAPS.md` — public honest gap register (9 items documented)
- `JOURNAL.md` — project journal with standing orders and session log
- `RECOMMENDATIONS/RECOMMENDATIONS.md` — prioritised suggestions, respecting your vision
- `RECOMMENDATIONS/PHILOSOPHY_THEORY_METAPHOR_POETRY.md` — theory, metaphor, poetry
- `.gitignore` — added `*.lock` coverage (was missing)
- `archive/` — new folder for development artifacts (nothing deleted, just organised)
  - `archive/test_runs/` — three artifact test run folders moved here
  - `archive/runtime/` — `ve_ledger.lock` and run log moved here
- `egs/` — `hello2.txt`, `payload.json`, `payload_diag.json` moved here (were at root)

### Nothing removed
All original files are present. Development history is preserved in `archive/`.

### New gaps documented (not yet fixed — owner decides)
- GAP-08: `ve_status.ps1` has hardcoded `C:\VE_Test_Suite_v0.1a` path
- GAP-09: `ve_ledger_pin.ps1` overwrites ledger — no guard against existing data

---

## v0.1b — October 2025

- PS 5.1-safe kernel iterations
- Snapshot system (seq-0004 through seq-0021)
- Artifact test runs
- Multiple kernel refinements (now archived as `archive/`)

## v0.1a — October 2025

- Initial VE build
- PS 5.1-safe kernel entrypoint
- Clean child exec + quiet audit
- Minimal scaffolding for receipts
