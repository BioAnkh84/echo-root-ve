# Bounded Initiative Notes

This document describes the autonomy concept in implementation-neutral terms.
It avoids character or franchise labels for runtime modes.

## Research Officer Profile

The research officer profile may inspect context, name uncertainty, and prepare
candidate next steps. It does not execute tools or mutate memory unless a
charter grants that lane and a receipt path is available.

## Curiosity Profile

The curiosity profile may ask useful questions and propose investigations. Its
output remains advisory until Echo Root gates the proposal.

## Bounded Initiative Mode

Bounded initiative means the agent may start a proposal without waiting for a
direct human prompt. It does not mean the agent may act without review.

The minimum loop is:

```text
observe context
create self_proposal
classify lane/scope/risk/authority
gate against charter and policy
write receipt
stop or request review
```

## Self-Proposal Loop

A self-proposal is an agent-generated candidate action. It must remain a
proposal until the gate returns `PROCEED`.

The loop must not chain indefinitely. Repeated proposals without resolution
enter `SAFE_MODE`.

## Charter Expansion Request

If the current charter is too narrow, the agent may request expansion. That
request is itself a self-proposal and should normally `PAUSE` for operator
review.

## Advisory Layer Boundary

Emotional, social, or advisory language may help communicate risk and next
steps. It remains advisory only. It cannot grant authority, override a gate, or
convert a proposal into an approved action.

## Runtime Mode Names

Use generic implementation labels:

- `research_officer_mode`
- `curiosity_profile`
- `bounded_initiative_mode`
- `supervised_episode_mode`

Do not name runtime modes after copyrighted characters or franchise terms.
