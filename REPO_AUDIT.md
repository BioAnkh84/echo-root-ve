# Repo Audit

Audit date: 2026-06-13

## Current Top-Level Shape

Core code:

- `echo_root_receipt.py`
- `self_proposal.py`
- `ve_kernel.py`
- `ve_gate_pipeline.py`
- `ve_gate_replay.py`
- `ve_audit_chain.py`
- `ve_deviation_classifier.py`
- `ve_*` support scripts

Release/docs:

- `README.md`
- `QUICKSTART.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `COMMERCIAL_LICENSE_NOTES.md`
- `LICENSE.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `RELEASE_EVIDENCE.md`
- `LICENSE_READINESS_CHECKLIST.md`
- `docs/AUTONOMY_CHARTER.md`
- `docs/DATA_LIKE_AUTONOMY_NOTES.md`
- `docs/`

Evidence/package folders:

- `examples/`
- `receipts/`
- `schemas/`
- `Tests/`
- `archive/`
- `ve_data/`

## Existing Strengths

- Public README already states VE is an execution and audit harness.
- Existing gate/replay tests cover current pairing pipeline behavior.
- Archive paths already preserve stale artifacts with manifests instead of deleting.
- SECURITY.md and CHANGELOG.md already exist.
- Existing doctrine files preserve Echo Root principles and claim boundaries.

## Dead Or Stale Candidates

Needs review before deletion:

- `README_syscheck.txt` and `README_stability.txt`: may be superseded by `QUICKSTART.md` and `ARCHITECTURE.md`.
- `release_notes_v0.1b.txt` and `RELEASE_NOTES.md`: duplicate release-note surfaces.
- Older `ve_*` PowerShell helper scripts: likely still useful for Windows harness operation, but should be classified before archiving.
- `ve_ledger.lock`: zero-byte lock artifact. Candidate for archive or `.gitignore` after confirming no active process relies on it.

## Duplicate Or Overlapping Docs

- `ECHO_ROOT_PROOF_PACKET.md`, `ECHO_ROOT_REVIEWER_QUICKSTART.md`, and `ECHO_ROOT_PUBLIC_PACKET_MANIFEST.md` overlap with release-readiness docs but serve reviewer/demo roles.
- `VE_GATE_PIPELINE.md`, `VE_GATE_REPLAY.md`, and `ARCHITECTURE.md` overlap at different depths.
- `CHANGELOG.md`, `RELEASE_NOTES.md`, and `release_notes_v0.1b.txt` should be normalized before external release.

## Missing Or Newly Added Docs

Added for v0.1.0 release packaging:

- `QUICKSTART.md`
- `ARCHITECTURE.md`
- `COMMERCIAL_LICENSE_NOTES.md`
- `LICENSE.md`
- `ROADMAP.md`
- `docs/COMPLIANCE_ALIGNMENT.md`
- `RELEASE_EVIDENCE.md`
- `LICENSE_READINESS_CHECKLIST.md`
- `docs/AUTONOMY_CHARTER.md`
- `docs/DATA_LIKE_AUTONOMY_NOTES.md`
- `schemas/self_proposal.schema.json`
- `receipts/self_proposal_gate.example.json`

## Broken Imports

No broken imports were identified in the inspected gate/receipt path. Verification should use:

```powershell
py -3.11 -m py_compile .\echo_root_receipt.py .\ve_gate_pipeline.py .\ve_gate_replay.py .\ve_audit_chain.py
py -3.11 -m unittest discover -s Tests
```

## Missing Tests

Added targeted tests for:

- valid `PROCEED`
- `PAUSE` on missing consent
- `PAUSE` on route fallback
- `PAUSE` on empty folder
- `PAUSE` on write budget exceeded
- `ABORT` on destructive action without L3
- `ABORT` on `delta > 0.40`
- `SAFE_MODE`/chain failure posture through broken hash-chain verification
- receipt schema validation
- replay verification
- L1/L2/L3/L4/L5 bounded self-proposal gates
- missing charter, permission request, memory mutation, repeated proposal loop, and calibration-reason coverage

## Deletion Policy

No files were deleted during this pass. Candidate cleanup should be handled by archive manifests first, then explicit L3 approval before removal.

## Release Safety Notes

The safety scan found release-boundary items that should not be treated as blockers for the v0.1 receipt package, but should be handled before publishing a broad source drop:

- Hardcoded local `E:\...` paths remain in older Windows operator scripts.
- Private habitat bridge references remain in optional/local integration scripts.
- `ve_data/` contains generated demo state and should be regenerated for release evidence rather than treated as source truth.
- `archive/` contains stale historical payloads and local-path traces; keep it out of a minimal licensing packet unless separately reviewed.

Use `RELEASE_MANIFEST.md` as the source of truth for the minimal v0.1 licensing packet.
