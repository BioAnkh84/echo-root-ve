# Compliance Alignment

Echo-Root-VE is designed to support auditability, human oversight, logging, and risk controls. It does not claim certification, regulatory approval, or guaranteed compliance.

## NIST AI RMF Style Mapping

| Echo-Root-VE concept | Alignment language |
| --- | --- |
| Product definition and action lanes | Supports govern/map activities by naming who may act, on what scope, and under what lane. |
| Consent scope gate | Supports human oversight and bounded authority before execution. |
| `rho` and `delta` gate | Supports measure/manage activities by making confidence and drift explicit. |
| Receipt schema | Supports auditability and post-action review. |
| Hash-chain receipts | Supports tamper-evident logging and replayable evidence. |
| Provider fallback gate | Supports risk controls when execution route or model provenance changes. |
| Write budget controls | Supports blast-radius limits for agentic actions. |
| `SAFE_MODE` | Supports fail-closed behavior when governance evidence is broken or missing. |

## Claim Boundary

Use:

- "designed to support auditability"
- "aligned with risk-management practices"
- "provides action gating and replayable receipts"

Do not use:

- "certified compliant"
- "regulator approved"
- "guarantees safety"
- "prevents all harmful outcomes"
