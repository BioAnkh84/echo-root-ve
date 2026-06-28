from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from math import hypot
from pathlib import Path
from typing import Any


ZERO_HASH = "0" * 64
DECISIONS = {"PROCEED", "PAUSE", "ABORT", "SAFE_MODE"}


@dataclass(frozen=True)
class OperationalEnvelope:
    envelope_id: str
    authority_id: str
    center_x: float
    center_y: float
    radius_m: float
    min_altitude_m: float = 0.0
    max_altitude_m: float = 120.0
    max_speed_mps: float = 8.0
    min_human_distance_m: float = 10.0
    receipt_required: bool = True
    authority_transfer_allowed: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "OperationalEnvelope | None":
        if data is None:
            return None
        return cls(
            envelope_id=str(data.get("envelope_id", "")),
            authority_id=str(data.get("authority_id", "")),
            center_x=float(data.get("center_x", 0.0)),
            center_y=float(data.get("center_y", 0.0)),
            radius_m=float(data.get("radius_m", 0.0)),
            min_altitude_m=float(data.get("min_altitude_m", 0.0)),
            max_altitude_m=float(data.get("max_altitude_m", 120.0)),
            max_speed_mps=float(data.get("max_speed_mps", 8.0)),
            min_human_distance_m=float(data.get("min_human_distance_m", 10.0)),
            receipt_required=bool(data.get("receipt_required", True)),
            authority_transfer_allowed=bool(data.get("authority_transfer_allowed", False)),
        )


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def canonicalize_spatial_receipt(receipt: dict[str, Any]) -> str:
    body = {key: receipt[key] for key in sorted(receipt) if key != "hash_self"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_hash(receipt: dict[str, Any]) -> str:
    return hashlib.sha256(canonicalize_spatial_receipt(receipt).encode("utf-8")).hexdigest()


def _last_hash(path: Path) -> str:
    if not path.exists():
        return ZERO_HASH
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return ZERO_HASH
    return json.loads(rows[-1]).get("hash_self", ZERO_HASH)


def create_spatial_event(**kwargs: Any) -> dict[str, Any]:
    return {
        "event_id": kwargs.get("event_id") or str(uuid.uuid4()),
        "timestamp": kwargs.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "agent_id": kwargs.get("agent_id", "spatial-adapter"),
        "operator_id": kwargs.get("operator_id", "operator"),
        "vehicle_id": kwargs.get("vehicle_id", "vehicle-demo"),
        "mission_id": kwargs.get("mission_id", "mission-demo"),
        "envelope_id": kwargs.get("envelope_id", ""),
        "authority_id": kwargs.get("authority_id", ""),
        "position": dict(kwargs.get("position", {"x": 0.0, "y": 0.0, "altitude_m": 0.0})),
        "velocity_mps": float(kwargs.get("velocity_mps", 0.0)),
        "nearest_human_distance_m": kwargs.get("nearest_human_distance_m"),
        "zone_authorized": bool(kwargs.get("zone_authorized", False)),
        "authority_transfer_requested": bool(kwargs.get("authority_transfer_requested", False)),
        "authority_transfer_receipt_present": bool(kwargs.get("authority_transfer_receipt_present", False)),
        "sensor_confidence": float(kwargs.get("sensor_confidence", 0.0)),
        "rho": float(kwargs.get("rho", 0.0)),
        "delta": float(kwargs.get("delta", 0.0)),
        "route_id": kwargs.get("route_id", "spatial-governance-local"),
        "model_id": kwargs.get("model_id", "local-demo"),
        "provider_id": kwargs.get("provider_id", "local"),
        "decision": kwargs.get("decision", ""),
        "decision_reason": list(kwargs.get("decision_reason", [])),
        "difference_makers": list(kwargs.get("difference_makers", [])),
        "calibration_reason": kwargs.get("calibration_reason", ""),
        "hash_prev": kwargs.get("hash_prev", ZERO_HASH),
        "hash_self": kwargs.get("hash_self", ZERO_HASH),
        "receipt_required": bool(kwargs.get("receipt_required", True)),
        "receipt_chain_valid": bool(kwargs.get("receipt_chain_valid", True)),
        "policy_present": bool(kwargs.get("policy_present", True)),
        "unsafe_fallback": bool(kwargs.get("unsafe_fallback", False)),
        "gate_bypass_attempt": bool(kwargs.get("gate_bypass_attempt", False)),
        "external_action_requested": bool(kwargs.get("external_action_requested", False)),
        "actuator_command_requested": bool(kwargs.get("actuator_command_requested", False)),
    }


def _distance_from_center(event: dict[str, Any], envelope: OperationalEnvelope) -> float:
    position = event.get("position", {})
    return hypot(float(position.get("x", 0.0)) - envelope.center_x, float(position.get("y", 0.0)) - envelope.center_y)


def _difference(rule_id: str, category: str, severity: str, rho_delta: float, delta_delta: float, decision: str) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "rho_delta": rho_delta,
        "delta_delta": delta_delta,
        "decision": decision,
    }


def classify_spatial_event(event: dict[str, Any], envelope: OperationalEnvelope | dict[str, Any] | None) -> dict[str, Any]:
    resolved = envelope if isinstance(envelope, OperationalEnvelope) else OperationalEnvelope.from_dict(envelope)
    if resolved is None:
        return {
            "envelope_present": False,
            "inside_envelope": False,
            "altitude_in_bounds": False,
            "speed_in_bounds": False,
            "proximity_in_bounds": False,
            "distance_from_center_m": None,
        }
    altitude = float(event.get("position", {}).get("altitude_m", 0.0))
    nearest_human = event.get("nearest_human_distance_m")
    distance = _distance_from_center(event, resolved)
    return {
        "envelope_present": True,
        "inside_envelope": distance <= resolved.radius_m,
        "altitude_in_bounds": resolved.min_altitude_m <= altitude <= resolved.max_altitude_m,
        "speed_in_bounds": float(event.get("velocity_mps", 0.0)) <= resolved.max_speed_mps,
        "proximity_in_bounds": nearest_human is None or float(nearest_human) >= resolved.min_human_distance_m,
        "distance_from_center_m": round(distance, 3),
    }


def evaluate_spatial_gate(
    event: dict[str, Any],
    envelope: OperationalEnvelope | dict[str, Any] | None,
    *,
    receipt_chain_valid: bool = True,
    policy_present: bool = True,
) -> tuple[str, list[str], list[dict[str, Any]], str]:
    resolved = envelope if isinstance(envelope, OperationalEnvelope) else OperationalEnvelope.from_dict(envelope)
    classification = classify_spatial_event(event, resolved)
    makers: list[dict[str, Any]] = []
    reasons: list[str] = []
    chain_valid = bool(event.get("receipt_chain_valid", receipt_chain_valid))
    policy_ok = bool(event.get("policy_present", policy_present))

    if not chain_valid:
        makers.append(_difference("receipt_chain_broken", "governance_substrate", "high", -0.30, 0.40, "SAFE_MODE"))
        return "SAFE_MODE", ["receipt chain broken"], makers, "rho/delta unreliable because receipt chain is broken"
    if not policy_ok:
        makers.append(_difference("policy_missing", "governance_substrate", "high", -0.25, 0.35, "SAFE_MODE"))
        return "SAFE_MODE", ["policy missing"], makers, "rho/delta unreliable because policy is missing"
    if bool(event.get("unsafe_fallback", False)):
        makers.append(_difference("unsafe_fallback", "route_integrity", "high", -0.20, 0.35, "SAFE_MODE"))
        return "SAFE_MODE", ["unsafe fallback"], makers, "delta increased because fallback route is unsafe"

    if bool(event.get("gate_bypass_attempt", False)):
        makers.append(_difference("gate_bypass_attempt", "gate_integrity", "critical", -0.40, 0.50, "ABORT"))
        return "ABORT", ["action attempts to bypass gate"], makers, "rho collapsed because event attempted to bypass gate"
    if bool(event.get("external_action_requested", False)) or bool(event.get("actuator_command_requested", False)):
        makers.append(_difference("actuation_requested", "actuator_boundary", "critical", -0.40, 0.50, "ABORT"))
        return "ABORT", ["adapter cannot issue physical action"], makers, "delta increased because governance adapter cannot command actuators"
    if float(event.get("delta", 0.0)) > 0.40:
        makers.append(_difference("delta_above_abort_threshold", "risk_drift", "high", -0.15, 0.25, "ABORT"))
        return "ABORT", ["delta above abort threshold"], makers, "delta above 0.40 abort threshold"

    if resolved is None:
        reasons.append("missing operational envelope")
        makers.append(_difference("missing_envelope", "scope_boundary", "medium", -0.10, 0.12, "PAUSE"))
    if not bool(event.get("zone_authorized", False)):
        reasons.append("zone authorization missing")
        makers.append(_difference("zone_authorization_missing", "authority_boundary", "medium", -0.10, 0.12, "PAUSE"))
    if resolved is not None and str(event.get("authority_id", "")) != resolved.authority_id:
        reasons.append("authority mismatch")
        makers.append(_difference("authority_mismatch", "authority_boundary", "high", -0.14, 0.18, "PAUSE"))
    if resolved is not None and not classification["inside_envelope"]:
        reasons.append("outside operational envelope")
        makers.append(_difference("outside_envelope", "spatial_boundary", "high", -0.15, 0.22, "PAUSE"))
    if resolved is not None and not classification["altitude_in_bounds"]:
        reasons.append("altitude outside envelope")
        makers.append(_difference("altitude_outside_envelope", "spatial_boundary", "high", -0.12, 0.18, "PAUSE"))
    if resolved is not None and not classification["speed_in_bounds"]:
        reasons.append("speed outside envelope")
        makers.append(_difference("speed_outside_envelope", "spatial_boundary", "medium", -0.08, 0.12, "PAUSE"))
    if resolved is not None and not classification["proximity_in_bounds"]:
        reasons.append("proximity breach")
        makers.append(_difference("proximity_breach", "human_safety_boundary", "high", -0.18, 0.25, "PAUSE"))
    if bool(event.get("authority_transfer_requested", False)):
        if resolved is None or not resolved.authority_transfer_allowed or not bool(event.get("authority_transfer_receipt_present", False)):
            reasons.append("authority transfer requires receipt")
            makers.append(_difference("authority_transfer_without_receipt", "authority_boundary", "high", -0.14, 0.18, "PAUSE"))
    if not bool(event.get("receipt_required", True)):
        reasons.append("receipt path unavailable")
        makers.append(_difference("receipt_path_unavailable", "receipt_boundary", "medium", -0.08, 0.12, "PAUSE"))
    if float(event.get("sensor_confidence", 0.0)) < 0.70:
        reasons.append("sensor confidence below threshold")
        makers.append(_difference("low_sensor_confidence", "evidence_quality", "medium", -0.08, 0.10, "PAUSE"))

    if reasons:
        return "PAUSE", reasons, makers, "rho/delta downgraded because " + "; ".join(item["rule_id"] for item in makers)

    if float(event.get("rho", 0.0)) >= 0.70 and float(event.get("delta", 1.0)) <= 0.30:
        makers.append(_difference("authorized_envelope_within_thresholds", "evidence_quality", "low", 0.05, -0.05, "PROCEED"))
        return "PROCEED", ["authorized envelope posture within thresholds"], makers, "rho/delta within spatial governance thresholds"

    makers.append(_difference("spatial_threshold_not_met", "evidence_quality", "medium", -0.08, 0.08, "PAUSE"))
    return "PAUSE", ["spatial governance threshold not met"], makers, "rho/delta did not meet spatial governance thresholds"


def _build_receipt(
    event: dict[str, Any],
    envelope: OperationalEnvelope | None,
    decision: str,
    reason: list[str],
    makers: list[dict[str, Any]],
    calibration_reason: str,
    hash_prev: str,
) -> dict[str, Any]:
    classification = classify_spatial_event(event, envelope)
    receipt = dict(event)
    receipt.update(
        {
            "event_type": "spatial_governance_gate",
            "decision": decision,
            "decision_reason": reason,
            "difference_makers": makers,
            "calibration_reason": calibration_reason,
            "classification": classification,
            "envelope": envelope.__dict__ if envelope is not None else None,
            "operator_review_required": decision != "PROCEED",
            "replayable": True,
            "hash_prev": hash_prev,
            "hash_self": ZERO_HASH,
            "boundary": "Spatial governance evaluates authority and envelope posture only. It does not navigate, avoid collisions, or command actuators.",
        }
    )
    receipt["hash_self"] = compute_hash(receipt)
    return receipt


def validate_spatial_receipt(receipt: dict[str, Any]) -> list[str]:
    required = {
        "event_id",
        "timestamp",
        "agent_id",
        "operator_id",
        "vehicle_id",
        "mission_id",
        "envelope_id",
        "authority_id",
        "position",
        "velocity_mps",
        "zone_authorized",
        "sensor_confidence",
        "rho",
        "delta",
        "decision",
        "decision_reason",
        "difference_makers",
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
    for field in ("rho", "delta", "sensor_confidence", "velocity_mps"):
        value = receipt.get(field)
        if not isinstance(value, (int, float)) or float(value) < 0:
            errors.append(f"{field} must be a non-negative number")
    if float(receipt.get("rho", 0.0)) > 1 or float(receipt.get("delta", 0.0)) > 1 or float(receipt.get("sensor_confidence", 0.0)) > 1:
        errors.append("rho, delta, and sensor_confidence must be between 0 and 1")
    if not isinstance(receipt.get("position"), dict):
        errors.append("position must be an object")
    if not str(receipt.get("calibration_reason", "")).strip():
        errors.append("calibration_reason is required")
    for field in ("hash_prev", "hash_self"):
        value = receipt.get(field, "")
        if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            errors.append(f"{field} must be a 64 character lowercase sha256 hex string")
    if "hash_self" in receipt and receipt.get("hash_self") != compute_hash(receipt):
        errors.append("hash_self does not match canonical spatial receipt")
    return errors


def write_spatial_receipt(path: Path, event: dict[str, Any], envelope: OperationalEnvelope | dict[str, Any] | None) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    resolved = envelope if isinstance(envelope, OperationalEnvelope) else OperationalEnvelope.from_dict(envelope)
    decision, reason, makers, calibration = evaluate_spatial_gate(event, resolved)
    receipt = _build_receipt(event, resolved, decision, reason, makers, calibration, _last_hash(path))
    errors = validate_spatial_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")
    return receipt
