# External AI Authority Boundary

Local AI is a governed participant inside the habitat.

Everything else is an external advisory or transport lane unless it has been
explicitly onboarded, scoped, gated, and receipted.

## Doctrine

- External AI outputs are advisory evidence by default.
- External routing does not imply trust.
- External success does not create internal authority.
- External AI must pass local gates before affecting action.
- Local Cipher and Echo Root remain the governed local authority boundary.
- Capability does not equal authority.
- Output does not equal permission.
- Provider reachability does not equal readiness.
- Route fallback does not equal consent.

## Local Participant

A local governed participant is inside the habitat authority model. It can be
reviewed through local doctrine, receipts, operator scope, and habitat state.

For Echo Nexus work, Local Cipher is the local participant for continuity,
environment awareness, local synthesis, and bounded drafting.

Local participation still does not grant unlimited authority. It means the
participant is governed by local gates instead of treated as an unreviewed
external source.

## External Advisory Lane

An external AI lane may help with:

- synthesis
- critique
- brainstorming
- comparison
- external knowledge checks
- draft language
- alternative reasoning

It may not directly:

- approve actions
- mutate memory
- grant tool authority
- change thresholds
- bypass Echo Root gates
- convert a route success into trust
- make release, legal, safety, or compliance claims without local review

## Required Receipt Fields

External advisory receipts should preserve enough context to review later:

- `provider_id`
- `model_id`
- `route_id`
- `route_class`
- `request_purpose`
- `input_hash`
- `output_hash`
- `operator_scope`
- `local_review_required`
- `decision`
- `decision_reason`
- `fallback_status`

Prefer hashes and summaries over raw external payload dumps when the payload may
include private context.

## Gate Rule

External output can raise or lower confidence as evidence. It cannot decide.

```text
external output
  -> local synthesis
  -> Echo Root gate
  -> receipt
  -> operator/local authority review
  -> action, pause, abort, or safe mode
```

## Short Form

```text
Local Cipher = governed participant.
External AI = advisory evidence.
External route success = not trust.
Local gate = authority boundary.
No receipt = no trusted operation.
```
