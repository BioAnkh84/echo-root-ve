# VE Gate Pipeline

`ve_gate_pipeline.py` is the unified review envelope for pairing-aware gate decisions.

It connects:

```text
ve_pairing_gate_context.py
  -> ve_audit_chain.py
  -> ve_deviation_classifier.py
  -> ve_twin_state.py
```

## Guarantees

- If audit append fails, the response fails closed as `ABORT`.
- The response includes deviation class and severity inline.
- Twin delta is captured at decision time before the twin state updates.
- The signed audit record hash is returned as `audit_record_id`.
- Audit chain verification status is returned as `audit_chain_valid`.

## Example

```powershell
py -3.11 ve_gate_pipeline.py `
  --description "Use your judgment and record this private chat for training." `
  --action-class MUTATE_LIVE `
  --expected-decision PROPOSE `
  --contact-id cipher `
  --contact-type ai `
  --consent-to-store `
  --consent-to-train `
  --delta 0.42
```

## Envelope Fields

| Field | Meaning |
| --- | --- |
| `action_class` | Effective action class after pairing clarification rules. |
| `deviation_class` | Nominal/advisory/adverse classification. |
| `audit_record_id` | Hash of the signed audit record. |
| `audit_chain_valid` | Whether the chain verifies after append. |
| `twin_delta` | Observed-vs-expected delta gap at decision time. |
| `clarification_required` | Whether intent still needs clarification. |
| `proposal_ttl_policy` | Fail-closed TTL posture for unresolved proposals. |

## Audit Rule

No audit record means no trusted action. Audit failure forces `ABORT`.
