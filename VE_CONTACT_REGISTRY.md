# VE Contact Registry

`ve_contact_registry.py` is a governed contact/context list for interactions with people, AIs, services, and groups.

It is designed for pairing context, not surveillance.

## Core Rules

- Contacts are added intentionally by the human or from explicit human-approved context.
- Check-ins are cadence-based, not random.
- The AI should ask the human before prompting about irregular or stale contacts.
- A stale contact is not a problem by itself; it is only a signal to clarify status.
- Private relationship details should stay local and should not be exported without consent.

## Contact Types

| Type | Meaning |
| --- | --- |
| `human` | A person. |
| `ai` | A local or external AI counterpart. |
| `service` | A tool, API, or system endpoint. |
| `group` | A team or recurring group context. |

## Cadence

| Cadence | Check Suggestion Threshold |
| --- | --- |
| `regular` | 14 days |
| `occasional` | 45 days |
| `rare` | 120 days |
| `paused` | No suggestions |

## Commands

Add a contact:

```powershell
py -3.11 ve_contact_registry.py add `
  --contact-id cipher `
  --display-name "Cipher" `
  --contact-type ai `
  --cadence regular `
  --ask-before-checkin `
  --tag local_ai
```

Mark a contact as recently interacted:

```powershell
py -3.11 ve_contact_registry.py seen --contact-id cipher
```

Show recent contacts:

```powershell
py -3.11 ve_contact_registry.py recent
```

Suggest status confirmations:

```powershell
py -3.11 ve_contact_registry.py suggest
```

## Pairing Posture

The AI can ask:

```text
This contact used to be regular but has not appeared recently. Do you want me to keep them active, pause them, or leave the status unchanged?
```

That lets the human guide nuance without the AI inventing relationship meaning.
