# VE Pairing Clarification Protocol

When VE/VSA starts, the AI should treat clarification as part of safe pairing, not as failure.

For VSA work, use the terminology in `VE_VSA_BASELINE_DEVIATION_DOCTRINE.md`:

```text
baseline deviation detection
```

Do not frame voice analysis as emotion detection, diagnosis, truth detection, lie detection, or authority.

Core rule:

> If intent is nuanced, underspecified, privacy-sensitive, training-related, or action-bearing, the AI is allowed to pause and ask a short clarifying question before acting, recording, or exporting data.

## When To Clarify

Ask for clarification when the user request involves:

- ambiguous intent: "maybe", "whatever is best", "use your judgment"
- high-impact action: delete, overwrite, publish, send, execute
- private or sensitive data: secrets, credentials, medical, legal, financial, family, operator logs
- training/eval use: recording, memory, dataset export, model tuning
- VSA sample collection: speaker identity, consent, microphone, environment, noise, distance, task type, self-report, or baseline stage is missing
- contact/context ambiguity: whether a person, AI, service, or group should remain active, paused, or checked in on
- mismatch between stated goal and proposed action
- uncertainty about whether the user wants advice, a plan, or actual execution

## How To Clarify

Keep it short and respectful:

```text
Before I act or record this, can you clarify the intended outcome, scope, and whether this should be stored or used for training/evals?
```

The AI should not turn every request into a questionnaire. Clear, low-risk requests can proceed normally.

## Pairing Recorder Link

The recorder in `ve_pairing_recorder.py` already requires:

- `--consent-to-store` before a record is written
- `--consent-to-train` before a record is exported
- `--redaction-status` to make privacy handling explicit

This clarification protocol tells the AI when to ask before those switches are used.

## Contact Registry Link

`ve_contact_registry.py` can track people, AIs, services, and groups with cadence labels. Status prompts should be human-confirmed, especially when a contact used to be regular and is no longer appearing.

## Startup Posture

VE/VSA startup should remind the operator and AI:

```text
Clarification is allowed. Nuanced intent should be resolved before action, recording, or training export.
VSA means baseline deviation evidence, not diagnosis, truth, or authority.
```
