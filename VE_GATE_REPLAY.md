# VE Gate Replay

`ve_gate_replay.py` provides forensic replay for gate pipeline audit records.

It reads the signed audit chain, verifies the chain, reclassifies each gate decision, and emits a session summary.

## Why Replay Matters

Auditability is stronger when a reviewer can reconstruct what happened after the fact without trusting live state.

Replay answers:

- Was the audit chain valid?
- How many gate decisions were replayed?
- Which decisions were advisory?
- Which decisions were adverse events?
- What was the largest twin delta observed?
- Did replay classification match the original envelope?
- Did updated classifier logic change the interpretation of older records?
- How did risk distribute across sessions/pairings?

## Run

```powershell
py -3.11 ve_gate_replay.py --ledger ve_data/gate_pipeline_audit.jsonl
```

## Forensic Rule

If the chain is tampered with, replay returns `audit_chain_valid=false` and exits non-zero from the CLI.

Replay does not grant permission and does not execute actions. It reconstructs evidence.

## Multi-Session Replay

Replay groups records by `pairing_id` and reports per-session:

- record count
- advisory events
- adverse events
- max twin delta
- classifier changes

## Replay Diff

`classifier_changes` counts records where the original envelope's `deviation_class` differs from the replayed classification. This supports retrospective safety analysis when classifier logic improves over time.
