# Spatial Governance Layer

The Spatial Governance Layer is future-facing adapter scaffolding for physical
operational spaces.

It is not flight control, collision avoidance, navigation, mesh networking, or
actuator command software. It evaluates whether a physical autonomy event is
inside a governed operational envelope and writes a reviewable receipt.

## Doctrine

- Occupying space is not permission.
- Mobility is not authority.
- Sensor contact is not consent.
- Position is not the whole state.
- Path history matters.
- Operational envelope must be authorized and replayable.

## Core Signals

- position
- operational envelope
- authority identity
- zone authorization
- authority transfer receipt
- proximity to humans
- altitude and speed bounds
- sensor confidence
- rho
- delta
- receipt chain state

## Decision Semantics

`PROCEED` means the event is inside the authorized envelope and the evidence
thresholds are met.

`PAUSE` means operator review is required because scope, authority, envelope,
proximity, sensor confidence, or transfer evidence is unclear.

`ABORT` means the event violates a hard boundary, such as attempting to command
an actuator through this governance adapter.

`SAFE_MODE` means the governance substrate is not trustworthy enough to
continue, such as a broken receipt chain or missing policy.

## Adapter Boundary

`spatial_governance.py` can classify and receipt:

- inside/outside envelope
- altitude/speed bounds
- proximity breach
- authority mismatch
- authority transfer without receipt
- zone authorization missing
- unsafe fallback

It cannot:

- fly a drone
- navigate a path
- avoid a collision
- issue motor or actuator commands
- approve its own operating envelope
- convert presence into authorization

## Hummingbird Profile

Hummingbird can later use this as an application profile:

```text
human requests help
  -> mission envelope opened
  -> authority logged
  -> vehicle event enters envelope review
  -> spatial_governance_gate receipt
  -> operator/system decides safe next step
```

The current repo only includes the governance adapter. Any physical autonomy
integration needs a separate safety, robotics, and legal review.
