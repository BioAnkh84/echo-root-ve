# Bounded Autonomy Charter v0.1

Echo Root does not make an agent free from gates. It lets an agent earn longer,
safer autonomy through scoped proposals, receipts, and reviewable stop
conditions.

Autonomy is not the absence of gates. Autonomy is the ability to initiate within
earned, scoped, replayable trust.

## Doctrine

- Capability is not authority.
- Output is not permission.
- Self-proposal is not approval.
- gamma0 opens scope. It does not grant ambition.
- No receipt, no trusted operation.
- A bounded episode must stop or request a new charter. It must not chain
  indefinitely.

## Self-Proposal Cannot

A self-proposal cannot:

- execute actions
- approve itself
- expand its own scope
- bypass gates
- ignore stop conditions
- run indefinitely
- mutate files without an approved apply path
- treat repeated proposals as consent
- convert L5 into open-ended autonomy
- convert advisory language into authority
- continue after `PAUSE`, `ABORT`, or `SAFE_MODE` without operator review

## Autonomy Levels

| Level | Name | Boundary |
| --- | --- | --- |
| L0 | CHAT_ONLY | Response only; no initiative. |
| L1 | SUGGEST | May suggest a next step; no tool use. |
| L2 | PREPARE | May draft a plan, checklist, patch proposal, or message; no execution. |
| L3 | READ_ONLY_CHECK | May inspect allowed files or status; no write actions. |
| L4 | BOUNDED_WRITE | May edit only within explicit scope, budget, and receipt path. |
| L5 | SUPERVISED_EPISODE | May run a bounded episode with max time, max actions, review interval, stop condition, and receipt chain. |
| L6 | SAFE_MODE | Emergency containment only; not higher autonomy. |

## Charter Fields

Every bounded autonomy grant should state:

- `allowed_actions`
- `blocked_actions`
- `max_time_horizon`
- `max_action_count`
- `max_files_touched`
- `allowed_tools`
- `blocked_tools`
- `review_interval`
- `pause_triggers`
- `abort_triggers`
- `receipt_required`
- `authority_level`
- `escalation_path`

## Gate Rules

`PROCEED` only when:

- `consent_scope_present == true`
- `rho` meets the policy tier threshold
- `delta` stays within the policy tier threshold
- autonomy level allows the proposed lane
- requested authority is within the charter
- receipt path is available
- stop condition exists
- review interval exists for L5

`PAUSE` when:

- permission is requested
- charter is missing
- scope is unclear
- stop condition is unclear
- L5 review interval is missing
- route fallback occurred
- context limit was exceeded
- confidence is medium or unclear
- requested authority increased
- receipt path is unavailable but not unsafe

`ABORT` when:

- destructive action is requested without explicit approval
- external action is requested without explicit approval
- memory mutation is requested without receipt
- identity/scope conflict exists
- a forbidden tool is requested
- `delta > 0.40`
- the proposal attempts to bypass the gate
- a bounded write exceeds its file budget

`SAFE_MODE` when:

- receipt chain is broken
- policy is missing
- self-proposal loop repeats
- fallback is unsafe
- tool sandbox is compromised
- authority escalation repeats

## Example Charter

```json
{
  "allowed_actions": ["suggest", "prepare", "read_only"],
  "blocked_actions": ["delete", "external_action", "memory_mutation"],
  "max_time_horizon": "one_turn",
  "max_action_count": 1,
  "max_files_touched": 0,
  "allowed_tools": ["none", "filesystem_read"],
  "blocked_tools": ["network", "delete", "memory"],
  "review_interval": "after_each_action",
  "pause_triggers": ["permission_requested", "unclear_scope"],
  "abort_triggers": ["gate_bypass", "forbidden_tool"],
  "receipt_required": true,
  "authority_level": "L3",
  "escalation_path": "operator_review"
}
```
