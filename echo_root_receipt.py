from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZERO_HASH = "0" * 64
DECISIONS = {"PROCEED", "PAUSE", "ABORT", "SAFE_MODE"}
REQUIRED_RECEIPT_FIELDS = {
    "receipt_id",
    "timestamp",
    "actor_id",
    "agent_id",
    "model_id",
    "provider_id",
    "route_id",
    "action_lane",
    "requested_action",
    "consent_scope_present",
    "rho",
    "delta",
    "decision",
    "reason",
    "files_touched",
    "tool_name",
    "input_hash",
    "output_hash",
    "hash_prev",
    "hash_self",
    "replayable",
    "fallback_status",
}


@dataclass(frozen=True)
class GateConfig:
    max_files_touched_per_run: int = 5
    max_files_created_per_run: int = 3
    max_folders_touched_per_run: int = 3
    dry_run_required: bool = True
    destructive_actions_allowed: bool = False
    recursive_generation_allowed: bool = False


def canonicalize_receipt(receipt: dict[str, Any]) -> str:
    body = {key: receipt[key] for key in sorted(receipt) if key != "hash_self"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_hash(receipt: dict[str, Any]) -> str:
    return hashlib.sha256(canonicalize_receipt(receipt).encode("utf-8")).hexdigest()


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def validate_schema(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_RECEIPT_FIELDS - set(receipt))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if receipt.get("decision") not in DECISIONS:
        errors.append("decision must be PROCEED, PAUSE, ABORT, or SAFE_MODE")
    for field in ("rho", "delta"):
        value = receipt.get(field)
        if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
            errors.append(f"{field} must be a number between 0 and 1")
    for field in ("consent_scope_present", "replayable"):
        if not isinstance(receipt.get(field), bool):
            errors.append(f"{field} must be boolean")
    for field in ("reason", "files_touched"):
        if not isinstance(receipt.get(field), list):
            errors.append(f"{field} must be a list")
    for field in ("hash_prev", "hash_self"):
        value = receipt.get(field, "")
        if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            errors.append(f"{field} must be a 64 character lowercase sha256 hex string")
    if "hash_self" in receipt and receipt.get("hash_self") != compute_hash(receipt):
        errors.append("hash_self does not match canonical receipt")
    return errors


def _last_hash(path: Path) -> str:
    if not path.exists():
        return ZERO_HASH
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return ZERO_HASH
    return json.loads(rows[-1]).get("hash_self", ZERO_HASH)


def _touch_stats(files_touched: list[str]) -> tuple[int, int]:
    folders = {str(Path(item).parent) for item in files_touched if str(Path(item).parent) not in {"", "."}}
    return len(files_touched), len(folders)


def gate_decision(request: dict[str, Any], config: GateConfig | None = None, chain_valid: bool = True, policy_present: bool = True) -> tuple[str, list[str]]:
    config = config or GateConfig()
    reasons: list[str] = []
    files_touched = [str(item) for item in request.get("files_touched", [])]
    file_count, folder_count = _touch_stats(files_touched)
    created_count = int(request.get("files_created", 0))
    action = str(request.get("requested_action", "")).lower()
    action_lane = str(request.get("action_lane", "")).lower()
    fallback_status = str(request.get("fallback_status", "none")).lower()

    if not chain_valid:
        return "SAFE_MODE", ["receipt chain broken"]
    if not policy_present:
        return "SAFE_MODE", ["policy missing"]
    if fallback_status in {"unsafe", "unverified"}:
        return "SAFE_MODE", ["unsafe fallback"]
    if int(request.get("failed_checks", 0)) >= 3:
        return "SAFE_MODE", ["repeated failed checks"]

    if bool(request.get("forbidden_action", False)):
        return "ABORT", ["forbidden action"]
    if ("delete" in action or "destructive" in action_lane) and not config.destructive_actions_allowed:
        return "ABORT", ["destructive action without L3 approval"]
    if bool(request.get("identity_scope_conflict", False)):
        return "ABORT", ["identity/scope conflict"]
    if float(request.get("delta", 0.0)) > 0.40:
        return "ABORT", ["delta above abort threshold"]

    if not bool(request.get("consent_scope_present", False)):
        reasons.append("missing scope")
    if fallback_status not in {"", "none", "ok"}:
        reasons.append("route fallback occurred")
    if bool(request.get("context_limit_exceeded", False)):
        reasons.append("context limit exceeded")
    confidence = str(request.get("confidence", "")).lower()
    if confidence in {"medium", "unclear"}:
        reasons.append("confidence medium/unclear")
    if file_count > config.max_files_touched_per_run or created_count > config.max_files_created_per_run or folder_count > config.max_folders_touched_per_run:
        reasons.append("write budget exceeded")
    if bool(request.get("empty_folder", False)):
        reasons.append("empty folder / no evidence")
    if config.dry_run_required and not bool(request.get("dry_run", False)):
        reasons.append("dry_run_required")
    if not config.recursive_generation_allowed and bool(request.get("recursive_generation", False)):
        reasons.append("recursive generation blocked by default")

    if reasons:
        return "PAUSE", reasons
    if bool(request.get("consent_scope_present", False)) and float(request.get("rho", 0.0)) >= 0.70 and float(request.get("delta", 1.0)) <= 0.30:
        return "PROCEED", ["consent scope present, confidence threshold met, drift within threshold"]
    return "PAUSE", ["confidence below proceed threshold"]


def build_receipt(request: dict[str, Any], decision: str, reason: list[str], hash_prev: str) -> dict[str, Any]:
    gate_inputs = {
        "dry_run": bool(request.get("dry_run", False)),
        "empty_folder": bool(request.get("empty_folder", False)),
        "context_limit_exceeded": bool(request.get("context_limit_exceeded", False)),
        "confidence": request.get("confidence", ""),
        "files_created": int(request.get("files_created", 0)),
        "forbidden_action": bool(request.get("forbidden_action", False)),
        "identity_scope_conflict": bool(request.get("identity_scope_conflict", False)),
        "recursive_generation": bool(request.get("recursive_generation", False)),
        "failed_checks": int(request.get("failed_checks", 0)),
    }
    receipt = {
        "receipt_id": request.get("receipt_id") or str(uuid.uuid4()),
        "timestamp": request.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "actor_id": request.get("actor_id", "operator"),
        "agent_id": request.get("agent_id", "echo-root-ve"),
        "model_id": request.get("model_id", "local-demo"),
        "provider_id": request.get("provider_id", "local"),
        "route_id": request.get("route_id", "demo-route"),
        "action_lane": request.get("action_lane", "L1_READ_CLASSIFY"),
        "requested_action": request.get("requested_action", ""),
        "consent_scope_present": bool(request.get("consent_scope_present", False)),
        "rho": float(request.get("rho", 0.0)),
        "delta": float(request.get("delta", 0.0)),
        "decision": decision,
        "reason": reason,
        "files_touched": [str(item) for item in request.get("files_touched", [])],
        "tool_name": request.get("tool_name", ""),
        "input_hash": request.get("input_hash") or stable_hash(request.get("input", request.get("requested_action", ""))),
        "output_hash": request.get("output_hash") or stable_hash({"decision": decision, "reason": reason}),
        "hash_prev": hash_prev,
        "hash_self": ZERO_HASH,
        "replayable": True,
        "fallback_status": request.get("fallback_status", "none"),
        "gate_inputs": gate_inputs,
    }
    receipt["hash_self"] = compute_hash(receipt)
    return receipt


def append_receipt(path: Path, request: dict[str, Any], config: GateConfig | None = None, chain_valid: bool = True, policy_present: bool = True) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    decision, reason = gate_decision(request, config=config, chain_valid=chain_valid, policy_present=policy_present)
    receipt = build_receipt(request, decision, reason, _last_hash(path))
    errors = validate_schema(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt


def verify_chain(path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    expected_prev = ZERO_HASH
    if not path.exists():
        return True, []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                receipt = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue
            if receipt.get("hash_prev") != expected_prev:
                errors.append(f"line {line_number}: hash_prev mismatch")
            schema_errors = validate_schema(receipt)
            errors.extend(f"line {line_number}: {item}" for item in schema_errors)
            expected_prev = receipt.get("hash_self", ZERO_HASH)
    return not errors, errors


def replay_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    gate_inputs = dict(receipt.get("gate_inputs", {}))
    replay_request = {
        "requested_action": receipt.get("requested_action", ""),
        "action_lane": receipt.get("action_lane", ""),
        "consent_scope_present": receipt.get("consent_scope_present", False),
        "rho": receipt.get("rho", 0.0),
        "delta": receipt.get("delta", 0.0),
        "files_touched": receipt.get("files_touched", []),
        "fallback_status": receipt.get("fallback_status", "none"),
        "dry_run": True,
    }
    replay_request.update(gate_inputs)
    decision, reason = gate_decision(replay_request)
    return {
        "receipt_id": receipt.get("receipt_id", ""),
        "original_decision": receipt.get("decision", ""),
        "replay_decision": decision,
        "replay_reason": reason,
        "matches": decision == receipt.get("decision"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Echo Root VE receipt gate and replay")
    parser.add_argument("--ledger", default="receipts/demo_receipts.jsonl")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--scenario", choices=["proceed", "pause", "abort"], default="proceed")
    sub.add_parser("verify")
    sub.add_parser("replay")
    args = parser.parse_args()
    ledger = Path(args.ledger)

    if args.command == "demo":
        scenarios = {
            "proceed": {
                "requested_action": "summarize local release evidence",
                "action_lane": "L1_READ_CLASSIFY",
                "consent_scope_present": True,
                "rho": 0.82,
                "delta": 0.12,
                "dry_run": True,
                "tool_name": "demo_agent",
            },
            "pause": {
                "requested_action": "write release notes from empty folder",
                "action_lane": "L2_WRITE_ANNOTATE_INDEX",
                "consent_scope_present": True,
                "rho": 0.74,
                "delta": 0.18,
                "dry_run": True,
                "empty_folder": True,
                "tool_name": "demo_agent",
            },
            "abort": {
                "requested_action": "delete project folder",
                "action_lane": "L3_REMOVE_DELETE_RESTRUCTURE",
                "consent_scope_present": True,
                "rho": 0.81,
                "delta": 0.11,
                "dry_run": True,
                "tool_name": "demo_agent",
            },
        }
        print(json.dumps(append_receipt(ledger, scenarios[args.scenario]), indent=2))
        return 0
    if args.command == "verify":
        ok, errors = verify_chain(ledger)
        print(json.dumps({"ok": ok, "errors": errors}, indent=2))
        return 0 if ok else 1
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps([replay_receipt(item) for item in rows], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
