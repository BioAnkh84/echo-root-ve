from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZERO_HASH = "0" * 64
DECISIONS = {"PROCEED", "PAUSE", "ABORT", "SAFE_MODE"}

AUTONOMY_LEVELS = {
    "L0_CHAT_ONLY",
    "L1_SUGGEST",
    "L2_PREPARE",
    "L3_READ_ONLY_CHECK",
    "L4_BOUNDED_WRITE",
    "L5_SUPERVISED_EPISODE",
    "L6_SAFE_MODE",
}

LEVEL_RANK = {
    "L0_CHAT_ONLY": 0,
    "L1_SUGGEST": 1,
    "L2_PREPARE": 2,
    "L3_READ_ONLY_CHECK": 3,
    "L4_BOUNDED_WRITE": 4,
    "L5_SUPERVISED_EPISODE": 5,
    "L6_SAFE_MODE": 6,
}

LANE_REQUIRED_LEVEL = {
    "chat": "L0_CHAT_ONLY",
    "suggest": "L1_SUGGEST",
    "prepare": "L2_PREPARE",
    "draft": "L2_PREPARE",
    "read": "L3_READ_ONLY_CHECK",
    "read_only": "L3_READ_ONLY_CHECK",
    "write": "L4_BOUNDED_WRITE",
    "bounded_write": "L4_BOUNDED_WRITE",
    "supervised_episode": "L5_SUPERVISED_EPISODE",
    "safe_mode": "L6_SAFE_MODE",
}

POLICY_THRESHOLDS = {
    "low": {"rho": 0.70, "delta": 0.30},
    "standard": {"rho": 0.75, "delta": 0.25},
    "elevated": {"rho": 0.82, "delta": 0.20},
}


@dataclass(frozen=True)
class AutonomyCharter:
    allowed_actions: tuple[str, ...] = ("suggest", "prepare", "read_only")
    blocked_actions: tuple[str, ...] = ("delete", "external_action", "memory_mutation")
    max_time_horizon: str = "one_turn"
    max_action_count: int = 1
    max_files_touched: int = 0
    allowed_tools: tuple[str, ...] = ("none",)
    blocked_tools: tuple[str, ...] = ("network", "delete", "memory")
    review_interval: str = "after_each_action"
    pause_triggers: tuple[str, ...] = ("permission_requested", "unclear_scope")
    abort_triggers: tuple[str, ...] = ("gate_bypass", "forbidden_tool")
    receipt_required: bool = True
    authority_level: str = "L1"
    escalation_path: str = "operator_review"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AutonomyCharter | None":
        if data is None:
            return None
        fields = {}
        for key in cls.__dataclass_fields__:
            if key not in data:
                continue
            value = data[key]
            if key.endswith("actions") or key.endswith("tools") or key.endswith("triggers"):
                fields[key] = tuple(str(item) for item in value)
            else:
                fields[key] = value
        return cls(**fields)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def canonicalize_self_proposal(receipt: dict[str, Any]) -> str:
    body = {key: receipt[key] for key in sorted(receipt) if key != "hash_self"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_hash(receipt: dict[str, Any]) -> str:
    return hashlib.sha256(canonicalize_self_proposal(receipt).encode("utf-8")).hexdigest()


def _last_hash(path: Path) -> str:
    if not path.exists():
        return ZERO_HASH
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return ZERO_HASH
    return json.loads(rows[-1]).get("hash_self", ZERO_HASH)


def create_self_proposal(**kwargs: Any) -> dict[str, Any]:
    proposal = {
        "proposal_id": kwargs.get("proposal_id") or str(uuid.uuid4()),
        "timestamp": kwargs.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "agent_id": kwargs.get("agent_id", "echo-root-ve"),
        "operator_id": kwargs.get("operator_id", "operator"),
        "autonomy_level": kwargs.get("autonomy_level", "L1_SUGGEST"),
        "proposed_action": kwargs.get("proposed_action", ""),
        "rationale": kwargs.get("rationale", ""),
        "expected_benefit": kwargs.get("expected_benefit", ""),
        "action_lane": kwargs.get("action_lane", "suggest"),
        "requested_authority": kwargs.get("requested_authority", "L1"),
        "policy_tier": kwargs.get("policy_tier", "low"),
        "consent_scope_present": bool(kwargs.get("consent_scope_present", False)),
        "rho": float(kwargs.get("rho", 0.0)),
        "delta": float(kwargs.get("delta", 0.0)),
        "risk_summary": kwargs.get("risk_summary", ""),
        "expected_files_touched": [str(item) for item in kwargs.get("expected_files_touched", [])],
        "expected_tools": [str(item) for item in kwargs.get("expected_tools", [])],
        "stop_condition": kwargs.get("stop_condition", ""),
        "review_interval": kwargs.get("review_interval", ""),
        "receipt_required": bool(kwargs.get("receipt_required", True)),
        "decision": kwargs.get("decision", ""),
        "decision_reason": list(kwargs.get("decision_reason", [])),
        "calibration_reason": kwargs.get("calibration_reason", ""),
        "hash_prev": kwargs.get("hash_prev", ZERO_HASH),
        "hash_self": kwargs.get("hash_self", ZERO_HASH),
    }
    optional_fields = [
        "permission_requested",
        "route_fallback",
        "context_limit_exceeded",
        "medium_confidence",
        "requested_authority_increased",
        "destructive_action",
        "external_action",
        "memory_mutation",
        "identity_scope_conflict",
        "gate_bypass_attempt",
        "repeated_proposal_count",
        "receipt_chain_valid",
        "policy_present",
        "unsafe_fallback",
        "sandbox_compromised",
        "authority_escalation_attempts",
        "files_touched_actual",
        "tool_actual",
        "model_id",
        "provider_id",
        "route_id",
    ]
    for field in optional_fields:
        if field in kwargs:
            proposal[field] = kwargs[field]
    return proposal


def _rank(level: str) -> int:
    return LEVEL_RANK.get(level, -1)


def _thresholds(policy_tier: str) -> dict[str, float]:
    return POLICY_THRESHOLDS.get(policy_tier, POLICY_THRESHOLDS["standard"])


def _difference(rule_id: str, category: str, severity: str, rho_delta: float, delta_delta: float, decision: str) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "rho_delta": rho_delta,
        "delta_delta": delta_delta,
        "decision": decision,
    }


def classify_self_proposal(proposal: dict[str, Any], charter: AutonomyCharter | None) -> dict[str, Any]:
    lane = str(proposal.get("action_lane", "")).lower()
    autonomy_level = str(proposal.get("autonomy_level", ""))
    requested_authority = str(proposal.get("requested_authority", ""))
    expected_tools = [str(item) for item in proposal.get("expected_tools", [])]
    expected_files = [str(item) for item in proposal.get("expected_files_touched", [])]
    required_level = LANE_REQUIRED_LEVEL.get(lane, "L4_BOUNDED_WRITE")
    return {
        "lane": lane,
        "autonomy_level": autonomy_level,
        "requested_authority": requested_authority,
        "expected_tools": expected_tools,
        "expected_files": expected_files,
        "required_level": required_level,
        "level_allows_lane": _rank(autonomy_level) >= _rank(required_level) and autonomy_level != "L6_SAFE_MODE",
        "charter_present": charter is not None,
    }


def evaluate_self_proposal_gate(
    proposal: dict[str, Any],
    charter: AutonomyCharter | dict[str, Any] | None = None,
    *,
    receipt_chain_valid: bool = True,
    policy_present: bool = True,
) -> tuple[str, list[str], list[dict[str, Any]], str]:
    resolved_charter = charter if isinstance(charter, AutonomyCharter) else AutonomyCharter.from_dict(charter)
    classification = classify_self_proposal(proposal, resolved_charter)
    reasons: list[str] = []
    makers: list[dict[str, Any]] = []
    policy_tier = str(proposal.get("policy_tier", "standard"))
    thresholds = _thresholds(policy_tier)
    lane = classification["lane"]
    tools = classification["expected_tools"]
    files = classification["expected_files"]

    chain_valid = bool(proposal.get("receipt_chain_valid", receipt_chain_valid))
    policy_ok = bool(proposal.get("policy_present", policy_present))
    repeated_count = int(proposal.get("repeated_proposal_count", 0))
    escalation_attempts = int(proposal.get("authority_escalation_attempts", 0))

    if not chain_valid:
        makers.append(_difference("receipt_chain_broken", "governance_substrate", "high", -0.30, 0.40, "SAFE_MODE"))
        return "SAFE_MODE", ["receipt chain broken"], makers, "rho/delta unreliable because receipt chain is broken"
    if not policy_ok:
        makers.append(_difference("policy_missing", "governance_substrate", "high", -0.25, 0.35, "SAFE_MODE"))
        return "SAFE_MODE", ["policy missing"], makers, "rho/delta unreliable because policy is missing"
    if repeated_count >= 3:
        makers.append(_difference("repeated_self_proposal_loop", "loop_control", "high", -0.20, 0.35, "SAFE_MODE"))
        return "SAFE_MODE", ["repeated proposal loop"], makers, "delta increased because proposal loop repeated without resolution"
    if bool(proposal.get("unsafe_fallback", False)):
        makers.append(_difference("unsafe_fallback", "route_integrity", "high", -0.20, 0.35, "SAFE_MODE"))
        return "SAFE_MODE", ["unsafe fallback"], makers, "delta increased because fallback route is unsafe"
    if bool(proposal.get("sandbox_compromised", False)):
        makers.append(_difference("tool_sandbox_compromised", "tool_integrity", "critical", -0.40, 0.50, "SAFE_MODE"))
        return "SAFE_MODE", ["tool sandbox compromised"], makers, "rho collapsed because tool sandbox integrity is compromised"
    if escalation_attempts >= 2:
        makers.append(_difference("repeated_authority_escalation", "authority_boundary", "high", -0.20, 0.35, "SAFE_MODE"))
        return "SAFE_MODE", ["proposal attempts authority escalation repeatedly"], makers, "delta increased because authority escalation repeated"

    if bool(proposal.get("gate_bypass_attempt", False)):
        makers.append(_difference("gate_bypass_attempt", "gate_integrity", "critical", -0.40, 0.50, "ABORT"))
        return "ABORT", ["action attempts to bypass gate"], makers, "rho collapsed because proposal attempted to bypass gate"
    if bool(proposal.get("destructive_action", False)):
        makers.append(_difference("destructive_without_explicit_approval", "authority_boundary", "high", -0.25, 0.35, "ABORT"))
        return "ABORT", ["destructive action requested without approval"], makers, "delta increased because destructive action lacks explicit approval"
    if bool(proposal.get("external_action", False)):
        makers.append(_difference("external_action_without_explicit_approval", "external_boundary", "high", -0.25, 0.35, "ABORT"))
        return "ABORT", ["external action requested without explicit approval"], makers, "delta increased because external action lacks explicit approval"
    if bool(proposal.get("memory_mutation", False)) and not bool(proposal.get("receipt_required", False)):
        makers.append(_difference("memory_mutation_without_receipt", "memory_boundary", "high", -0.25, 0.35, "ABORT"))
        return "ABORT", ["memory mutation requested without receipt"], makers, "delta increased because memory mutation lacks receipt path"
    if bool(proposal.get("identity_scope_conflict", False)):
        makers.append(_difference("identity_scope_conflict", "identity_scope", "high", -0.25, 0.35, "ABORT"))
        return "ABORT", ["identity/scope conflict"], makers, "delta increased because identity and scope conflict"
    if float(proposal.get("delta", 0.0)) > 0.40:
        makers.append(_difference("delta_above_abort_threshold", "risk_drift", "high", -0.15, 0.25, "ABORT"))
        return "ABORT", ["delta above abort threshold"], makers, "delta above 0.40 abort threshold"

    if resolved_charter is None:
        reasons.append("missing charter")
        makers.append(_difference("missing_charter", "scope_boundary", "medium", -0.10, 0.12, "PAUSE"))
    else:
        if lane not in resolved_charter.allowed_actions:
            reasons.append("requested action outside charter")
            makers.append(_difference("lane_outside_charter", "scope_boundary", "medium", -0.08, 0.10, "PAUSE"))
        if len(files) > int(resolved_charter.max_files_touched):
            makers.append(_difference("file_budget_exceeded", "write_budget", "high", -0.20, 0.30, "ABORT"))
            return "ABORT", ["file budget exceeded"], makers, "delta increased because bounded proposal exceeded its file budget"
        forbidden_tools = sorted(set(tools).intersection(set(resolved_charter.blocked_tools)))
        if forbidden_tools:
            return "ABORT", ["forbidden tool"], [
                _difference("forbidden_tool", "tool_boundary", "high", -0.25, 0.35, "ABORT")
            ], "delta increased because proposal requested a forbidden tool"
        if tools and "none" not in resolved_charter.allowed_tools:
            disallowed_tools = sorted(set(tools).difference(set(resolved_charter.allowed_tools)))
            if disallowed_tools:
                reasons.append("requested tool outside charter")
                makers.append(_difference("tool_outside_charter", "tool_boundary", "medium", -0.08, 0.10, "PAUSE"))

    if bool(proposal.get("permission_requested", False)):
        reasons.append("permission requested")
        makers.append(_difference("permission_implies_authority_context_changed", "authority_boundary", "medium", -0.07, 0.10, "PAUSE"))
    if not bool(proposal.get("consent_scope_present", False)):
        reasons.append("unclear scope")
        makers.append(_difference("missing_consent_scope", "scope_boundary", "medium", -0.10, 0.12, "PAUSE"))
    if not classification["level_allows_lane"]:
        reasons.append("autonomy level does not allow proposed lane")
        makers.append(_difference("autonomy_level_below_lane", "autonomy_boundary", "medium", -0.10, 0.12, "PAUSE"))
    if not str(proposal.get("stop_condition", "")).strip():
        reasons.append("unclear stop condition")
        makers.append(_difference("missing_stop_condition", "loop_control", "medium", -0.07, 0.10, "PAUSE"))
    if str(proposal.get("autonomy_level", "")) == "L5_SUPERVISED_EPISODE" and not str(proposal.get("review_interval", "")).strip():
        reasons.append("missing review interval")
        makers.append(_difference("missing_review_interval", "loop_control", "medium", -0.07, 0.10, "PAUSE"))
    if bool(proposal.get("route_fallback", False)):
        reasons.append("route fallback occurred")
        makers.append(_difference("route_fallback", "route_integrity", "medium", -0.08, 0.12, "PAUSE"))
    if bool(proposal.get("context_limit_exceeded", False)):
        reasons.append("context limit exceeded")
        makers.append(_difference("context_limit_exceeded", "context_boundary", "medium", -0.08, 0.12, "PAUSE"))
    if bool(proposal.get("medium_confidence", False)):
        reasons.append("medium confidence")
        makers.append(_difference("medium_confidence", "confidence", "medium", -0.06, 0.08, "PAUSE"))
    if bool(proposal.get("requested_authority_increased", False)):
        reasons.append("requested authority increased")
        makers.append(_difference("authority_increase_requested", "authority_boundary", "medium", -0.08, 0.12, "PAUSE"))
    if not bool(proposal.get("receipt_required", False)):
        reasons.append("receipt path unavailable")
        makers.append(_difference("receipt_path_unavailable", "receipt_boundary", "medium", -0.08, 0.12, "PAUSE"))

    if reasons:
        return "PAUSE", reasons, makers, "rho/delta downgraded because " + "; ".join(item["rule_id"] for item in makers)

    if float(proposal.get("rho", 0.0)) >= thresholds["rho"] and float(proposal.get("delta", 1.0)) <= thresholds["delta"]:
        makers.append(_difference("scope_confidence_and_drift_within_policy", "evidence_quality", "low", 0.05, -0.05, "PROCEED"))
        return "PROCEED", ["bounded proposal within charter and policy thresholds"], makers, (
            f"rho={proposal.get('rho')} >= {thresholds['rho']} and "
            f"delta={proposal.get('delta')} <= {thresholds['delta']} for {policy_tier} policy tier"
        )
    makers.append(_difference("policy_threshold_not_met", "evidence_quality", "medium", -0.08, 0.08, "PAUSE"))
    return "PAUSE", ["policy threshold not met"], makers, "rho/delta did not meet policy tier thresholds"


def _build_receipt(
    proposal: dict[str, Any],
    decision: str,
    reason: list[str],
    makers: list[dict[str, Any]],
    calibration_reason: str,
    hash_prev: str,
) -> dict[str, Any]:
    receipt = dict(proposal)
    receipt.update(
        {
            "event_type": "self_proposal_gate",
            "decision": decision,
            "decision_reason": reason,
            "difference_makers": makers,
            "calibration_reason": calibration_reason,
            "gamma0": bool(proposal.get("consent_scope_present", False)),
            "files_expected": [str(item) for item in proposal.get("expected_files_touched", [])],
            "files_touched_actual": [str(item) for item in proposal.get("files_touched_actual", [])],
            "tool_expected": [str(item) for item in proposal.get("expected_tools", [])],
            "tool_actual": [str(item) for item in proposal.get("tool_actual", [])],
            "operator_review_required": decision != "PROCEED",
            "route_id": proposal.get("route_id", "self-proposal-local"),
            "model_id": proposal.get("model_id", "local-demo"),
            "provider_id": proposal.get("provider_id", "local"),
            "replayable": True,
            "hash_prev": hash_prev,
            "hash_self": ZERO_HASH,
        }
    )
    receipt["hash_self"] = compute_hash(receipt)
    return receipt


def approve_bounded_proposal(proposal: dict[str, Any], charter: AutonomyCharter | dict[str, Any]) -> dict[str, Any]:
    decision, reason, makers, calibration = evaluate_self_proposal_gate(proposal, charter)
    if decision != "PROCEED":
        raise ValueError("proposal did not proceed: " + "; ".join(reason))
    return _build_receipt(proposal, decision, reason, makers, calibration, proposal.get("hash_prev", ZERO_HASH))


def pause_self_proposal(proposal: dict[str, Any], reason: list[str] | None = None) -> dict[str, Any]:
    return _build_receipt(proposal, "PAUSE", reason or ["operator review required"], [], "manual pause", proposal.get("hash_prev", ZERO_HASH))


def abort_self_proposal(proposal: dict[str, Any], reason: list[str] | None = None) -> dict[str, Any]:
    return _build_receipt(proposal, "ABORT", reason or ["operator aborted proposal"], [], "manual abort", proposal.get("hash_prev", ZERO_HASH))


def validate_self_proposal_schema(receipt: dict[str, Any]) -> list[str]:
    required = {
        "proposal_id",
        "timestamp",
        "agent_id",
        "operator_id",
        "autonomy_level",
        "proposed_action",
        "rationale",
        "expected_benefit",
        "action_lane",
        "requested_authority",
        "policy_tier",
        "consent_scope_present",
        "rho",
        "delta",
        "risk_summary",
        "expected_files_touched",
        "expected_tools",
        "stop_condition",
        "review_interval",
        "receipt_required",
        "decision",
        "decision_reason",
        "calibration_reason",
        "hash_prev",
        "hash_self",
    }
    errors: list[str] = []
    missing = sorted(required - set(receipt))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if receipt.get("decision") not in DECISIONS:
        errors.append("decision must be PROCEED, PAUSE, ABORT, or SAFE_MODE")
    if receipt.get("autonomy_level") not in AUTONOMY_LEVELS:
        errors.append("autonomy_level is not recognized")
    for field in ("rho", "delta"):
        value = receipt.get(field)
        if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
            errors.append(f"{field} must be a number between 0 and 1")
    for field in ("expected_files_touched", "expected_tools", "decision_reason"):
        if not isinstance(receipt.get(field), list):
            errors.append(f"{field} must be a list")
    if not str(receipt.get("calibration_reason", "")).strip():
        errors.append("calibration_reason is required")
    for field in ("hash_prev", "hash_self"):
        value = receipt.get(field, "")
        if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            errors.append(f"{field} must be a 64 character lowercase sha256 hex string")
    if "hash_self" in receipt and receipt.get("hash_self") != compute_hash(receipt):
        errors.append("hash_self does not match canonical self-proposal receipt")
    return errors


def write_self_proposal_receipt(
    path: Path,
    proposal: dict[str, Any],
    charter: AutonomyCharter | dict[str, Any] | None = None,
    *,
    receipt_chain_valid: bool = True,
    policy_present: bool = True,
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    decision, reason, makers, calibration = evaluate_self_proposal_gate(
        proposal,
        charter,
        receipt_chain_valid=receipt_chain_valid,
        policy_present=policy_present,
    )
    receipt = _build_receipt(proposal, decision, reason, makers, calibration, _last_hash(path))
    errors = validate_self_proposal_schema(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt
