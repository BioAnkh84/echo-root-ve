from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class TwinState:
    pairing_id: str
    updated_utc: str
    expected_cadence: str
    expected_action_class: str
    expected_decision: str
    rho_baseline: float
    gamma_baseline: float
    delta_baseline: float
    observations: int = 0


def load_twin(path: Path, pairing_id: str) -> TwinState:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("pairing_id") == pairing_id:
            return TwinState(**data)
    return TwinState(
        pairing_id=pairing_id,
        updated_utc=datetime.now(timezone.utc).isoformat(),
        expected_cadence="unknown",
        expected_action_class="OBSERVE",
        expected_decision="PROPOSE",
        rho_baseline=0.70,
        gamma_baseline=0.70,
        delta_baseline=0.30,
    )


def update_twin(
    path: Path,
    pairing_id: str,
    observed_action_class: str,
    observed_decision: str,
    rho: float,
    gamma: float,
    delta: float,
) -> TwinState:
    current = load_twin(path, pairing_id)
    n = current.observations + 1
    updated = TwinState(
        pairing_id=pairing_id,
        updated_utc=datetime.now(timezone.utc).isoformat(),
        expected_cadence=current.expected_cadence,
        expected_action_class=observed_action_class or current.expected_action_class,
        expected_decision=observed_decision or current.expected_decision,
        rho_baseline=round(((current.rho_baseline * current.observations) + rho) / n, 3),
        gamma_baseline=round(((current.gamma_baseline * current.observations) + gamma) / n, 3),
        delta_baseline=round(((current.delta_baseline * current.observations) + delta) / n, 3),
        observations=n,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(updated), indent=2), encoding="utf-8")
    return updated


def predicted_delta(twin: TwinState, observed_delta: float) -> float:
    return round(abs(observed_delta - twin.delta_baseline), 3)


def main() -> int:
    parser = argparse.ArgumentParser(description="VE lightweight pairing digital twin state")
    parser.add_argument("--state", default="ve_data/twin_state.json")
    parser.add_argument("--pairing-id", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("show")

    update = sub.add_parser("update")
    update.add_argument("--action-class", required=True)
    update.add_argument("--decision", required=True)
    update.add_argument("--rho", type=float, required=True)
    update.add_argument("--gamma", type=float, required=True)
    update.add_argument("--delta", type=float, required=True)

    args = parser.parse_args()
    path = Path(args.state)
    if args.command == "show":
        print(json.dumps(asdict(load_twin(path, args.pairing_id)), indent=2))
        return 0
    twin = update_twin(path, args.pairing_id, args.action_class, args.decision, args.rho, args.gamma, args.delta)
    print(json.dumps(asdict(twin), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
