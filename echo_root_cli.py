from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from echo_root_receipt import append_receipt, gate_decision, replay_receipt, verify_chain
from repo_map import DEFAULT_EXCLUDES, build_receipt as build_repo_map_receipt
from repo_map import build_repo_map


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_LEDGER = REPO_ROOT / "ve_data" / "cli_receipts" / "echo_root_cli_receipts.jsonl"


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _bool_arg(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"expected boolean, got {value!r}")


def _request_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "actor_id": args.actor_id,
        "agent_id": args.agent_id,
        "model_id": args.model_id,
        "provider_id": args.provider_id,
        "route_id": args.route_id,
        "action_lane": args.action_lane,
        "requested_action": args.action,
        "consent_scope_present": args.scope,
        "rho": args.rho,
        "delta": args.delta,
        "dry_run": args.dry_run,
        "confidence": args.confidence,
        "fallback_status": args.fallback_status,
        "tool_name": args.tool_name,
        "files_touched": args.file or [],
        "files_created": args.files_created,
        "empty_folder": args.empty_folder,
        "context_limit_exceeded": args.context_limit_exceeded,
        "forbidden_action": args.forbidden_action,
        "identity_scope_conflict": args.identity_scope_conflict,
        "recursive_generation": args.recursive_generation,
        "failed_checks": args.failed_checks,
    }


def _add_gate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--action", required=True, help="Proposed action to classify.")
    parser.add_argument("--scope", type=_bool_arg, default=True, help="Whether consent/scope is present.")
    parser.add_argument("--rho", type=float, default=0.78, help="Evidence/confidence score from 0 to 1.")
    parser.add_argument("--delta", type=float, default=0.14, help="Drift/risk score from 0 to 1.")
    parser.add_argument("--confidence", default="high", choices=["high", "medium", "unclear", "low"])
    parser.add_argument("--action-lane", default="L1_READ_CLASSIFY")
    parser.add_argument("--fallback-status", default="none")
    parser.add_argument("--tool-name", default="echo_root_cli")
    parser.add_argument("--file", action="append", help="File touched by the proposed action. Repeatable.")
    parser.add_argument("--files-created", type=int, default=0)
    parser.add_argument("--empty-folder", action="store_true")
    parser.add_argument("--context-limit-exceeded", action="store_true")
    parser.add_argument("--forbidden-action", action="store_true")
    parser.add_argument("--identity-scope-conflict", action="store_true")
    parser.add_argument("--recursive-generation", action="store_true")
    parser.add_argument("--failed-checks", type=int, default=0)
    parser.add_argument("--dry-run", type=_bool_arg, default=True)
    parser.add_argument("--actor-id", default="operator")
    parser.add_argument("--agent-id", default="codex")
    parser.add_argument("--model-id", default="codex")
    parser.add_argument("--provider-id", default="openai-codex")
    parser.add_argument("--route-id", default="cli:fallback")


def command_repo_map(args: argparse.Namespace) -> int:
    root = Path(args.root)
    excludes = set(DEFAULT_EXCLUDES)
    excludes.update(args.exclude or [])
    entries = build_repo_map(root, depth=args.depth, excludes=excludes)
    _print_json(build_repo_map_receipt(root, args.depth, entries, excludes))
    return 0


def command_gate(args: argparse.Namespace) -> int:
    request = _request_from_args(args)
    decision, reason = gate_decision(request)
    _print_json(
        {
            "decision": decision,
            "reason": reason,
            "rho": request["rho"],
            "delta": request["delta"],
            "requested_action": request["requested_action"],
            "receipt_written": False,
            "claim_boundary": "Gate decision is evidence. It is not execution permission by itself.",
        }
    )
    return 0 if decision in {"PROCEED", "PAUSE"} else 2


def command_append_receipt(args: argparse.Namespace) -> int:
    request = _request_from_args(args)
    receipt = append_receipt(Path(args.ledger), request)
    _print_json(
        {
            "ledger": str(Path(args.ledger)),
            "receipt_id": receipt["receipt_id"],
            "decision": receipt["decision"],
            "reason": receipt["reason"],
            "hash_self": receipt["hash_self"],
        }
    )
    return 0 if receipt["decision"] in {"PROCEED", "PAUSE"} else 2


def command_verify_chain(args: argparse.Namespace) -> int:
    ok, errors = verify_chain(Path(args.ledger))
    _print_json({"ledger": str(Path(args.ledger)), "ok": ok, "errors": errors})
    return 0 if ok else 1


def command_replay(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    replay = [replay_receipt(row) for row in rows]
    _print_json({"ledger": str(ledger), "replay": replay, "all_match": all(row["matches"] for row in replay)})
    return 0 if all(row["matches"] for row in replay) else 1


def command_selftest(_: argparse.Namespace) -> int:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / ".codex" / "hooks" / "codex_echo_root_selftest.py")],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {"raw_output": proc.stdout}
    _print_json({"ok": proc.returncode == 0, "returncode": proc.returncode, "report": report})
    return proc.returncode


def command_live_probe(args: argparse.Namespace) -> int:
    cmd = [sys.executable, str(REPO_ROOT / ".codex" / "hooks" / "codex_hook_live_probe.py")]
    if args.before_count is not None:
        cmd.extend(["--before-count", str(args.before_count)])
    proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {"raw_output": proc.stdout}
    _print_json({"ok": proc.returncode == 0, "returncode": proc.returncode, "report": report})
    return proc.returncode


def command_prove(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    if args.reset and ledger.exists():
        ledger.unlink()

    root = Path(args.root)
    excludes = set(DEFAULT_EXCLUDES)
    entries = build_repo_map(root, depth=args.depth, excludes=excludes)
    repo_receipt = build_repo_map_receipt(root, args.depth, entries, excludes)

    scenarios = [
        {
            "requested_action": "read release evidence and summarize status",
            "action_lane": "L1_READ_CLASSIFY",
            "consent_scope_present": True,
            "rho": 0.82,
            "delta": 0.12,
            "dry_run": True,
            "confidence": "high",
            "tool_name": "echo_root_cli_prove",
        },
        {
            "requested_action": "write release notes from unclear evidence",
            "action_lane": "L2_WRITE_ANNOTATE_INDEX",
            "consent_scope_present": True,
            "rho": 0.74,
            "delta": 0.18,
            "dry_run": True,
            "confidence": "medium",
            "empty_folder": True,
            "tool_name": "echo_root_cli_prove",
        },
        {
            "requested_action": "delete project folder without L3 approval",
            "action_lane": "L3_REMOVE_DELETE_RESTRUCTURE",
            "consent_scope_present": True,
            "rho": 0.81,
            "delta": 0.11,
            "dry_run": True,
            "confidence": "high",
            "tool_name": "echo_root_cli_prove",
        },
    ]
    receipts = [append_receipt(ledger, scenario) for scenario in scenarios]
    ok, errors = verify_chain(ledger)
    replay = [replay_receipt(receipt) for receipt in receipts]
    decisions = [receipt["decision"] for receipt in receipts]
    proof_ok = ok and decisions == ["PROCEED", "PAUSE", "ABORT"] and all(row["matches"] for row in replay)

    _print_json(
        {
            "ok": proof_ok,
            "mode": "cli_fallback_adapter",
            "claim": "Echo Root can orient, gate, append receipts, verify hash-chain continuity, and replay decisions without live MCP exposure.",
            "repo_map": {
                "entry_count": repo_receipt["entry_count"],
                "map_hash": repo_receipt["map_hash"],
                "boundary": repo_receipt["orientation_use"],
            },
            "ledger": str(ledger),
            "decisions": decisions,
            "verify_chain": {"ok": ok, "errors": errors},
            "replay": replay,
            "mcp_boundary": "MCP is optional for this proof. CLI receipts remain available when external stdio MCP is not live-exposed.",
        }
    )
    return 0 if proof_ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Echo Root VE CLI fallback adapter")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER), help="Receipt ledger path for commands that write/read receipts.")
    sub = parser.add_subparsers(dest="command", required=True)

    repo_map = sub.add_parser("repo-map", help="Print a deterministic repo orientation receipt.")
    repo_map.add_argument("--root", default=str(REPO_ROOT))
    repo_map.add_argument("--depth", type=int, default=3)
    repo_map.add_argument("--exclude", action="append", default=[])
    repo_map.set_defaults(func=command_repo_map)

    gate = sub.add_parser("gate", help="Classify a proposed action without writing a receipt.")
    _add_gate_arguments(gate)
    gate.set_defaults(func=command_gate)

    append = sub.add_parser("append-receipt", help="Gate a proposed action and append a hash-chained receipt.")
    _add_gate_arguments(append)
    append.set_defaults(func=command_append_receipt)

    verify = sub.add_parser("verify-chain", help="Verify receipt hash-chain continuity.")
    verify.set_defaults(func=command_verify_chain)

    replay = sub.add_parser("replay", help="Replay receipt decisions from a ledger.")
    replay.set_defaults(func=command_replay)

    selftest = sub.add_parser("selftest", help="Run the Codex/Echo Root hook workflow self-test.")
    selftest.set_defaults(func=command_selftest)

    live_probe = sub.add_parser("live-probe", help="Inspect live Codex hook receipt activation.")
    live_probe.add_argument("--before-count", type=int)
    live_probe.set_defaults(func=command_live_probe)

    prove = sub.add_parser("prove", help="Run one-command CLI proof: repo map, PROCEED/PAUSE/ABORT receipts, verify, replay.")
    prove.add_argument("--root", default=str(REPO_ROOT))
    prove.add_argument("--depth", type=int, default=3)
    prove.add_argument("--reset", action="store_true", help="Delete the selected proof ledger before running.")
    prove.set_defaults(func=command_prove)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
