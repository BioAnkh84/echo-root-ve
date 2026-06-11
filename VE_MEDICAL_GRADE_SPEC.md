# VE Medical-Grade-Inspired Spec

This document describes controls that move VE toward medical-grade-style discipline.

It does **not** claim FDA compliance, clinical validation, or suitability for medical use.

## Reference Posture

FDA 21 CFR Part 11 is a useful reference point for electronic records and electronic signatures because it emphasizes trustworthy, reliable electronic records, audit trails, validation, and record/signature controls. VE uses that as inspiration only.

Official references:

- FDA guidance: Part 11, Electronic Records; Electronic Signatures - Scope and Application
- 21 CFR Part 11 text: Electronic Records; Electronic Signatures

## Control Goals

| Control | VE Artifact |
| --- | --- |
| Append-only signed audit records | `ve_audit_chain.py` |
| Adverse/deviation classification | `ve_deviation_classifier.py` |
| Pairing clarification TTL fail-closed | `ve_pairing_gate_context.py` |
| Consent-before-record | `ve_pairing_recorder.py` |
| Human/operator/contact resolution authority | `ve_pairing_recorder.py` and `ve_pairing_gate_context.py` |
| Lightweight digital twin state | `ve_twin_state.py` |

## Medical-Grade-Inspired Rules

1. No silent self-authorization.
2. No recording without consent.
3. No training export without explicit training consent.
4. Missing clarification is unresolved.
5. PROPOSE expires and fails closed.
6. Gate deviation is classified, not merely logged.
7. Audit records are hash-chained and signed.
8. Digital twin state is advisory evidence, not execution permission.

## Digital Twin Direction

The VE twin is a persistent mirror of expected pairing behavior:

- expected cadence
- expected action class
- expected decision
- baseline rho/gamma/delta
- observation count

The twin can compare observed drift against baseline drift. It should assist the gate, not bypass it.
