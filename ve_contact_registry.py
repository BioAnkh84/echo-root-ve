from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


CONTACT_TYPES = {"human", "ai", "service", "group"}
CADENCES = {"regular", "occasional", "rare", "paused"}


@dataclass(frozen=True)
class Contact:
    contact_id: str
    display_name: str
    contact_type: str
    cadence: str
    ask_before_checkin: bool = True
    last_interaction_utc: str | None = None
    status: str = "active"
    notes: str = ""
    tags: list[str] = field(default_factory=list)


def load_contacts(path: Path) -> list[Contact]:
    if not path.exists():
        return []
    contacts = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            contacts.append(Contact(**json.loads(line)))
    return contacts


def save_contacts(path: Path, contacts: list[Contact]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(asdict(contact), sort_keys=True) for contact in contacts)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def upsert_contact(path: Path, contact: Contact) -> Contact:
    contacts = load_contacts(path)
    remaining = [item for item in contacts if item.contact_id != contact.contact_id]
    remaining.append(contact)
    save_contacts(path, sorted(remaining, key=lambda item: item.display_name.lower()))
    return contact


def record_interaction(path: Path, contact_id: str, timestamp_utc: str | None = None) -> Contact:
    contacts = load_contacts(path)
    timestamp_utc = timestamp_utc or datetime.now(timezone.utc).isoformat()
    updated = None
    new_contacts = []
    for contact in contacts:
        if contact.contact_id == contact_id:
            updated = Contact(**{**asdict(contact), "last_interaction_utc": timestamp_utc, "status": "active"})
            new_contacts.append(updated)
        else:
            new_contacts.append(contact)
    if updated is None:
        raise ValueError(f"unknown contact_id: {contact_id}")
    save_contacts(path, new_contacts)
    return updated


def most_recent(path: Path, limit: int = 5) -> list[Contact]:
    contacts = [item for item in load_contacts(path) if item.last_interaction_utc]
    return sorted(contacts, key=lambda item: item.last_interaction_utc or "", reverse=True)[:limit]


def checkin_suggestions(path: Path, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    thresholds = {
        "regular": 14,
        "occasional": 45,
        "rare": 120,
    }
    suggestions = []
    for contact in load_contacts(path):
        if contact.status != "active" or contact.cadence == "paused":
            continue
        if contact.cadence not in thresholds:
            continue
        if not contact.last_interaction_utc:
            suggestions.append(
                {
                    "contact_id": contact.contact_id,
                    "display_name": contact.display_name,
                    "reason": "no recorded interaction yet",
                    "ask_human_first": True,
                    "suggested_question": f"Do you want to confirm the current status for {contact.display_name}?",
                }
            )
            continue
        last = datetime.fromisoformat(contact.last_interaction_utc.replace("Z", "+00:00"))
        elapsed_days = (now - last).days
        if elapsed_days >= thresholds[contact.cadence]:
            suggestions.append(
                {
                    "contact_id": contact.contact_id,
                    "display_name": contact.display_name,
                    "reason": f"{elapsed_days} days since last interaction; cadence is {contact.cadence}",
                    "ask_human_first": contact.ask_before_checkin,
                    "suggested_question": f"{contact.display_name} has not been marked recently. Should I update their status or leave them as-is?",
                }
            )
    return suggestions


def main() -> int:
    parser = argparse.ArgumentParser(description="VE contact registry for human/AI interaction context")
    parser.add_argument("--contacts", default="ve_data/contacts.jsonl")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("--contact-id", required=True)
    add.add_argument("--display-name", required=True)
    add.add_argument("--contact-type", choices=sorted(CONTACT_TYPES), required=True)
    add.add_argument("--cadence", choices=sorted(CADENCES), default="occasional")
    add.add_argument("--ask-before-checkin", action="store_true")
    add.add_argument("--status", default="active")
    add.add_argument("--notes", default="")
    add.add_argument("--tag", action="append", default=[])

    seen = sub.add_parser("seen")
    seen.add_argument("--contact-id", required=True)

    sub.add_parser("list")

    recent = sub.add_parser("recent")
    recent.add_argument("--limit", type=int, default=5)

    sub.add_parser("suggest")

    args = parser.parse_args()
    path = Path(args.contacts)
    if args.command == "add":
        contact = upsert_contact(
            path,
            Contact(
                contact_id=args.contact_id,
                display_name=args.display_name,
                contact_type=args.contact_type,
                cadence=args.cadence,
                ask_before_checkin=args.ask_before_checkin,
                status=args.status,
                notes=args.notes,
                tags=args.tag,
            ),
        )
        print(json.dumps(asdict(contact), indent=2))
    elif args.command == "seen":
        print(json.dumps(asdict(record_interaction(path, args.contact_id)), indent=2))
    elif args.command == "list":
        print(json.dumps([asdict(item) for item in load_contacts(path)], indent=2))
    elif args.command == "recent":
        print(json.dumps([asdict(item) for item in most_recent(path, args.limit)], indent=2))
    elif args.command == "suggest":
        print(json.dumps(checkin_suggestions(path), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
