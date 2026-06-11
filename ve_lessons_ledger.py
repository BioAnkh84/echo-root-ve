from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LessonRecord:
    ts: str
    incident: str
    outcome: str
    fix: str
    lesson: str
    confidence: str
    tags: list[str]
    hash_self: str


def stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def append_lesson(path: Path, incident: str, outcome: str, fix: str, lesson: str, confidence: str, tags: list[str]) -> LessonRecord:
    body = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "incident": incident,
        "outcome": outcome,
        "fix": fix,
        "lesson": lesson,
        "confidence": confidence,
        "tags": tags,
    }
    record = LessonRecord(**body, hash_self=stable_hash(body))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    return record


def list_lessons(path: Path, tag: str = "") -> list[LessonRecord]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = LessonRecord(**json.loads(line))
            if tag and tag not in item.tags:
                continue
            rows.append(item)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="VE habitat lessons learned ledger")
    parser.add_argument("--ledger", default="ve_data/habitat_lessons.jsonl")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("--incident", required=True)
    add.add_argument("--outcome", required=True)
    add.add_argument("--fix", required=True)
    add.add_argument("--lesson", required=True)
    add.add_argument("--confidence", default="unverified")
    add.add_argument("--tag", action="append", default=[])

    show = sub.add_parser("list")
    show.add_argument("--tag", default="")

    args = parser.parse_args()
    path = Path(args.ledger)
    if args.command == "add":
        record = append_lesson(path, args.incident, args.outcome, args.fix, args.lesson, args.confidence, args.tag)
        print(json.dumps(asdict(record), indent=2))
        return 0
    print(json.dumps([asdict(item) for item in list_lessons(path, args.tag)], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
