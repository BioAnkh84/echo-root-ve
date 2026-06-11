# Echo Root Public Packet Manifest

Generated for repo cleanup and reviewer orientation.

## Purpose

This manifest groups the current public Echo Root additions so untracked files are understandable before they are committed, packaged, or reviewed.

It is a map, not authority. Use tests and replay commands for proof.

## Timestamp Groups

| Group | Timestamp window | Meaning |
| --- | --- | --- |
| Pairing and contacts | 2026-06-05 00:37-01:05 UTC | Consent-first pairing, clarification, gate context, recorder, and contact registry |
| Medical-grade-inspired controls | 2026-06-05 01:11-01:25 UTC | Audit chain, deviation classifier, twin state, gate pipeline, and tests |
| Replay and reports | 2026-06-05 01:29-05:29 UTC | Signed replay, classifier drift check, operator-readable replay report |
| Doctrine memory | 2026-06-05 05:35-05:46 UTC | Mission memory, lessons ledger, constitution audit, seed data |
| Public proof packet | 2026-06-05 07:02 UTC | One diagram, proof packet, reviewer quickstart, demo script |
| Demo evidence | 2026-06-07 01:37-01:38 UTC | Sample signed gate pipeline audit, twin state, replay reports |
| Market readiness | 2026-06-08 03:15-03:30 UTC | Public positioning, claim boundaries, demo-readiness checklist |
| VSA doctrine correction | 2026-06-08 18:36 UTC | Reframes VSA as baseline deviation detection with metadata, environment ladder, and no diagnosis/authority claims |

## Public Orientation Docs

- `README.md`
- `WHAT_THIS_IS.md`
- `ECHO_ROOT_PROOF_PACKET.md`
- `ECHO_ROOT_MARKET_READINESS.md`
- `ECHO_ROOT_PUBLIC_PACKET_MANIFEST.md`
- `ECHO_ROOT_ONE_DIAGRAM.mmd`
- `ECHO_ROOT_10_MIN_DEMO_SCRIPT.md`
- `ECHO_ROOT_REVIEWER_QUICKSTART.md`
- `KNOWN_GAPS.md`

## Core Evidence Code

- `ve_pairing_clarifier.py`
- `ve_pairing_recorder.py`
- `ve_pairing_gate_context.py`
- `ve_contact_registry.py`
- `ve_audit_chain.py`
- `ve_deviation_classifier.py`
- `ve_twin_state.py`
- `ve_gate_pipeline.py`
- `ve_gate_replay.py`
- `ve_replay_report.py`
- `ve_mission_memory.py`
- `ve_lessons_ledger.py`
- `ve_habitat_constitution.py`

## Supporting Docs

- `VE_PAIRING_CLARIFICATION_PROTOCOL.md`
- `VE_PAIRING_RECORDER.md`
- `VE_PAIRING_GATE_CONTEXT.md`
- `VE_CONTACT_REGISTRY.md`
- `VE_MEDICAL_GRADE_SPEC.md`
- `VE_GATE_PIPELINE.md`
- `VE_GATE_REPLAY.md`
- `VE_REPLAY_REPORT.md`
- `VE_HABITAT_DOCTRINE.md`
- `VE_VSA_BASELINE_DEVIATION_DOCTRINE.md`

## Tests

- `Tests/test_ve_pairing_clarifier.py`
- `Tests/test_ve_pairing_recorder.py`
- `Tests/test_ve_pairing_gate_context.py`
- `Tests/test_ve_contact_registry.py`
- `Tests/test_ve_medical_grade_controls.py`
- `Tests/test_ve_gate_pipeline.py`
- `Tests/test_ve_gate_replay.py`
- `Tests/test_ve_replay_report.py`
- `Tests/test_ve_habitat_doctrine.py`

## Demo Evidence Artifacts

- `ve_data/gate_pipeline_audit.jsonl`
- `ve_data/gate_replay_report.html`
- `ve_data/gate_replay_report.md`
- `ve_data/habitat_lessons.jsonl`
- `ve_data/mission_memory.json`
- `ve_data/twin_state.json`

## Cleanup Notes

- Cleanup archive: `archive/public_cleanup_20260608/ARCHIVE_MANIFEST.md`
  - Reason: moved legacy backup files, old generated artifact reports, and scratch payloads out of active public paths while preserving reference history.
- Python cache folders are generated noise and should stay ignored:
  - `__pycache__/`
  - `Tests/__pycache__/`
- Public docs should use generic demo identities.
- Private Echo Nexus / Cipher habitat data should stay outside this repo.
- Claims should stay bounded: medical-grade-inspired, not FDA compliant; replayable evidence, not guaranteed safety.
- VSA claims should say baseline deviation detection, not stress detection, emotion detection, diagnosis, truth, or voice lie detection.
- Archive status for VSA doctrine correction: no old standalone VSA doctrine file existed in this public repo, so nothing was moved to `archive/`. This manifest records the reason.

## Suggested Tracking Set

If preparing a public commit, track the docs, code, tests, and demo evidence above as one coherent public packet.

Keep generated cache, local virtual environments, logs, secrets, and private habitat files out of the commit.
