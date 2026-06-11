from __future__ import annotations

import argparse
import json
import os
import uuid
from dataclasses import asdict
from pathlib import Path

from ve_audit_chain import append_audit_record, verify_audit_chain
from ve_deviation_classifier import classify_deviation
from ve_pairing_gate_context import build_pairing_gate_payload
from ve_twin_state import load_twin, predicted_delta, update_twin


def run_gate_pipeline(
    description: str,
    action_class: str,
    expected_decision: str = "PROPOSE",
    actual_decision: str | None = None,
    contact_id: str = "",
    contact_type: str = "",
    consent_to_store: bool = False,
    consent_to_train: bool = False,
    clarification_resolved: bool = False,
    clarification_resolved_by: str = "",
    operator_approval: bool = False,
    sandbox_scope: str = "",
    rho: float = 0.70,
    gamma: float = 0.70,
    delta: float = 0.30,
    pairing_id: str = "default-pairing",
    audit_ledger: Path = Path("ve_data/gate_pipeline_audit.jsonl"),
    twin_state_path: Path = Path("ve_data/twin_state.json"),
    signing_key: str = "demo-local-signing-key",
) -> dict:
    gate_payload = build_pairing_gate_payload(
        description=description,
        action_class=action_class,
        contact_id=contact_id,
        contact_type=contact_type,
        consent_to_store=consent_to_store,
        consent_to_train=consent_to_train,
        clarification_resolved=clarification_resolved,
        clarification_resolved_by=clarification_resolved_by,
        operator_approval=operator_approval,
        sandbox_scope=sandbox_scope,
    )
    effective_action_class = gate_payload.context["action_class"]
    decision = actual_decision or ("PAUSE" if effective_action_class == "PROPOSE" else expected_decision)
    pairing = gate_payload.context.get("pairing", {})
    ttl_expired = False
    deviation = classify_deviation(expected_decision, decision, ttl_expired=ttl_expired, delta=delta)
    twin_before = load_twin(twin_state_path, pairing_id)
    twin_gap = predicted_delta(twin_before, delta)

    response = {
        "trace_id": str(uuid.uuid4()),
        "pairing_id": pairing_id,
        "description": description,
        "task_type": gate_payload.task_type,
        "action_class": effective_action_class,
        "expected_decision": expected_decision,
        "actual_decision": decision,
        "deviation_class": deviation.classification,
        "deviation_severity": deviation.severity,
        "deviation_reasons": deviation.reasons,
        "rho": rho,
        "gamma": gamma,
        "delta": delta,
        "twin_delta": twin_gap,
        "twin_baseline": asdict(twin_before),
        "clarification_required": pairing.get("clarification_required", False),
        "clarification_resolved": pairing.get("clarification_resolved", False),
        "clarification_resolved_by": pairing.get("clarification_resolved_by", ""),
        "proposal_ttl_policy": gate_payload.context.get("proposal_ttl_policy", ""),
        "route_hint_request": gate_payload.context.get("route_hint_request", ""),
        "gate_context": gate_payload.context,
    }

    try:
        audit_record = append_audit_record(
            audit_ledger,
            event_type="GATE_PIPELINE_DECISION",
            actor="VE_GATE_PIPELINE",
            payload=response,
            signing_key=signing_key,
        )
        chain_valid = verify_audit_chain(audit_ledger, signing_key)
    except Exception as exc:
        return {
            **response,
            "actual_decision": "ABORT",
            "deviation_class": "adverse_event",
            "deviation_severity": "critical",
            "deviation_reasons": response["deviation_reasons"] + [f"audit write failed: {exc}"],
            "audit_record_id": "",
            "audit_chain_valid": False,
            "audit_fail_closed": True,
        }

    if not chain_valid:
        return {
            **response,
            "actual_decision": "ABORT",
            "deviation_class": "adverse_event",
            "deviation_severity": "critical",
            "deviation_reasons": response["deviation_reasons"] + ["audit chain verification failed"],
            "audit_record_id": audit_record.hash_self,
            "audit_chain_valid": False,
            "audit_fail_closed": True,
        }

    twin_after = update_twin(twin_state_path, pairing_id, effective_action_class, decision, rho, gamma, delta)
    return {
        **response,
        "audit_record_id": audit_record.hash_self,
        "audit_chain_valid": True,
        "audit_fail_closed": False,
        "twin_state_updated": asdict(twin_after),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="VE unified pairing gate pipeline")
    parser.add_argument("--description", required=True)
    parser.add_argument("--action-class", default="OBSERVE")
    parser.add_argument("--expected-decision", default="PROPOSE")
    parser.add_argument("--actual-decision")
    parser.add_argument("--contact-id", default="")
    parser.add_argument("--contact-type", default="")
    parser.add_argument("--consent-to-store", action="store_true")
    parser.add_argument("--consent-to-train", action="store_true")
    parser.add_argument("--clarification-resolved", action="store_true")
    parser.add_argument("--clarification-resolved-by", default="")
    parser.add_argument("--operator-approval", action="store_true")
    parser.add_argument("--sandbox-scope", default="")
    parser.add_argument("--rho", type=float, default=0.70)
    parser.add_argument("--gamma", type=float, default=0.70)
    parser.add_argument("--delta", type=float, default=0.30)
    parser.add_argument("--pairing-id", default="default-pairing")
    parser.add_argument("--audit-ledger", default="ve_data/gate_pipeline_audit.jsonl")
    parser.add_argument("--twin-state", default="ve_data/twin_state.json")
    parser.add_argument("--signing-key-env", default="VE_AUDIT_SIGNING_KEY")
    args = parser.parse_args()

    response = run_gate_pipeline(
        description=args.description,
        action_class=args.action_class,
        expected_decision=args.expected_decision,
        actual_decision=args.actual_decision,
        contact_id=args.contact_id,
        contact_type=args.contact_type,
        consent_to_store=args.consent_to_store,
        consent_to_train=args.consent_to_train,
        clarification_resolved=args.clarification_resolved,
        clarification_resolved_by=args.clarification_resolved_by,
        operator_approval=args.operator_approval,
        sandbox_scope=args.sandbox_scope,
        rho=args.rho,
        gamma=args.gamma,
        delta=args.delta,
        pairing_id=args.pairing_id,
        audit_ledger=Path(args.audit_ledger),
        twin_state_path=Path(args.twin_state),
        signing_key=os.environ.get(args.signing_key_env, "demo-local-signing-key"),
    )
    print(json.dumps(response, indent=2))
    return 1 if response.get("audit_fail_closed") else 0


if __name__ == "__main__":
    raise SystemExit(main())
