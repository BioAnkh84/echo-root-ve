# Vulpine Echo (VE) - Echo Root Execution Harness

Vulpine Echo is a public test harness for Echo Root OS.

It demonstrates a simple idea:

```text
AI understanding is not permission.
Execution should be gated, enforced, and recorded.
```

VE is not the whole Echo Root habitat. It is the execution and audit layer: a place to test governed runs, ledger receipts, integrity checks, and reproducible demo behavior.

---

## What This Is

VE is a trust-gated audit and execution harness.

It is designed to show that a request can move through a public, inspectable control path before anything acts:

```text
Input
  -> governance gate
  -> enforcement decision
  -> route contract
  -> execution harness
  -> ledger receipt
  -> integrity check
```

The goal is to make AI-human operation more observable, bounded, and reviewable.

---

## Why This Matters

Most AI systems decide behavior internally.

Echo Root enforces:

```text
decision before execution
deterministic control
auditable outcome
```

This supports controlled AI deployment without treating capability as authority.

---

## What It Does Today

- runs local test commands through a governed harness
- records execution receipts in JSONL ledgers
- supports PowerShell, Python, and CI-facing checks
- validates ledger and manifest integrity
- generates repo-map receipts so humans and AI can share the same orientation snapshot before deeper search
- demonstrates `PROCEED`, `PAUSE`, and `ABORT` style execution control
- supports consent-first human/local-AI pairing records with clarification before nuanced recording or training export
- supports a local contact registry for human/AI interaction context and cadence-based status confirmation
- keeps a public known-gaps register

---

## What It Does Not Do

- it does not grant AI unlimited autonomy
- it does not replace human approval
- it does not prove safety for production or safety-critical use
- it does not expose private Echo Nexus / Cipher habitat data
- it does not include private memories, credentials, or operator records
- it does not claim general intelligence

---

## Quickstart

```powershell
git clone https://github.com/BioAnkh84/echo-root-ve.git
cd .\echo-root-ve
powershell -ExecutionPolicy Bypass -File .\ve_prepush_check.ps1
```

If the audit passes, VE has verified the public harness, ledger checks, and baseline repo health.

For the v0.1.0 license-readiness demo:

```powershell
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario proceed
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario pause
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario abort
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl verify
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl replay
py -3.11 -m unittest discover -s Tests
```

---

## Decision Model

| Condition | Decision | Behavior |
| --- | --- | --- |
| Consent scope present, `rho >= 0.70`, `delta <= 0.30` | `PROCEED` | normal execution |
| Missing scope, fallback, weak context, unclear confidence, write-budget pressure, or empty evidence | `PAUSE` | safe review |
| Forbidden action, destructive action without L3 approval, identity/scope conflict, or `delta > 0.40` | `ABORT` | blocked |
| Broken receipt chain, missing policy, unsafe fallback, or repeated failed checks | `SAFE_MODE` | fail closed |

---

## Public Architecture

| Component | Public role |
| --- | --- |
| Echo Root | Governance concept and decision authority |
| VE kernel | Execution and audit harness |
| Redivous | Enforcement role |
| Bridge | Route contract between decision and execution |
| Ledger | Append-only evidence trail |
| Quickcheck | Integrity and regression check |

This repository describes the public execution harness. Private habitat work, operator data, and internal scoring details stay outside this repo.

---

## Runtime Guarantees

- governance is evaluated before execution
- uncertain inputs can be routed to safe review
- unsafe inputs can be blocked
- execution decisions can be traced with receipts
- CI-compatible checks can validate the public harness

These are harness guarantees, not certification or safety guarantees.

---

## Key Files

| File | Role |
| --- | --- |
| `ECHO_ROOT_PROOF_PACKET.md` | Five-minute reviewer orientation for governed habitat architecture |
| `ECHO_ROOT_MARKET_READINESS.md` | Public positioning, audience, claim boundaries, and demo-readiness checklist |
| `ECHO_ROOT_ONE_DIAGRAM.mmd` | One-diagram flow from pairing to replay and lessons |
| `ECHO_ROOT_10_MIN_DEMO_SCRIPT.md` | Short demo path for gate, audit, replay, and doctrine |
| `ECHO_ROOT_REVIEWER_QUICKSTART.md` | Reviewer checklist and first-run commands |
| `ve_kernel.ps1` | PowerShell execution harness |
| `ve_kernel.py` | Python execution bridge |
| `ve_quickcheck.py` | Integrity validation |
| `ve_schema_check.py` | Ledger chain validation |
| `ve_manifest_verify.py` | File manifest verification |
| `ve_prepush_check.ps1` | Local pre-push audit |
| `ve_pairing_recorder.py` | Consent-first human/local-AI pairing recorder |
| `ve_pairing_clarifier.py` | Clarification check for nuanced or sensitive pairing intent |
| `ve_pairing_gate_context.py` | Builds structured gate payloads from pairing, consent, and clarification signals |
| `ve_contact_registry.py` | Local contacts/context registry for people, AIs, services, and groups |
| `ve_audit_chain.py` | Append-only signed audit chain for medical-grade-inspired evidence |
| `ve_deviation_classifier.py` | Classifies nominal/advisory/adverse gate outcomes |
| `ve_twin_state.py` | Lightweight pairing digital twin state |
| `ve_gate_pipeline.py` | Unified pairing gate envelope with signed audit, deviation class, and twin delta |
| `ve_gate_replay.py` | Forensic replay of signed gate pipeline audit records |
| `ve_replay_report.py` | HUD-style HTML and markdown reports for replay output |
| `ve_mission_memory.py` | Habitat mission memory for purpose, constraints, success conditions, and non-goals |
| `ve_lessons_ledger.py` | Lessons learned ledger for incidents, fixes, and verified patterns |
| `ve_habitat_constitution.py` | Constitution audit for Echo Root doctrine rules |
| `echo_root_receipt.py` | v0.1.0 receipt gate, hash-chain receipt engine, and replay demo |
| `repo_map.py` | Deterministic repo-map receipt for human/AI orientation |
| `schemas/echo_root_receipt.schema.json` | v0.1.0 receipt schema |
| `QUICKSTART.md` | install, demo, verify, replay, and test commands |
| `ARCHITECTURE.md` | release architecture and authority levels |
| `RELEASE_EVIDENCE.md` | test command, fault modes, sample receipt fields, known limits |
| `LICENSE_READINESS_CHECKLIST.md` | licensing package checklist and release tag instructions |
| `VE_PAIRING_CLARIFICATION_PROTOCOL.md` | Startup posture for clarifying intent before action, recording, or training export |
| `VE_PAIRING_GATE_CONTEXT.md` | Guide for pairing signals that assist VE gate decisions |
| `VE_MEDICAL_GRADE_SPEC.md` | Medical-grade-inspired control posture and digital twin direction |
| `VE_VSA_BASELINE_DEVIATION_DOCTRINE.md` | VSA doctrine update: baseline deviation detection, metadata, and no emotion/diagnosis/authority claims |
| `VE_GATE_PIPELINE.md` | Single-command integration pipeline for audit-ready gate decisions |
| `VE_GATE_REPLAY.md` | Replay/forensics guide for reconstructing gate decisions |
| `VE_REPLAY_REPORT.md` | Operator-readable replay report surface |
| `VE_HABITAT_DOCTRINE.md` | Mission memory, lessons learned, and constitution audit overview |
| `VE_CONTACT_REGISTRY.md` | Contact cadence and status-confirmation guidance |
| `WHAT_THIS_IS.md` | One-page orientation |
| `KNOWN_GAPS.md` | Honest public gap register |
| `JOURNAL.md` | Build log and milestone history |

---

## Status

Current public state:

- active experimental prototype
- audit-first repo structure
- CI-compatible checks
- known gaps documented openly
- part of the Team PURP independent-builder lab

---

## Philosophy

```text
Gate before execution.
Consent before authority.
Receipts before trust.
Human review before expansion.
```

Echo Root separates decision authority from execution so behavior can be reviewed, constrained, and recorded before it becomes action.
