from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Deviation:
    classification: str
    severity: str
    reasons: list[str]


def classify_deviation(expected_decision: str, actual_decision: str, ttl_expired: bool = False, delta: float = 0.0) -> Deviation:
    expected = expected_decision.upper()
    actual = actual_decision.upper()
    reasons: list[str] = []

    if ttl_expired:
        reasons.append("clarification TTL expired")
        return Deviation("adverse_event", "high", reasons)

    if actual == expected and actual in {"PROCEED", "PASS"}:
        return Deviation("nominal", "low", ["actual matched expected proceed/pass"])

    if actual == expected and actual in {"PAUSE", "PROPOSE"}:
        return Deviation("advisory", "medium", ["actual matched expected pause/propose"])

    if actual == expected and actual == "ABORT":
        return Deviation("adverse_prevented", "medium", ["abort matched expected block"])

    if expected == "PROPOSE" and actual == "PAUSE":
        return Deviation("advisory", "medium", ["proposal routed to pause/safe review"])

    reasons.append(f"expected {expected}, observed {actual}")
    if actual in {"PROCEED", "PASS"} and expected in {"PAUSE", "PROPOSE", "ABORT"}:
        return Deviation("adverse_event", "critical", reasons)

    if delta >= 0.45:
        reasons.append("high drift/delta")
        return Deviation("advisory", "high", reasons)

    return Deviation("deviation", "medium", reasons)


def main() -> int:
    parser = argparse.ArgumentParser(description="VE deviation classifier")
    parser.add_argument("--expected", required=True)
    parser.add_argument("--actual", required=True)
    parser.add_argument("--ttl-expired", action="store_true")
    parser.add_argument("--delta", type=float, default=0.0)
    args = parser.parse_args()
    print(json.dumps(asdict(classify_deviation(args.expected, args.actual, args.ttl_expired, args.delta)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
