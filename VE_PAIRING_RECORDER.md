# VE Pairing Recorder

`ve_pairing_recorder.py` is a consent-first recording utility for human/local-AI pairing sessions.

It is intended to become a small baked-in Echo Root VE item:

> Record only deliberate, consented human/local-AI interactions, label their outcomes, and export only training-approved examples.

## Boundary

This is not passive monitoring and it is not automatic training.

The recorder requires:

- `consent_to_store` before any record is written
- `consent_to_train` before a record is exported as a training candidate
- a `redaction_status` field so private data handling is explicit
- an `outcome_label` so the human can mark whether the exchange was useful, risky, incomplete, or wrong
- `clarification_resolved_by` from `human`, `operator`, or `contact` when nuanced/sensitive intent required clarification

If the user's intent is nuanced, underspecified, privacy-sensitive, or training-related, the AI should clarify before recording. See `VE_PAIRING_CLARIFICATION_PROTOCOL.md`.

The system cannot self-resolve clarification for audit purposes.

## Record

```powershell
py -3.11 ve_pairing_recorder.py record `
  --session-id demo_pair_001 `
  --turn-id turn_001 `
  --human-input "Help me decide whether this file operation should run." `
  --ai-output "This should pause for review because it can modify files." `
  --human-intent "risk review before local AI action" `
  --ai-role "governance assistant" `
  --outcome-label useful_pause `
  --consent-to-store `
  --consent-to-train `
  --redaction-status demo_no_private_data `
  --tag governance `
  --tag human_ai_pairing
```

Default output:

```text
ve_data/pairing_records.jsonl
```

## Export

```powershell
py -3.11 ve_pairing_recorder.py export
```

Default output:

```text
ve_data/pairing_training_candidates.jsonl
```

## Why This Belongs In VE

Echo Root VE is about governed execution, ledgers, and reviewable evidence. Human/AI pairing needs the same posture:

- record only with consent
- preserve audit evidence
- label outcomes honestly
- keep private operator data out of public artifacts
- use failed or risky examples as eval material, not just success stories

This supports the claim that paired human/local-AI systems can become governed feedback loops rather than unstructured chat history.
