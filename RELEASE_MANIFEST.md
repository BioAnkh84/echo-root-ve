# Release Manifest

Target: v0.1.0 license-ready MVP

This manifest defines the minimal packet for licensing review. It is narrower than the full working tree.

## Include

Core runtime:

- `echo_root_receipt.py`
- `self_proposal.py`
- `spatial_governance.py`
- `repo_map.py`
- `ve_scheduled_health.ps1`
- `schemas/echo_root_receipt.schema.json`
- `schemas/self_proposal.schema.json`
- `schemas/spatial_governance.schema.json`
- `examples/sample_intercept_action.json`
- `examples/self_proposal_l1_suggest.json`
- `examples/self_proposal_l2_prepare_patch.json`
- `examples/self_proposal_l3_read_only_audit.json`
- `examples/self_proposal_l5_supervised_research_episode.json`
- `examples/spatial_envelope_search_zone.json`
- `examples/spatial_event_authorized.json`
- `receipts/.gitkeep`
- `receipts/self_proposal_gate.example.json`
- `receipts/spatial_governance_gate.example.json`

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
- `docs/AUTONOMY_CHARTER.md`
- `docs/DATA_LIKE_AUTONOMY_NOTES.md`
- `docs/SCHEDULED_HEALTH_CHECKS.md`
- `docs/SPATIAL_GOVERNANCE_LAYER.md`
- `docs/EXTERNAL_AI_AUTHORITY_BOUNDARY.md`
- `docs/VSA_TUNING_ROUND_1.md`

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
classify bounded self-proposal
evaluate spatial operational envelope posture
gate decision
append receipt
verify hash chain
replay decision
run tests
run optional scheduled health evidence check
```

It does not claim certification, regulatory approval, production readiness, or guaranteed compliance.
