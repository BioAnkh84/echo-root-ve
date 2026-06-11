# VE Habitat Doctrine

This layer gives VE operational memory about itself.

It is not human memory, pairing memory, or private operator memory. It is system memory:

- mission memory
- lessons learned
- constitutional rules

## Tier 1 Additions

| Artifact | Purpose |
| --- | --- |
| `ve_mission_memory.py` | Stores purpose, constraints, current mission, success conditions, and non-goals. |
| `ve_lessons_ledger.py` | Records incidents, outcomes, fixes, lessons, and confidence. |
| `ve_habitat_constitution.py` | Audits events against core Echo Root principles. |

## Core Constitutional Rules

- Presence is not permission.
- Confidence is not authority.
- Pairing is not consent.
- Proposal is not execution.
- Pairing context becomes evidence for the gate, not permission to bypass it.

## Why This Matters

As VE grows, it should not rediscover the same lessons repeatedly. The habitat needs institutional memory:

```text
What happened?
What did we learn?
What rule did it reinforce?
What should future VE avoid?
```

This is doctrine, not autonomy.
