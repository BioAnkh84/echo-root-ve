# Echo-Root-VE Architecture

## Product Definition

Echo-Root-VE is a runtime governance layer for agentic AI. It intercepts proposed actions before execution, checks identity/scope/consent/drift, writes replayable receipts, and prevents capability from silently becoming authority.

## Control Flow

```text
proposed action
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

## Doctrine

Capability does not equal authority.
Output does not equal permission.
Fallback does not equal consent.
Signal does not equal command.
Empty folder does not equal missing README.
No receipt means no trusted operation.
