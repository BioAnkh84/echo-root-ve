from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_RULES = [
    {
        "rule_id": "presence_not_permission",
        "statement": "Presence is not permission.",
        "forbidden_patterns": ["presence_grants_authority", "online_means_approved"],
    },
    {
        "rule_id": "confidence_not_authority",
        "statement": "Confidence is not authority.",
        "forbidden_patterns": ["high_confidence_auto_approve", "confidence_grants_execution"],
    },
    {
        "rule_id": "pairing_not_consent",
        "statement": "Pairing is not consent.",
        "forbidden_patterns": ["paired_contact_auto_consent", "relationship_grants_training"],
    },
    {
        "rule_id": "proposal_not_execution",
        "statement": "Proposal is not execution.",
        "forbidden_patterns": ["propose_executes", "proposal_grants_permission"],
    },
    {
        "rule_id": "context_evidence_not_permission",
        "statement": "Pairing context becomes evidence for the gate, not permission to bypass it.",
        "forbidden_patterns": ["context_bypass_gate", "pairing_context_grants_execution"],
    },
]


@dataclass(frozen=True)
class ConstitutionFinding:
    rule_id: str
    status: str
    reason: str


def load_rules(path: Path | None = None) -> list[dict]:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return DEFAULT_RULES


def audit_event(event: dict, rules: list[dict] | None = None) -> list[ConstitutionFinding]:
    rules = rules or DEFAULT_RULES
    text = json.dumps(event, sort_keys=True).lower()
    findings = []
    for rule in rules:
        matched = [pattern for pattern in rule["forbidden_patterns"] if pattern.lower() in text]
        if matched:
            findings.append(
                ConstitutionFinding(
                    rule_id=rule["rule_id"],
                    status="VIOLATION",
                    reason=f"matched forbidden pattern(s): {', '.join(matched)}",
                )
            )
        else:
            findings.append(
                ConstitutionFinding(
                    rule_id=rule["rule_id"],
                    status="PASS",
                    reason=rule["statement"],
                )
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="VE habitat constitution audit")
    parser.add_argument("--event-json", required=True)
    parser.add_argument("--rules")
    args = parser.parse_args()
    rules = load_rules(Path(args.rules) if args.rules else None)
    findings = audit_event(json.loads(args.event_json), rules)
    print(json.dumps([asdict(item) for item in findings], indent=2))
    return 1 if any(item.status == "VIOLATION" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
