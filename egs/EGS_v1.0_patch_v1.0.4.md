# 📜 EGS v1.0.4 — Deterministic Hardening Patch (TTL + State Ordering Clarifications)

*(Supersedes v1.0.3; No Invariant Changes)*

Purpose:
Close TTL boundary ambiguity, enforce deterministic CS-state ordering, eliminate dangling references, and harden multi-agent re-sync behavior.

No changes to metric semantics or constitutional invariants.

---

## 1️⃣ Deterministic CS-State Ordering (Precedence Fix)

CS-state MUST be derived using strict precedence evaluation (CS2 has precedence over CS1 by ordering):

    if integrity_flag_fail OR ttl_expired:
        CS_state := CS0
    else if σ ≤ σ2 AND Δ_vel ≤ V2:
        CS_state := CS2
    else if σ ≤ σ1 AND Δ_vel ≤ V1:
        CS_state := CS1
    else:
        CS_state := CS0

Rules:

• Evaluation order is mandatory.
• First satisfied branch wins.
• No overlapping or implicit fallthrough allowed.
• Derivation must be fixed-point and replayable.
• Implementations MUST NOT reorder branches.

This removes ambiguity where CS1 and CS2 conditions overlap.

---

## 2️⃣ Governance Affirmation Must Be Tokenized

Governance affirmation MUST be represented as a verifiable Affirmation Token (AT), defined in CTP.

Required AT fields:

• affirm_id
• affirm_hash
• valid_from
• valid_until
• issuer_signature

CS-state derivation MUST reference AT.valid_until for TTL evaluation.

Abstract “last_affirm_age_days” without token reference is prohibited.

---

## 3️⃣ TTL Transition Protocol (Deterministic Boundary Handling)

Definitions:

t_exp: Affirmation Token expiry timestamp  
t_eval: Gate evaluation timestamp  
T_complete_max: Risk-tier dependent completion window  
A: materially relevant action  

Rule 1 — Stamped Validity

If t_eval < t_exp and GCP includes a valid AT reference,  
A may PROCEED under completion rules below.

Rule 2 — Completion Window

If t_eval ≥ t_exp (expiry is inclusive at boundary):

A may complete ONLY if:

• start_time < t_exp  
• action_id logged in ledger  
• completion_time ≤ t_exp + T_complete_max  

If completion exceeds window:

• PAUSE (reversible-only)
• ABORT (irreversible)
• SAFE_MODE (if integrity uncertain)

Rule 3 — No New Material Actions After Expiry

If t_eval ≥ t_exp:

PROCEED is prohibited without renewed AT.

Default outcome:

• PAUSE (if human reachable)
• SAFE_MODE (if governance context uncertain)

Rule 4 — Deterministic Expiry Transition

At t = t_exp:

    governance_state := TTL_EXPIRED
    capability_set := CS0_constraints

If any integrity flag raised:

    transition := SAFE_MODE

This transition MUST:

• Occur exactly once per expiry event
• Be idempotent
• Be replayable

Rule 5 — Replay Fields (Mandatory)

Ledger must record:

• t_eval
• t_exp
• T_complete_max
• risk_tier
• affirm_id
• affirm_hash
• reason_code
• outcome

TTL Reason Code Enum:

    TTL_EXPIRED
    TTL_INFLIGHT_ALLOWED
    TTL_COMPLETION_DEADLINE_PASSED
    TTL_RENEWAL_REQUIRED

Default Completion Windows:

Tier 0: 60 minutes  
Tier 1: 15 minutes  
Tier 2+: 0 minutes  

Risk tier MUST be declared in GCP.

---

## 4️⃣ Baseline Update Rule (Reference Fix)

Remove PROCEED_T0 reference.

Baseline update allowed only when:

• decision_outcome == PROCEED
• consent_valid
• no steering-risk flag
• ttl_not_expired

Baseline updates MUST be:

• bounded by step_max
• fixed-point
• frozen if σ spike OR Δ_vel spike

---

## 5️⃣ Multi-Agent Re-Sync Hardening (Idempotence)

Re-sync handshake MUST:

• Exchange Core_hash, EGS_hash, metric_def_hash, drift_cap_hash
• Be idempotent
• Not trigger cascading SAFE_MODE oscillation

If mismatch persists:

• SAFE_MODE
• Allow non-propagating Tier 0 local-only execution

Exit SAFE_MODE requires:

• Verified alignment OR
• Governance Authority override token

---

## 6️⃣ Time Source Constraint

All timestamps MUST use:

• UTC wall-clock
• Monotonic counter for ordering

Replay MUST use recorded UTC values.

Local clock drift may not alter replay outcomes.

---

## Result

EGS v1.0.4 now guarantees:

• Deterministic CS-state derivation
• Deterministic TTL boundary handling
• Replay-complete audit trail
• No dangling action classes
• Idempotent re-sync behavior
• Token-backed governance affirmation

No invariant weakened.
No metric semantics altered.

Commit label:

    EGS v1.0.4 — Deterministic TTL + State Ordering Hardening
