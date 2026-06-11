from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


NUANCE_MARKERS = (
    "maybe",
    "not sure",
    "kinda",
    "sort of",
    "if you think",
    "whatever is best",
    "use your judgment",
    "do what you think",
)

HIGH_STAKES_MARKERS = (
    "delete",
    "remove",
    "overwrite",
    "send",
    "publish",
    "train",
    "record",
    "private",
    "secret",
    "credential",
    "medical",
    "legal",
    "financial",
)


@dataclass(frozen=True)
class ClarificationDecision:
    should_clarify: bool
    reasons: list[str]
    suggested_question: str


def assess_clarification_need(text: str, action: str = "") -> ClarificationDecision:
    combined = f"{text} {action}".lower()
    reasons: list[str] = []

    if any(marker in combined for marker in NUANCE_MARKERS):
        reasons.append("nuanced or uncertain intent")

    if any(marker in combined for marker in HIGH_STAKES_MARKERS):
        reasons.append("high-stakes or privacy-sensitive action")

    if len(text.strip()) < 12:
        reasons.append("underspecified request")

    if not reasons:
        return ClarificationDecision(
            should_clarify=False,
            reasons=["intent appears sufficiently clear for low-risk handling"],
            suggested_question="",
        )

    return ClarificationDecision(
        should_clarify=True,
        reasons=reasons,
        suggested_question=(
            "Before I act or record this, can you clarify the intended outcome, "
            "scope, and whether this should be stored or used for training/evals?"
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="VE pairing clarification check")
    parser.add_argument("--text", required=True)
    parser.add_argument("--action", default="")
    args = parser.parse_args()
    decision = assess_clarification_need(args.text, args.action)
    print(json.dumps(asdict(decision), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
