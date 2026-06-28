# Echo Root Proof Packet

## One Sentence

Echo Root is a governed AI habitat architecture that makes human-AI cooperation auditable through consent gates, clarification, doctrine memory, signed records, and replayable forensic evidence.

## The Problem

Most agent systems can answer what they tried to do. Fewer can prove what they were allowed to do, who resolved ambiguity, whether sensitive recording was consented to, and whether later reviewers can reconstruct the decision path.

Echo Root targets that gap:

```text
Capability without consent is not authority.
Logging without replay is not forensics.
Pairing context is evidence for the gate, not permission to bypass it.
```

## What This Repository Shows

This repository is the VE execution and evidence harness for Echo Root. It demonstrates a narrow, reviewable vertical slice:

1. A human/local-AI pairing creates context.
2. Nuanced or sensitive intent triggers clarification.
3. The gate uses pairing context as evidence.
4. The action is classified as `PROCEED`, `PROPOSE`, `PAUSE`, or `ABORT`.
5. The decision is written to a signed append-only audit chain.
6. A deviation classifier records nominal/advisory/adverse posture.
7. A lightweight twin state captures observed-vs-expected delta at decision time.
8. Replay reconstructs the signed decision path for later review.
9. Doctrine memory records mission, constraints, lessons learned, and constitution checks.

The v0.1 release packet also includes bounded self-proposal mechanics:

```text
agent proposes candidate action
  -> charter, scope, authority, rho, and delta review
  -> PROCEED / PAUSE / ABORT / SAFE_MODE
  -> self_proposal_gate receipt
```

A self-proposal is not approval. It cannot execute, approve itself, expand
scope, bypass gates, run indefinitely, or turn L5 into open-ended autonomy.

## Evidence, Not Claims

| Claim | Evidence Surface |
| --- | --- |
| Consent and clarification are explicit | `ve_pairing_clarifier.py`, `VE_PAIRING_CLARIFICATION_PROTOCOL.md` |
| Pairing data does not bypass gates | `ve_pairing_gate_context.py`, `VE_PAIRING_GATE_CONTEXT.md` |
| Audit records are signed and chained | `ve_audit_chain.py`, `Tests/test_ve_medical_grade_controls.py` |
| Audit failure fails closed | `ve_gate_pipeline.py`, `Tests/test_ve_gate_pipeline.py` |
| Decisions can be replayed | `ve_gate_replay.py`, `VE_GATE_REPLAY.md` |
| Replay can detect classifier drift | `Tests/test_ve_gate_replay.py` |
| Operator-readable replay exists | `ve_replay_report.py`, `VE_REPLAY_REPORT.md` |
| Doctrine is auditable | `ve_habitat_constitution.py`, `VE_HABITAT_DOCTRINE.md` |
| Lessons are recorded without retraining | `ve_lessons_ledger.py`, `ve_data/habitat_lessons.jsonl` |
| VSA avoids emotion/diagnosis/authority claims | `VE_VSA_BASELINE_DEVIATION_DOCTRINE.md` |
| Bounded self-proposals stay gated | `self_proposal.py`, `docs/AUTONOMY_CHARTER.md`, `Tests/test_self_proposal.py` |

## What Makes It Different

The unusual asset is not one gate or one ledger. It is the interaction model:

```text
identity
consent
pairing
clarification
memory
gates
audit
doctrine
replay
nodes
operators
```

Echo Root treats those as one governed habitat, not disconnected features.

## What It Is Not

- Not FDA compliant medical software.
- Not a production safety certification.
- Not autonomous authority for AI agents.
- Not a replacement for human approval.
- Not a claim that all future behavior is safe.
- Not a container for private operator memories or credentials.
- Not voice lie detection, diagnosis, or emotion authority.

This is medical-grade-inspired architecture, not regulated medical software.

## Reviewer Flow

Read these in order:

1. `ECHO_ROOT_ONE_DIAGRAM.mmd`
2. `ECHO_ROOT_MARKET_READINESS.md`
3. `ECHO_ROOT_REVIEWER_QUICKSTART.md`
4. `ECHO_ROOT_10_MIN_DEMO_SCRIPT.md`
5. `VE_GATE_PIPELINE.md`
6. `VE_GATE_REPLAY.md`
7. `VE_HABITAT_DOCTRINE.md`
8. `VE_VSA_BASELINE_DEVIATION_DOCTRINE.md`
9. `docs/AUTONOMY_CHARTER.md`

## Ten-Minute Review Question

Do not ask, "Can the AI do more?"

Ask:

```text
Can the system explain what it was allowed to do,
why it chose the safe posture,
who resolved ambiguity,
and whether the record can be replayed later?
```

That is the proof target.
