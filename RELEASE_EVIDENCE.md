# Release Evidence

Target: v0.1.0 License-ready MVP

## Test Command

```powershell
py -3.11 -m unittest discover -s Tests
```

Result on 2026-06-12:

```text
Ran 58 tests
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

## Known Limitations

- Schema validation is implemented with a local validator to avoid adding a dependency.
- Demo receipts are unsigned hash-chain records. Existing `ve_audit_chain.py` provides HMAC-signed audit records for the older gate pipeline.
- Policy loading is represented by function parameters in v0.1.0 and should become a formal policy file before production packaging.
- The v0.1.0 package is local-first and does not include hosted service deployment.

## What Is Not Claimed

- No certification claim.
- No regulatory approval claim.
- No guaranteed compliance claim.
- No claim that all harmful actions are prevented.
- No claim that model output is truthful or authorized without receipts and scope.
