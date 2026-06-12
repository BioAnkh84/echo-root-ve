# Echo-Root-VE Quickstart

Echo-Root-VE is a runtime governance layer for agentic AI. It intercepts proposed actions before execution, checks scope/confidence/drift, writes replayable receipts, and prevents capability from silently becoming authority.

## Setup

No package install is required for the v0.1.0 local demo. Use Python 3.11+.

```powershell
py -3.11 --version
```

## Run The Demo

One-command proof path, useful when MCP tools are not live-exposed:

```powershell
py -3.11 .\echo_root_cli.py prove --reset
```

This runs repo orientation, writes `PROCEED` / `PAUSE` / `ABORT` receipts,
verifies the hash chain, and replays the decisions. MCP is optional for this
proof path.

```powershell
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario proceed
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario pause
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl demo --scenario abort
```

Expected decisions:

- `PROCEED`: consent scope present, `rho >= 0.70`, `delta <= 0.30`
- `PAUSE`: review needed before writing or acting
- `ABORT`: blocked because the proposed action violates a hard gate

## Verify And Replay

```powershell
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl verify
py -3.11 .\echo_root_receipt.py --ledger .\receipts\demo_receipts.jsonl replay
```

## Shared Repo Orientation

```powershell
py -3.11 .\echo_root_cli.py repo-map --depth 3
py -3.11 .\repo_map.py --depth 3 --json
```

This produces a repo-map receipt with a stable hash. Use it as orientation before deeper search; it is not a health or freshness claim.

Optional generated snapshot and delta:

```powershell
py -3.11 .\repo_map.py --depth 3 --write-snapshot .\receipts\repo_map_latest.json --json
py -3.11 .\repo_map.py --depth 3 --delta-from .\receipts\repo_map_latest.json
```

## Run Tests

```powershell
py -3.11 -m unittest discover -s Tests
```

## Claim Boundary

This release is a license-readiness MVP. It demonstrates installable gate logic, receipt writing, replay, and tests. It does not claim certification, regulatory approval, or guaranteed compliance.
