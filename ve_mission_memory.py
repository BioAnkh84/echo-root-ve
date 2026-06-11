from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class MissionMemory:
    updated_utc: str
    purpose: str
    constraints: list[str]
    current_mission: str
    success_conditions: list[str]
    non_goals: list[str] = field(default_factory=list)


DEFAULT_MISSION = MissionMemory(
    updated_utc=datetime.now(timezone.utc).isoformat(),
    purpose="Build a governed local-first AI habitat that can explain and audit its own behavior.",
    constraints=[
        "No authority leakage",
        "Consent first",
        "Local-first where possible",
        "Pairing context is evidence, not permission",
        "Proposal is not execution",
    ],
    current_mission="Maintain a reviewable VE gate, audit, replay, and pairing evidence pipeline.",
    success_conditions=[
        "Gate decisions are signed and replayable",
        "Nuanced intent is clarified before action or recording",
        "Lessons learned are recorded without granting new autonomy",
    ],
    non_goals=[
        "More autonomy without review",
        "More device control",
        "Unconsented training data collection",
    ],
)


def load_mission(path: Path) -> MissionMemory:
    if not path.exists():
        return DEFAULT_MISSION
    return MissionMemory(**json.loads(path.read_text(encoding="utf-8")))


def save_mission(path: Path, mission: MissionMemory) -> MissionMemory:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(mission), indent=2), encoding="utf-8")
    return mission


def main() -> int:
    parser = argparse.ArgumentParser(description="VE mission memory")
    parser.add_argument("--mission", default="ve_data/mission_memory.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show")
    sub.add_parser("init")
    args = parser.parse_args()
    path = Path(args.mission)
    if args.command == "init":
        print(json.dumps(asdict(save_mission(path, load_mission(path))), indent=2))
        return 0
    print(json.dumps(asdict(load_mission(path)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
