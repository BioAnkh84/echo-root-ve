# Annunimas / ARDA Alignment Map

Last reviewed: 2026-06-28

This map helps humans and AI compare Echo Root VE with the Annunimas / ARDA
reference surfaces without treating another repository as local authority.

Echo Root VE remains the governing harness for this repository. Annunimas,
ARDA repos, Mythos notes, Local Cipher, and other external AI outputs are
advisory evidence until they are converted into local receipts, schemas,
tests, or explicit human approvals.

## Source Surfaces

| Source | Observed role | Echo Root stance |
| --- | --- | --- |
| `dward1502/Annunimas` | Private local-first auditable agent control plane. Includes routing, governance, memory, tools, HUD, fleet, and human knowledge surfaces. | Reference architecture only. Do not import private paths, operator state, or runtime claims without review. |
| `dward1502/Arda-Agent-Loop-Contract` | Portable inspect-act-verify contract and validator for autonomous agent cycles. | Strong fit for Echo Root receipts and lifecycle language. |
| `dward1502/Arda-tool-gate` | Rust policy gate and JSON decision receipts for autonomous tool invocations. | Strong fit for pre-execution authority checks. Keep execution outside the gate. |
| `dward1502/Arda-Signal-Grid` | Governed signal routing blueprint for comments, alerts, pauses, review requests, and state projections. | Useful comparison for route envelopes, PAUSE behavior, and operator review surfaces. |
| `dward1502/Arda-Service-Registry` | Service discovery and governance contract registry blueprint. | Useful future map for service identity, lifecycle, and health posture. |
| Annunimas PR `#9` Echo Root Local Cipher Bridge | Draft bridge describing rho/gamma/delta gate signals before Charon execution. | Advisory seed. Echo Root VE should prefer local schemas, tests, receipts, and explicit bridge contracts. |

## Concept Mapping

| Echo Root VE concept | ARDA / Annunimas analogue | Shared idea | Boundary |
| --- | --- | --- | --- |
| Governance before execution | Tool Gate, Agent Loop execute stage | Permission must be decided before side effects. | A gate is not a sandbox and does not execute actions. |
| Self-proposal gate | Agent Loop plan/task stages | Agents may propose bounded work before execution authority exists. | Proposal is not approval. |
| Receipt chain | Agent Loop cycle receipts, Tool Gate decision receipts | Decisions should be replayable and machine-readable. | External receipts must be normalized before local trust. |
| Spatial governance adapter | Signal Grid route plans and operational state projections | Context, area, risk, and review posture should travel as explicit envelopes. | VE does not command actuators, navigation, drones, or safety-critical systems. |
| Scheduled health checks | Annunimas Warden / Chronos style monitoring | Read-only evidence can be collected on cadence. | Health evidence does not authorize auto-repair or mutation. |
| Repo-map receipt | Annunimas CODEMAP / FILE_TREE / source-map surfaces | AI needs compact orientation before broad parsing. | Presence is not freshness; rerun local checks. |
| External AI boundary | Annunimas governance wording boundaries | Advisory systems can inform local decisions. | External AI output is not local authority. |
| Local Cipher habitat | Annunimas Charon / HUMAN / Mnemosyne style runtime surfaces | Local-first context can support human/AI pairing. | Private habitat data stays outside public VE commits unless sanitized. |
| Service identity | ARDA Service Registry | Services should declare identity, lifecycle, dependencies, and policy posture. | Registry entries should not imply live health without fresh proof. |

## Integration Rules

1. Do not vendor Annunimas or ARDA code into Echo Root VE by default.
2. Prefer contract-level adoption: schemas, receipts, examples, docs, and tests.
3. Treat any external repo, AI, HUD, or runtime output as advisory until local
   Echo Root evidence exists.
4. Keep BTDS, Local Cipher, operator records, credentials, and private habitat
   details out of public Echo Root VE unless explicitly sanitized.
5. If an ARDA concept changes Echo Root behavior, add or update a local test.
6. If an ARDA concept changes authority, add or update a local receipt example.
7. If an ARDA concept changes public claims, update safety and non-goal wording.

## Adoption Candidates

| Candidate | Local Echo Root form | Priority |
| --- | --- | --- |
| Agent Loop cycle schema | `schemas/inspect_act_verify_cycle.schema.json` plus one example receipt | High |
| Tool invocation envelope | `schemas/tool_invocation_envelope.schema.json` plus allowed / review / denied examples | High |
| Service contract registry | `schemas/service_contract.schema.json` and local examples for VE, Local Cipher, and external advisory systems | Medium |
| Signal route plan | Extend spatial governance examples with review request, pause, escalation, and suppress outcomes | Medium |
| Bridge note for Local Cipher | Public-safe contract showing Cipher as assistant inside the habitat, not certifier or authority | Medium |

## Human / AI Use

When an AI sees an Annunimas or ARDA reference, it should ask:

- Is this a concept, a schema, a receipt, a test, or a live runtime claim?
- Does Echo Root VE already have a local equivalent?
- Does adopting it change authority, privacy, safety, or public claims?
- What local receipt proves the decision?
- What human approval is required before mutation or publication?

The default answer should be conservative: map first, test second, integrate
only after the local boundary is clear.
