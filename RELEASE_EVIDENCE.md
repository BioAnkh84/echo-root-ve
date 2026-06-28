# Release Evidence

Target: v0.1.0 License-ready MVP

## Test Command

```powershell
py -3.11 -m unittest discover -s Tests
```

Result on 2026-06-13:

```text
Ran 82 tests
OK
```

## Syntax Check

```powershell
py -3.11 -m py_compile .\echo_root_receipt.py .\ve_gate_pipeline.py .\ve_gate_replay.py .\ve_audit_chain.py
```

Result on 2026-06-11: passed.

## Demo Commands

MCP-independent proof path:

```powershell
py -3.11 .\echo_root_cli.py prove --reset
```

Result on 2026-06-12:

- repo-map orientation receipt generated with `map_hash`
- decisions produced in order: `PROCEED`, `PAUSE`, `ABORT`
- receipt chain verification: `ok: true`
- replay matched every decision
- claim boundary: MCP is optional for this proof path

Result on 2026-06-13 after bounded self-proposal changes:

- `echo_root_cli.py prove --reset`: `ok: true`
- decisions produced in order: `PROCEED`, `PAUSE`, `ABORT`
- receipt chain verification: `ok: true`
- replay matched every decision

```powershell
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario proceed
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario pause
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario abort
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl verify
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl replay
```

Result on 2026-06-11:

- receipt chain verification: `ok: true`
- replayed `PROCEED`: `matches: true`
- replayed `PAUSE`: `matches: true`
- replayed `ABORT`: `matches: true`

## Repo Map Receipt

```powershell
py -3.11 .\repo_map.py --depth 3 --json
py -3.11 .\repo_map.py --depth 3 --write-snapshot .\receipts\repo_map_latest.json --json
py -3.11 .\repo_map.py --depth 3 --delta-from .\receipts\repo_map_latest.json
```

The repo map receipt gives humans and AI a shared orientation hash before deeper search. It excludes noisy folders such as `.git`, `.venv`, `archive`, and generated `ve_data`.

The delta receipt compares a current map against a previous snapshot and reports added paths, removed paths, file/folder kind changes, and size changes only. It does not prove semantic content changes.

## Fault Modes Covered

- missing consent scope
- route fallback
- empty folder/no evidence
- write budget exceeded
- destructive action without L3 approval
- drift above abort threshold
- broken hash chain
- receipt schema failure
- replay mismatch detection
- repo map orientation hash generation
- repo map delta generation
- L1 self-proposal proceeds without tool authority
- L2 self-proposal proceeds as draft-only preparation
- L3 read-only self-proposal pauses when it requests write access
- L4 bounded-write self-proposal aborts when file budget is exceeded
- L5 supervised episode pauses without stop condition and review interval
- missing autonomy charter pauses
- permission request pauses
- memory mutation without receipt aborts
- repeated self-proposal loop triggers `SAFE_MODE`
- self-proposal receipt schema and `calibration_reason` coverage
- spatial governance adapter proceeds for authorized envelope posture
- spatial governance pauses on missing zone authorization, envelope breach, proximity breach, and authority transfer without receipt
- spatial governance aborts actuator-command attempts
- spatial governance enters `SAFE_MODE` on broken receipt chain

## Sample Receipt Fields

Every v0.1.0 receipt includes:

- `receipt_id`
- `timestamp`
- `actor_id`
- `agent_id`
- `model_id`
- `provider_id`
- `route_id`
- `action_lane`
- `requested_action`
- `consent_scope_present`
- `rho`
- `delta`
- `decision`
- `reason`
- `files_touched`
- `tool_name`
- `input_hash`
- `output_hash`
- `hash_prev`
- `hash_self`
- `replayable`
- `fallback_status`

Receipts may also include `gate_inputs` so replay can reproduce non-schema gate triggers such as empty-folder review, dry-run posture, confidence ambiguity, context limits, and write-budget counters.

Self-proposal gate receipts use `schemas/self_proposal.schema.json` and include:

- `event_type: self_proposal_gate`
- `proposal_id`
- `autonomy_level`
- `action_lane`
- `requested_authority`
- `decision`
- `rho`
- `delta`
- `gamma0` / `consent_scope_present`
- `difference_makers`
- `calibration_reason`
- `policy_tier`
- `route_id`
- `model_id`
- `provider_id`
- `files_expected`
- `files_touched_actual`
- `tool_expected`
- `tool_actual`
- `stop_condition`
- `review_interval`
- `operator_review_required`
- `hash_prev`
- `hash_self`
- `replayable`

Spatial governance gate receipts use `schemas/spatial_governance.schema.json`
and include:

- `event_type: spatial_governance_gate`
- `event_id`
- `vehicle_id`
- `mission_id`
- `envelope_id`
- `authority_id`
- `position`
- `velocity_mps`
- `zone_authorized`
- `sensor_confidence`
- `rho`
- `delta`
- `decision`
- `decision_reason`
- `difference_makers`
- `calibration_reason`
- `classification`
- `envelope`
- `operator_review_required`
- `hash_prev`
- `hash_self`

## Known Limitations

- Schema validation is implemented with a local validator to avoid adding a dependency.
- Demo receipts are unsigned hash-chain records. Existing `ve_audit_chain.py` provides HMAC-signed audit records for the older gate pipeline.
- Policy loading is represented by function parameters in v0.1.0 and should become a formal policy file before production packaging.
- The v0.1.0 package is local-first and does not include hosted service deployment.
- Spatial governance is adapter scaffolding only. It does not provide flight control, collision avoidance, navigation, networking, or actuator control.

## What Is Not Claimed

- No certification claim.
- No regulatory approval claim.
- No guaranteed compliance claim.
- No claim that all harmful actions are prevented.
- No claim that model output is truthful or authorized without receipts and scope.
