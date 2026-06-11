# Release Manifest

Target: v0.1.0 license-ready MVP

This manifest defines the minimal packet for licensing review. It is narrower than the full working tree.

## Include

Core runtime:

- `echo_root_receipt.py`
- `repo_map.py`
- `schemas/echo_root_receipt.schema.json`
- `examples/sample_intercept_action.json`
- `receipts/.gitkeep`

Tests:

- `Tests/test_echo_root_receipt.py`
- Existing `Tests/test_*.py` files that validate the current VE gate/replay surfaces

Primary docs:

- `README.md`
- `QUICKSTART.md`
- `ARCHITECTURE.md`
- `RELEASE_EVIDENCE.md`
- `LICENSE_READINESS_CHECKLIST.md`
- `RELEASE_MANIFEST.md`
- `PUBLIC_RELEASE_SAFETY_SCAN.md`
- `SECURITY.md`
- `COMMERCIAL_LICENSE_NOTES.md`
- `ROADMAP.md`
- `CHANGELOG.md`
- `docs/COMPLIANCE_ALIGNMENT.md`
- `docs/REPO_MAP_RECEIPTS.md`

Reviewer/demo docs:

- `ECHO_ROOT_PROOF_PACKET.md`
- `ECHO_ROOT_MARKET_READINESS.md`
- `ECHO_ROOT_REVIEWER_QUICKSTART.md`
- `ECHO_ROOT_10_MIN_DEMO_SCRIPT.md`
- `ECHO_ROOT_PUBLIC_PACKET_MANIFEST.md`

CI:

- `.github/ve_checks.py`
- `.github/workflows/ve-pr-check.yml`

## Exclude From Minimal Licensing Packet Unless Separately Reviewed

- `archive/`
- generated `ve_data/` records
- generated `receipts/*.jsonl`
- generated `receipts/repo_map_*.json`
- `.ve_logs/`
- `.ve_snapshots/`
- `.venv/`
- local operator scripts with hardcoded machine paths
- private habitat/Cipher bridge integrations

## Boundary

The minimal packet demonstrates:

```text
install/check environment
run demo
intercept action
gate decision
append receipt
verify hash chain
replay decision
run tests
```

It does not claim certification, regulatory approval, production readiness, or guaranteed compliance.
