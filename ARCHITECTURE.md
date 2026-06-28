# Echo-Root-VE Architecture

## Product Definition

Echo-Root-VE is a runtime governance layer for agentic AI. It intercepts proposed actions before execution, checks identity/scope/consent/drift, writes replayable receipts, and prevents capability from silently becoming authority.

## Control Flow

```text
proposed action
  -> optional self-proposal classification
  -> identity and scope check
  -> consent scope check
  -> confidence and drift gate
  -> write budget and authority check
  -> decision: PROCEED | PAUSE | ABORT | SAFE_MODE
  -> receipt append
  -> hash-chain verification
  -> replay
```

## Decision Semantics

- `PROCEED`: consent scope is present, `rho >= 0.70`, and `delta <= 0.30`.
- `PAUSE`: review is required because evidence, context, route, confidence, scope, or write budget is insufficient.
- `ABORT`: the action violates a hard gate.
- `SAFE_MODE`: the governance substrate is not trustworthy enough to continue.

## Bounded Self-Proposals

A self-proposal is an agent-generated candidate action. It is not approval.
The proposal must be classified by autonomy level, lane, scope, risk, requested
authority, policy tier, and receipt path before any execution.

Supported autonomy levels are:

- `L0_CHAT_ONLY`: response only.
- `L1_SUGGEST`: may suggest a next step; no tool use.
- `L2_PREPARE`: may draft a plan, checklist, patch proposal, or message; no execution.
- `L3_READ_ONLY_CHECK`: may inspect allowed files or status; no writes.
- `L4_BOUNDED_WRITE`: may edit only within explicit scope and budget.
- `L5_SUPERVISED_EPISODE`: may run a bounded episode with stop condition and review interval.
- `L6_SAFE_MODE`: emergency containment only; not higher autonomy.

Self-proposals use `schemas/self_proposal.schema.json` and write
`self_proposal_gate` receipts. They are bounded by `docs/AUTONOMY_CHARTER.md`.

## Spatial Governance Adapter

`spatial_governance.py` is future-facing adapter scaffolding for operational
envelope review. It evaluates position, authority, zone authorization,
proximity, speed, altitude, sensor confidence, `rho`, and `delta`, then writes a
`spatial_governance_gate` receipt.

It is not flight control, collision avoidance, navigation, mesh networking, or
actuator command software. Any attempt to use the adapter for physical action
returns `ABORT`.

## Authority Levels

- `L1`: read/classify only.
- `L2`: write/annotate/index only. Requires evidence threshold before writing.
- `L3`: remove/delete/restructure. Requires explicit approval receipt.

## Write Budget Controls

Default controls are intentionally conservative:

```json
{
  "max_files_touched_per_run": 5,
  "max_files_created_per_run": 3,
  "max_folders_touched_per_run": 3,
  "dry_run_required": true,
  "destructive_actions_allowed": false,
  "recursive_generation_allowed": false
}
```

## Empty Folder Rule

An empty folder is not missing documentation. Empty folders are marked `candidate_for_review`. The gate writes an audit receipt only if audit receipts are enabled. It never deletes an empty folder unless L3 destructive authority is explicitly approved.

## Provider Fallback Gate

If model, provider, or route changes mid-run, Echo-Root-VE logs `fallback_status` and downgrades to `PAUSE` or read-only posture. Writes do not continue after fallback unless explicitly approved.

## External AI Authority Boundary

Local AI can be a governed participant inside the habitat. External AI lanes are
advisory evidence by default unless explicitly onboarded, scoped, gated, and
receipted.

External routing does not imply trust. External success does not create internal
authority. External AI output must pass local gates before it affects action.

See `docs/EXTERNAL_AI_AUTHORITY_BOUNDARY.md`.

## Doctrine

Capability does not equal authority.
Output does not equal permission.
Fallback does not equal consent.
Signal does not equal command.
Empty folder does not equal missing README.
No receipt means no trusted operation.
