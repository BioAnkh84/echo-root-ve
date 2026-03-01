# Echo Kernel v1.0 — Enforcement Spine (Minimal)

## 1. Immutable Kernel Invariants (Non-Tunable)
- Consent sovereignty (explicit, scoped, revocable, atomic)
- Bounded drift (Δ always capped)
- Metric semantic immutability (ρ / γ / Δ meanings cannot change)
- Deterministic replay requirement
- Governance oversight for structural change
- No trust inheritance without proof
- SAFE_MODE on structural uncertainty

## 2. Separation Principle
Gate ≠ Baseline Engine
- Gate: read-only evaluator; emits decision + reason codes; no baseline writes
- Baseline Engine: rate-limited updates; freeze-on-volatility; snapshot/revert capable

## 3. Determinism Requirements
- Fixed-point arithmetic in decision layer
- Quantized thresholds declared and hash-bound
- No float intermediates in Gate decision path
- Gate Context Package (GCP) Merkle-bound
- Every materially relevant action is replayable

## 4. Consent Token Model (First-Class Capability)
Fields:
- scope, duration, risk tier, issuer, revocation state, propagation constraints
Rule:
- Consent ambiguity → containment (never inference)

## 5. PAUSE vs SAFE_MODE (Crisp)
- PAUSE: human judgment required; authority transfer; reversible-only assistance; trust intact
- SAFE_MODE: structural uncertainty (version mismatch, ledger failure, coercion flag); governance escalation required

## 6. Version & Compatibility Contract
Must declare and verify:
- Core hash, Charter hash/version, EGS hash/version, metric definition hash
Mismatch → SAFE_MODE. No silent downgrade.

## 7. Multi-Agent Rule (Cipher/Vexis)
- No baseline sharing without explicit consent
- No raw Δ profile transfer
- Compatibility proofs for interaction
- Least-capability downgrade on mismatch
- Each human pairing is a distinct baseline manifold (no relational equivalence assumption)

## 8. Resource & Edge Constraints
- Rate-limited baseline updates
- Bounded ledger growth; snapshot compression rules
- Degraded-safe mode under memory pressure
- Offline operation permitted; governance TTL enforces conservative derived state
