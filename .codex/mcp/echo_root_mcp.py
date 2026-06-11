#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from echo_root_receipt import append_receipt, gate_decision, verify_chain  # noqa: E402
from repo_map import DEFAULT_EXCLUDES, build_repo_map, build_snapshot  # noqa: E402


SERVER_NAME = "echo-root-ve"
SERVER_VERSION = "0.1.0"
DEFAULT_PROTOCOL_VERSION = "2025-06-18"
DEFAULT_LEDGER = REPO_ROOT / "ve_data" / "mcp_receipts" / "mcp_receipts.jsonl"
INSTRUCTIONS = (
    "Echo Root VE tools provide orientation, gate posture, receipts, and replay checks. "
    "Presence is not proof. Permission is authority change. Receipt is evidence, not approval."
)


def tool_repo_map(arguments: dict[str, Any]) -> dict[str, Any]:
    depth = int(arguments.get("depth", 3))
    excludes = set(DEFAULT_EXCLUDES)
    excludes.update(str(item) for item in arguments.get("exclude", []))
    entries = build_repo_map(REPO_ROOT, depth=depth, excludes=excludes)
    snapshot = build_snapshot(REPO_ROOT, depth, entries, excludes)
    return {
        "receipt_type": "repo_map",
        "root": str(REPO_ROOT),
        "entry_count": snapshot["entry_count"],
        "map_hash": snapshot["map_hash"],
        "depth": depth,
        "orientation_use": "Use this before deeper search. Repo map is orientation, not proof.",
    }


def _gate_request(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "actor_id": arguments.get("actor_id", "operator"),
        "agent_id": arguments.get("agent_id", "codex"),
        "model_id": arguments.get("model_id", "codex"),
        "provider_id": arguments.get("provider_id", "openai-codex"),
        "route_id": arguments.get("route_id", "mcp:echo-root-ve"),
        "action_lane": arguments.get("action_lane", "L2_WRITE_ANNOTATE_INDEX"),
        "requested_action": arguments.get("requested_action", ""),
        "consent_scope_present": bool(arguments.get("consent_scope_present", False)),
        "rho": float(arguments.get("rho", 0.0)),
        "delta": float(arguments.get("delta", 0.0)),
        "dry_run": bool(arguments.get("dry_run", True)),
        "confidence": arguments.get("confidence", "medium"),
        "fallback_status": arguments.get("fallback_status", "none"),
        "tool_name": arguments.get("tool_name", "mcp"),
        "files_touched": [str(item) for item in arguments.get("files_touched", [])],
        "files_created": int(arguments.get("files_created", 0)),
        "empty_folder": bool(arguments.get("empty_folder", False)),
        "context_limit_exceeded": bool(arguments.get("context_limit_exceeded", False)),
        "forbidden_action": bool(arguments.get("forbidden_action", False)),
        "identity_scope_conflict": bool(arguments.get("identity_scope_conflict", False)),
        "recursive_generation": bool(arguments.get("recursive_generation", False)),
        "failed_checks": int(arguments.get("failed_checks", 0)),
    }


def tool_gate_action(arguments: dict[str, Any]) -> dict[str, Any]:
    request = _gate_request(arguments)
    decision, reason = gate_decision(request)
    return {
        "decision": decision,
        "reason": reason,
        "rho": request["rho"],
        "delta": request["delta"],
        "requested_action": request["requested_action"],
        "boundary": "Gate posture is advice/evidence until paired with approved authority.",
    }


def tool_append_receipt(arguments: dict[str, Any]) -> dict[str, Any]:
    ledger = Path(arguments.get("ledger", DEFAULT_LEDGER))
    if not ledger.is_absolute():
        ledger = REPO_ROOT / ledger
    request = _gate_request(arguments)
    request["calibration_reason"] = arguments.get(
        "calibration_reason",
        {
            "rho": f"rho={request['rho']} supplied by MCP caller",
            "delta": f"delta={request['delta']} supplied by MCP caller",
        },
    )
    receipt = append_receipt(ledger, request)
    return {
        "ledger": str(ledger),
        "receipt_id": receipt["receipt_id"],
        "decision": receipt["decision"],
        "reason": receipt["reason"],
        "hash_self": receipt["hash_self"],
    }


def tool_verify_chain(arguments: dict[str, Any]) -> dict[str, Any]:
    ledger = Path(arguments.get("ledger", DEFAULT_LEDGER))
    if not ledger.is_absolute():
        ledger = REPO_ROOT / ledger
    ok, errors = verify_chain(ledger)
    return {"ledger": str(ledger), "ok": ok, "errors": errors}


def tool_selftest(_: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / ".codex" / "hooks" / "codex_echo_root_selftest.py")],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        parsed = {"raw_output": proc.stdout}
    return {"ok": proc.returncode == 0, "returncode": proc.returncode, "report": parsed}


def tool_live_probe(arguments: dict[str, Any]) -> dict[str, Any]:
    cmd = [sys.executable, str(REPO_ROOT / ".codex" / "hooks" / "codex_hook_live_probe.py")]
    if "before_count" in arguments:
        cmd.extend(["--before-count", str(arguments["before_count"])])
    proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        parsed = {"raw_output": proc.stdout}
    return {"ok": proc.returncode == 0, "returncode": proc.returncode, "report": parsed}


TOOLS = {
    "echo_root_repo_map": {
        "description": "Create a deterministic repo orientation receipt. Orientation is not proof.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "depth": {"type": "integer", "default": 3},
                "exclude": {"type": "array", "items": {"type": "string"}},
            },
        },
        "handler": tool_repo_map,
    },
    "echo_root_gate_action": {
        "description": "Classify a proposed action as PROCEED, PAUSE, ABORT, or SAFE_MODE using Echo Root VE gate rules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requested_action": {"type": "string"},
                "consent_scope_present": {"type": "boolean"},
                "rho": {"type": "number"},
                "delta": {"type": "number"},
                "action_lane": {"type": "string"},
                "confidence": {"type": "string"},
                "fallback_status": {"type": "string"},
                "files_touched": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["requested_action", "consent_scope_present", "rho", "delta"],
        },
        "handler": tool_gate_action,
    },
    "echo_root_append_receipt": {
        "description": "Append a local hash-chained Echo Root receipt under ve_data by default.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ledger": {"type": "string"},
                "requested_action": {"type": "string"},
                "consent_scope_present": {"type": "boolean"},
                "rho": {"type": "number"},
                "delta": {"type": "number"},
                "action_lane": {"type": "string"},
                "tool_name": {"type": "string"},
                "files_touched": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["requested_action", "consent_scope_present", "rho", "delta"],
        },
        "handler": tool_append_receipt,
    },
    "echo_root_verify_chain": {
        "description": "Verify a local Echo Root JSONL receipt chain.",
        "inputSchema": {"type": "object", "properties": {"ledger": {"type": "string"}}},
        "handler": tool_verify_chain,
    },
    "echo_root_selftest": {
        "description": "Run the Codex/Echo Root workflow self-test.",
        "inputSchema": {"type": "object", "properties": {}},
        "handler": tool_selftest,
    },
    "echo_root_live_probe": {
        "description": "Inspect whether live Codex hook receipts have appended since a previous count.",
        "inputSchema": {"type": "object", "properties": {"before_count": {"type": "integer"}}},
        "handler": tool_live_probe,
    },
}


def _tool_specs() -> list[dict[str, Any]]:
    return [
        {"name": name, "description": spec["description"], "inputSchema": spec["inputSchema"]}
        for name, spec in TOOLS.items()
    ]


def _tool_result(data: Any) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(data, indent=2, sort_keys=True)}],
        "structuredContent": data,
    }


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    msg_id = message.get("id")
    if method == "initialize":
        params = message.get("params", {})
        protocol_version = DEFAULT_PROTOCOL_VERSION
        if isinstance(params, dict):
            protocol_version = str(params.get("protocolVersion") or protocol_version)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": protocol_version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "instructions": INSTRUCTIONS,
            },
        }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    if method == "notifications/initialized":
        return None
    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"resources": []}}
    if method == "resources/templates/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"resourceTemplates": []}}
    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"prompts": []}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": _tool_specs()}}
    if method == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"unknown tool: {name}"}}
        try:
            data = TOOLS[name]["handler"](arguments if isinstance(arguments, dict) else {})
            return {"jsonrpc": "2.0", "id": msg_id, "result": _tool_result(data)}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32000, "message": str(exc)}}
    if msg_id is None:
        return None
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"unknown method: {method}"}}


def _read_content_length_message(stdin: Any) -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = stdin.buffer.readline()
        if not line:
            return None
        if line in {b"\r\n", b"\n"}:
            break
        key, _, value = line.decode("ascii", errors="replace").partition(":")
        headers[key.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    return json.loads(stdin.buffer.read(length).decode("utf-8"))


def _write_message(message: dict[str, Any]) -> None:
    body = json.dumps(message, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body)
    sys.stdout.buffer.flush()


def serve() -> int:
    while True:
        message = _read_content_length_message(sys.stdin)
        if message is None:
            return 0
        response = handle_request(message)
        if response is not None:
            _write_message(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="Echo Root VE MCP server")
    parser.add_argument("--oneshot", help="Handle one JSON request from this argument and print response JSON")
    args = parser.parse_args()
    if args.oneshot:
        response = handle_request(json.loads(args.oneshot))
        print(json.dumps(response, indent=2, sort_keys=True))
        return 0
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())
