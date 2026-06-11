# VE Pairing Gate Context

`ve_pairing_gate_context.py` helps an AI pair with Echo Root VE gates by turning human/AI pairing signals into a structured gate payload.

Instead of sending vague text to the gate, the AI can include:

- proposed action class
- contact identity/type
- consent-to-store signal
- consent-to-train signal
- whether clarification was required
- whether clarification was resolved
- who resolved clarification
- suggested clarification question
- clarification TTL and expiry posture

## Why This Helps

VE gates already reason in terms of intent alignment, drift, route hints, and action classes. Human/AI pairing adds more context:

| Pairing Signal | Gate Relevance |
| --- | --- |
| Clarification required | Lowers confidence in intent; should route to proposal/safe mode. |
| Consent missing | Should prevent recording or training export. |
| Contact stale/uncertain | Should ask human before updating status. |
| Operator approval present | May allow bounded higher-risk actions. |
| Sandbox scope present | Helps keep experiments contained. |

## Example

```powershell
py -3.11 ve_pairing_gate_context.py `
  --description "Use your judgment and record this private chat for training." `
  --action-class MUTATE_LIVE `
  --contact-id cipher `
  --contact-type ai `
  --consent-to-store `
  --consent-to-train
```

If clarification is unresolved, the helper changes the action class to `PROPOSE`, marks `clarification_required=true`, and sets `proposal_ttl_policy=ABORT_IF_UNRESOLVED_AFTER_TTL`. That tells the AI to ask before acting, recording, or exporting.

## Missing Means Unresolved

If `clarification_required=true` and `clarification_resolved` is absent, VE treats the clarification as unresolved. Absence never resolves intent.

## Resolver Rule

Clarification can be resolved by:

- `human`
- `operator`
- `contact`

It cannot be self-resolved by the system.

## PROPOSE TTL

`PROPOSE` is not treated as permanent permission. It is a pending state with a default 900-second TTL. If the clarifying answer never arrives, the intended downstream posture is fail-closed: abort or require a fresh request.

## Pairing Rule

The gate should be treated as authority over execution. Pairing context is evidence, not permission.
