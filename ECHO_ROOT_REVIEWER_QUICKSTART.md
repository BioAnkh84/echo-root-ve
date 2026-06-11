# Echo Root Reviewer Quickstart

## What To Review First

Start here:

1. `ECHO_ROOT_PROOF_PACKET.md`
2. `ECHO_ROOT_MARKET_READINESS.md`
3. `ECHO_ROOT_ONE_DIAGRAM.mmd`
4. `ECHO_ROOT_10_MIN_DEMO_SCRIPT.md`
5. `VE_GATE_PIPELINE.md`
6. `VE_GATE_REPLAY.md`
7. `VE_HABITAT_DOCTRINE.md`

## Run The Tests

```powershell
# from the checked-out repository root
py -3.11 -m unittest discover -s Tests
```

## Inspect The Core Evidence Path

| Surface | File |
| --- | --- |
| Pairing and consent | `ve_pairing_recorder.py` |
| Clarification | `ve_pairing_clarifier.py` |
| Gate context | `ve_pairing_gate_context.py` |
| Signed audit | `ve_audit_chain.py` |
| Unified envelope | `ve_gate_pipeline.py` |
| Replay | `ve_gate_replay.py` |
| Replay report | `ve_replay_report.py` |
| Doctrine memory | `ve_mission_memory.py` |
| Lessons ledger | `ve_lessons_ledger.py` |
| Constitution audit | `ve_habitat_constitution.py` |

## What Good Looks Like

- Sensitive or nuanced intent does not silently proceed.
- Missing clarification is treated as unresolved.
- System self-resolution is not accepted for consent closure.
- Proposal windows fail closed after TTL.
- Audit failure forces `ABORT`.
- Replay verifies the chain and reconstructs decisions.
- Doctrine memory explains mission and constraints without granting authority.

## What Not To Infer

- Do not infer regulatory compliance.
- Do not infer production readiness.
- Do not infer autonomous authority.
- Do not infer that private Echo Nexus / Cipher data is included.

This is a working governance architecture slice, not a certification claim.
