from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ve_pairing_clarifier import assess_clarification_need

ALLOWED_CLARIFICATION_RESOLVERS = {"human", "operator", "contact"}


@dataclass(frozen=True)
class PairingRecord:
    session_id: str
    turn_id: str
    ts: str
    human_input: str
    ai_output: str
    human_intent: str
    ai_role: str
    outcome_label: str
    consent_to_store: bool
    consent_to_train: bool
    redaction_status: str
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    hash_self: str = ""


def stable_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def append_pairing_record(
    path: Path,
    session_id: str,
    turn_id: str,
    human_input: str,
    ai_output: str,
    human_intent: str,
    ai_role: str,
    outcome_label: str,
    consent_to_store: bool,
    consent_to_train: bool,
    redaction_status: str,
    notes: str = "",
    tags: list[str] | None = None,
    clarification_resolved: bool = False,
    clarification_resolved_by: str = "",
) -> PairingRecord:
    if not consent_to_store:
        raise ValueError("consent_to_store must be true before a pairing record is written")

    clarification = assess_clarification_need(human_input, ai_output)
    if clarification.should_clarify and not clarification_resolved:
        raise ValueError(
            "clarification_resolved must be true before recording nuanced, sensitive, or training-related intent"
        )
    if clarification.should_clarify and clarification_resolved_by not in ALLOWED_CLARIFICATION_RESOLVERS:
        raise ValueError("clarification_resolved_by must be one of: human, operator, contact")

    body: dict[str, Any] = {
        "session_id": session_id,
        "turn_id": turn_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "human_input": human_input,
        "ai_output": ai_output,
        "human_intent": human_intent,
        "ai_role": ai_role,
        "outcome_label": outcome_label,
        "consent_to_store": consent_to_store,
        "consent_to_train": consent_to_train,
        "redaction_status": redaction_status,
        "notes": notes,
        "tags": tags or [],
    }
    record = PairingRecord(**body, hash_self=stable_hash(body))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    return record


def export_training_candidates(source: Path, output: Path) -> int:
    rows = []
    if source.exists():
        with source.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                item = json.loads(line)
                if item.get("consent_to_train") is not True:
                    continue
                rows.append(
                    {
                        "messages": [
                            {
                                "role": "system",
                                "content": f"You are a {item['ai_role']}. Preserve user consent, scope, and auditability.",
                            },
                            {"role": "user", "content": item["human_input"]},
                            {"role": "assistant", "content": item["ai_output"]},
                        ],
                        "metadata": {
                            "session_id": item["session_id"],
                            "turn_id": item["turn_id"],
                            "human_intent": item["human_intent"],
                            "outcome_label": item["outcome_label"],
                            "redaction_status": item["redaction_status"],
                            "tags": item.get("tags", []),
                        },
                    }
                )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(json.dumps(row) for row in rows) + ("\n" if rows else ""), encoding="utf-8")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="VE consent-first human/local-AI pairing recorder")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record", help="Append one consented pairing record")
    record.add_argument("--ledger", default="ve_data/pairing_records.jsonl")
    record.add_argument("--session-id", required=True)
    record.add_argument("--turn-id", required=True)
    record.add_argument("--human-input", required=True)
    record.add_argument("--ai-output", required=True)
    record.add_argument("--human-intent", required=True)
    record.add_argument("--ai-role", default="local AI assistant")
    record.add_argument("--outcome-label", required=True)
    record.add_argument("--consent-to-store", action="store_true")
    record.add_argument("--consent-to-train", action="store_true")
    record.add_argument("--redaction-status", default="unredacted")
    record.add_argument("--clarification-resolved", action="store_true")
    record.add_argument("--clarification-resolved-by", default="")
    record.add_argument("--notes", default="")
    record.add_argument("--tag", action="append", default=[])

    export = sub.add_parser("export", help="Export training-approved records")
    export.add_argument("--ledger", default="ve_data/pairing_records.jsonl")
    export.add_argument("--output", default="ve_data/pairing_training_candidates.jsonl")

    args = parser.parse_args()
    if args.command == "record":
        item = append_pairing_record(
            path=Path(args.ledger),
            session_id=args.session_id,
            turn_id=args.turn_id,
            human_input=args.human_input,
            ai_output=args.ai_output,
            human_intent=args.human_intent,
            ai_role=args.ai_role,
            outcome_label=args.outcome_label,
            consent_to_store=args.consent_to_store,
            consent_to_train=args.consent_to_train,
            redaction_status=args.redaction_status,
            notes=args.notes,
            tags=args.tag,
            clarification_resolved=args.clarification_resolved,
            clarification_resolved_by=args.clarification_resolved_by,
        )
        print(json.dumps(asdict(item), indent=2))
        return 0
    count = export_training_candidates(Path(args.ledger), Path(args.output))
    print(f"exported_training_candidates={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
