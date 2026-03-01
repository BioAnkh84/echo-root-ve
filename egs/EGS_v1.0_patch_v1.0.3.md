# EGS v1.0 — Patch v1.0.3 (March 2026 Minimal Spine)

## 1) Phase-as-a-Derived-State (No Progression Mechanics)
CS-state is derived at decision time from:
- recent stability window statistics
- integrity flags
- governance affirmation recency

Inputs (fixed-point, deterministic):
- σ: rolling variance of Δ_mag over W decisions (default W=50)
- Δ_vel: rolling median of Δ_mag delta over K decisions (default K=7, median-of-7)
- integrity_flags: hash verified, consent valid, ledger OK, no version mismatch
- last_affirm_age_days: days since Governance Authority affirmation

Derived rule (example defaults; tunable but hash-bound):
- CS0 if: integrity_fail OR last_affirm_age_days > 30 OR σ > σ0 OR Δ_vel > V0
- CS1 if: integrity_ok AND last_affirm_age_days ≤ 30 AND σ ≤ σ1 AND Δ_vel ≤ V1
- CS2 if: integrity_ok AND last_affirm_age_days ≤ 30 AND σ ≤ σ2 AND Δ_vel ≤ V2

## 2) Robust Aggregation (Median Gaming Fix)
Default: median-of-7 for Δ_vel; optional trimmed mean over W for σ.

## 3) Baseline Poisoning Fix Without Rotation Churn
- baseline_update allowed only on {PROCEED, PROCEED_T0} with consent valid and no steering-risk flag
- baseline_step ≤ step_max (fixed-point cap)
- freeze baseline_update on σ spike or Δ_vel spike until resolved

## 4) Materiality Counters (Bounded Lifetime)
Lifetime: last 1000 materially relevant decisions (or last 7 days if trusted clock), whichever comes first.
Hard minima:
- export_bytes > 300 KB ⇒ Tier escalates
- persistence_events > 5 ⇒ Tier escalates
- scope_expansions > 2 ⇒ Tier escalates
Counters included in GCP Merkle root.

## 5) Multi-Agent Re-Sync Handshake (No CRO)
- exchange: Core_hash, EGS_hash, metric_def_hash, drift_cap_hash
- mismatch: SAFE_MODE + local-only Tier 0 allowed (non-propagating)
- exit SAFE_MODE: verified alignment OR Governance override token

## 6) γ Demoted to Constraint Gate Only
γ is scope/consent feasibility:
- γ = 1 if within consent scope (+ objective scope if declared)
- γ = 0 otherwise
No gradients, no alignment optimization.

## 7) Fixed-Point Everywhere
All computations in fixed-point basis points; replay uses identical integer arithmetic.

## 8) Governance Touchpoint (Single TTL)
governance_affirm_ttl_days default 30.
On expiry: derived state falls to CS0 constraints until renewed.

Outcome:
- no farmable progression
- no offline stall beyond governance TTL
- reduced poisoning surface (bounded step + freeze on volatility)
- deterministic replay
- mismatch containment without CRO loops
- γ constrained to legality-safe permission feasibility
