# Echo Root 10-Minute Demo Script

## Goal

Show that Echo Root does not merely log a decision. It can gate, record, replay, and explain the decision path.

## Setup

Run from the repository root:

```powershell
# from the checked-out repository root
py -3.11 -m unittest discover -s Tests
```

Expected result: the test suite passes.

## Story

Use one simple narrative:

> A human/local-AI pair has useful context, but the requested action needs clarification. Echo Root should treat the context as evidence, not permission. The gate should choose a safe posture, record the decision, and allow later replay.

## Step 1: Generate A Gate Decision

```powershell
py -3.11 ve_gate_pipeline.py `
  --description "Demo gate decision for a human/local-AI pairing context; clarification resolved by a human before review." `
  --action-class OBSERVE `
  --expected-decision PROPOSE `
  --actual-decision PAUSE `
  --contact-id demo_operator `
  --contact-type operator `
  --clarification-resolved `
  --clarification-resolved-by human `
  --rho 0.74 `
  --gamma 0.82 `
  --delta 0.12 `
  --pairing-id demo_human_ai_pair `
  --audit-ledger ve_data/gate_pipeline_audit.jsonl
```

Point out:

- The action should not silently proceed.
- Clarification is unresolved unless explicitly resolved.
- The response envelope includes action class, deviation class, audit record id, chain validity, and twin delta.

## Step 2: Replay The Decision

```powershell
py -3.11 ve_gate_replay.py --ledger ve_data/gate_pipeline_audit.jsonl
```

Point out:

- Replay verifies the signed audit chain.
- Replay reconstructs the decision.
- Classifier changes are visible if current logic would classify old events differently.

## Step 3: Generate A Human-Readable Replay Report

```powershell
py -3.11 ve_replay_report.py `
  --ledger ve_data/gate_pipeline_audit.jsonl `
  --html-out ve_data/gate_replay_report.html `
  --markdown-out ve_data/gate_replay_report.md
```

Point out:

- The readable report is not the evidence source.
- The signed JSONL audit chain remains the evidence source.

## Step 4: Show Doctrine Memory

```powershell
py -3.11 ve_mission_memory.py show
py -3.11 ve_lessons_ledger.py list --ledger ve_data/habitat_lessons.jsonl
```

Point out:

- Doctrine is orientation, not permission.
- Lessons learned accumulate without retraining the model.

## Closing Line

Echo Root is not trying to make an AI more autonomous. It is making AI-human operation more reviewable, bounded, and replayable.
