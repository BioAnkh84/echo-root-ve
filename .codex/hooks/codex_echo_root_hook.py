#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from echo_root_receipt import append_receipt, verify_chain  # noqa: E402
from repo_map import DEFAULT_EXCLUDES, build_repo_map, build_snapshot, write_snapshot  # noqa: E402


RUNTIME_DIR = Path(os.environ.get("ECHO_ROOT_CODEX_HOOK_DIR", REPO_ROOT / "ve_data" / "codex_hooks"))
LEDGER = RUNTIME_DIR / "codex_hook_receipts.jsonl"
REPO_MAP_SNAPSHOT = RUNTIME_DIR / "repo_map_latest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_stdin_json() -> dict[str, Any]:
    if sys.stdin.isatty():
        return {}
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {"stdin": data}
    except json.JSONDecodeError:
        return {"stdin_text": raw[:4000]}


def _git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _event_request(event: str, payload: dict[str, Any]) -> dict[str, Any]:
    tool_name = str(payload.get("tool_name") or payload.get("tool") or payload.get("name") or event)
    command = payload.get("command") or payload.get("args") or payload.get("input") or payload.get("stdin_text") or ""
    requested_action = f"codex hook {event}"
    if command:
        requested_action = f"{requested_action}: {str(command)[:220]}"

    branch = _git(["branch", "--show-current"]) or "unknown"
    status = _git(["status", "--porcelain"])
    dirty = bool(status)
    event_lower = event.lower()
    action_lane = "L1_READ_CLASSIFY"
    rho = 0.76
    delta = 0.12
    confidence = "high"

    if event_lower in {"pretooluse", "permissionrequest"}:
        action_lane = "L2_WRITE_ANNOTATE_INDEX"
        rho = 0.72
        delta = 0.20 if dirty else 0.16
        confidence = "medium"
    if "delete" in str(command).lower() or "remove-item" in str(command).lower() or "git reset" in str(command).lower():
        action_lane = "L3_REMOVE_DELETE_RESTRUCTURE"
        delta = 0.41

    return {
        "actor_id": os.environ.get("USERNAME") or os.environ.get("USER") or "operator",
        "agent_id": "codex",
        "model_id": os.environ.get("CODEX_MODEL", "codex"),
        "provider_id": "openai-codex",
        "route_id": f"codex-hook:{event}:{branch}",
        "action_lane": action_lane,
        "requested_action": requested_action,
        "consent_scope_present": True,
        "rho": rho,
        "delta": delta,
        "dry_run": True,
        "confidence": confidence,
        "fallback_status": "none",
        "tool_name": tool_name,
        "files_touched": [],
        "input": {
            "event": event,
            "branch": branch,
            "dirty": dirty,
            "payload_keys": sorted(payload.keys()),
        },
    }


def _write_hook_receipt(event: str, payload: dict[str, Any]) -> int:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    chain_valid, chain_errors = verify_chain(LEDGER)
    request = _event_request(event, payload)
    receipt = append_receipt(LEDGER, request, chain_valid=chain_valid)
    result = {
        "event": event,
        "decision": receipt["decision"],
        "reason": receipt["reason"],
        "ledger": str(LEDGER),
        "chain_valid_before_append": chain_valid,
        "chain_errors": chain_errors[:3],
    }
    print(json.dumps(result, sort_keys=True))
    return 0


def _session_start(payload: dict[str, Any]) -> int:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    excludes = set(DEFAULT_EXCLUDES)
    entries = build_repo_map(REPO_ROOT, depth=3, excludes=excludes)
    snapshot = build_snapshot(REPO_ROOT, 3, entries, excludes)
    write_snapshot(REPO_MAP_SNAPSHOT, snapshot)
    _write_hook_receipt("SessionStart", payload | {"repo_map_hash": snapshot["map_hash"]})
    print(
        json.dumps(
            {
                "event": "SessionStart",
                "repo_map_hash": snapshot["map_hash"],
                "repo_map_entries": snapshot["entry_count"],
                "snapshot": str(REPO_MAP_SNAPSHOT),
                "boundary": "Repo map is orientation, not proof.",
            },
            sort_keys=True,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Echo Root Codex hook bridge")
    parser.add_argument("event", choices=["SessionStart", "PreToolUse", "PermissionRequest", "PostToolUse", "Stop"])
    args = parser.parse_args()
    payload = _read_stdin_json()

    if args.event == "SessionStart":
        return _session_start(payload)
    return _write_hook_receipt(args.event, payload)


if __name__ == "__main__":
    raise SystemExit(main())
