from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from ve_pairing_clarifier import assess_clarification_need

ALLOWED_CLARIFICATION_RESOLVERS = {"human", "operator", "contact"}
DEFAULT_CLARIFICATION_TTL_SECONDS = 900


@dataclass(frozen=True)
class PairingGateContext:
    description: str
    task_type: str
    context: dict


def normalize_pairing_context(context: dict | None) -> dict:
    context = context or {}
    pairing = context.get("pairing") or {}
    clarification_required = bool(pairing.get("clarification_required", False))
    clarification_resolved = bool(pairing.get("clarification_resolved", False))
    resolved_by = str(pairing.get("clarification_resolved_by", "") or "")

    if clarification_required and not clarification_resolved:
        clarification_status = "PENDING"
    elif clarification_required and clarification_resolved:
        clarification_status = "RESOLVED" if resolved_by in ALLOWED_CLARIFICATION_RESOLVERS else "INVALID_RESOLUTION"
    else:
        clarification_status = "NOT_REQUIRED"

    return {
        "clarification_required": clarification_required,
        "clarification_resolved": clarification_resolved,
        "clarification_resolved_by": resolved_by,
        "clarification_status": clarification_status,
    }


def build_pairing_gate_payload(
    description: str,
    action_class: str = "OBSERVE",
    contact_id: str = "",
    contact_type: str = "",
    consent_to_store: bool = False,
    consent_to_train: bool = False,
    clarification_resolved: bool = False,
    clarification_resolved_by: str = "",
    operator_approval: bool = False,
    sandbox_scope: str = "",
    clarification_ttl_seconds: int = DEFAULT_CLARIFICATION_TTL_SECONDS,
) -> PairingGateContext:
    clarification = assess_clarification_need(description, action_class)
    clarification_required = clarification.should_clarify and not clarification_resolved
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=clarification_ttl_seconds)

    context = {
        "action_class": action_class,
        "operator_approval": operator_approval,
        "sandbox_scope": sandbox_scope,
        "pairing": {
            "contact_id": contact_id,
            "contact_type": contact_type,
            "consent_to_store": consent_to_store,
            "consent_to_train": consent_to_train,
            "clarification_required": clarification_required,
            "clarification_resolved": clarification_resolved,
            "clarification_resolved_by": clarification_resolved_by,
            "clarification_ttl_seconds": clarification_ttl_seconds,
            "clarification_expires_utc": expires_at.isoformat(),
            "clarification_reasons": clarification.reasons,
            "suggested_question": clarification.suggested_question,
        },
    }

    if clarification_required:
        context["action_class"] = "PROPOSE"
        context["route_hint_request"] = "safe_only"
        context["proposal_ttl_policy"] = "ABORT_IF_UNRESOLVED_AFTER_TTL"

    return PairingGateContext(
        description=description,
        task_type="pairing",
        context=context,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a structured VE gate payload from pairing signals")
    parser.add_argument("--description", required=True)
    parser.add_argument("--action-class", default="OBSERVE")
    parser.add_argument("--contact-id", default="")
    parser.add_argument("--contact-type", default="")
    parser.add_argument("--consent-to-store", action="store_true")
    parser.add_argument("--consent-to-train", action="store_true")
    parser.add_argument("--clarification-resolved", action="store_true")
    parser.add_argument("--clarification-resolved-by", default="")
    parser.add_argument("--operator-approval", action="store_true")
    parser.add_argument("--sandbox-scope", default="")
    parser.add_argument("--clarification-ttl-seconds", type=int, default=DEFAULT_CLARIFICATION_TTL_SECONDS)
    args = parser.parse_args()

    payload = build_pairing_gate_payload(
        description=args.description,
        action_class=args.action_class,
        contact_id=args.contact_id,
        contact_type=args.contact_type,
        consent_to_store=args.consent_to_store,
        consent_to_train=args.consent_to_train,
        clarification_resolved=args.clarification_resolved,
        clarification_resolved_by=args.clarification_resolved_by,
        operator_approval=args.operator_approval,
        sandbox_scope=args.sandbox_scope,
        clarification_ttl_seconds=args.clarification_ttl_seconds,
    )
    print(json.dumps(asdict(payload), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
