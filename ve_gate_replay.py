from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from ve_audit_chain import verify_audit_chain
from ve_deviation_classifier import classify_deviation


@dataclass(frozen=True)
class ReplayRecord:
    trace_id: str
    pairing_id: str
    event_type: str
    action_class: str
    expected_decision: str
    actual_decision: str
    original_deviation_class: str
    replay_deviation_class: str
    replay_severity: str
    ttl_policy: str
    clarification_required: bool
    twin_delta: float
    audit_hash: str
    classifier_changed: bool


def load_audit_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def replay_gate_audit(path: Path, signing_key: str) -> dict:
    chain_valid = verify_audit_chain(path, signing_key)
    records = []
    for item in load_audit_records(path):
        payload = item.get("payload", {})
        if item.get("event_type") != "GATE_PIPELINE_DECISION":
            continue
        replay = classify_deviation(
            payload.get("expected_decision", "PROPOSE"),
            payload.get("actual_decision", "ABORT"),
            ttl_expired=False,
            delta=float(payload.get("delta", 0.0)),
        )
        records.append(
            ReplayRecord(
                trace_id=payload.get("trace_id", ""),
                pairing_id=payload.get("pairing_id", "default-pairing"),
                event_type=item.get("event_type", ""),
                action_class=payload.get("action_class", ""),
                expected_decision=payload.get("expected_decision", ""),
                actual_decision=payload.get("actual_decision", ""),
                original_deviation_class=payload.get("deviation_class", ""),
                replay_deviation_class=replay.classification,
                replay_severity=replay.severity,
                ttl_policy=payload.get("proposal_ttl_policy", ""),
                clarification_required=bool(payload.get("clarification_required", False)),
                twin_delta=float(payload.get("twin_delta", 0.0)),
                audit_hash=item.get("hash_self", ""),
                classifier_changed=payload.get("deviation_class", "") != replay.classification,
            )
        )

    sessions: dict[str, dict] = {}
    for record in records:
        session = sessions.setdefault(
            record.pairing_id,
            {
                "pairing_id": record.pairing_id,
                "records": 0,
                "adverse_events": 0,
                "advisory_events": 0,
                "max_twin_delta": 0.0,
                "classifier_changes": 0,
            },
        )
        session["records"] += 1
        if record.replay_deviation_class == "adverse_event":
            session["adverse_events"] += 1
        if record.replay_deviation_class == "advisory":
            session["advisory_events"] += 1
        if record.classifier_changed:
            session["classifier_changes"] += 1
        session["max_twin_delta"] = max(session["max_twin_delta"], record.twin_delta)

    summary = {
        "audit_chain_valid": chain_valid,
        "records_replayed": len(records),
        "adverse_events": sum(1 for item in records if item.replay_deviation_class == "adverse_event"),
        "advisory_events": sum(1 for item in records if item.replay_deviation_class == "advisory"),
        "max_twin_delta": max((item.twin_delta for item in records), default=0.0),
        "classifier_changes": sum(1 for item in records if item.classifier_changed),
        "sessions": list(sessions.values()),
        "records": [asdict(item) for item in records],
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay VE gate pipeline audit records")
    parser.add_argument("--ledger", default="ve_data/gate_pipeline_audit.jsonl")
    parser.add_argument("--signing-key-env", default="VE_AUDIT_SIGNING_KEY")
    args = parser.parse_args()
    summary = replay_gate_audit(Path(args.ledger), os.environ.get(args.signing_key_env, "demo-local-signing-key"))
    print(json.dumps(summary, indent=2))
    return 0 if summary["audit_chain_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
