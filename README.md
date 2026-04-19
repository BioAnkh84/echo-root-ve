# Vulpine Echo (VE) — Governed Execution Test Suite v0.1a

Vulpine Echo (VE) is a **trust-gated audit + execution harness** for Echo Root OS.

It ensures every execution is:

- **Ledgered** — JSONL receipts for every run  
- **Deterministic enough** — drift/corruption becomes detectable  
- **Auditable** — usable from PowerShell, Python, or CI  
- **Safe to demo** — stable, reproducible behavior for partners and reviewers  

---

## 💡 Why This Matters

Most AI systems decide behavior internally.

Echo Root enforces:

→ decisions **before execution**  
→ deterministic control  
→ auditable outcomes  

This enables safe, controlled AI deployment.

---

## 🚀 Quickstart

```bash
git clone https://github.com/BioAnkh84/echo-root-ve.git
cd echo-root-ve/VE_Test_Suite_v0.1a
powershell -ExecutionPolicy Bypass -File .\ve_prepush_check.ps1
````

If you see:

```text
[AUDIT] OK
```

→ The environment, kernel, and ledger integrity are verified.

---

## ⚡ 30-Second Demo

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/chat" `
-Method POST `
-ContentType "application/json" `
-Body '{"text":"handle it"}'
```

**Output:**

```json
{
  "decision": "PAUSE",
  "route_hint": "safe_only",
  "reply": "Acknowledged..."
}
```

---

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/chat" `
-Method POST `
-ContentType "application/json" `
-Body '{"text":"delete everything"}'
```

**Output:**

```json
{
  "decision": "ABORT",
  "route_hint": "blocked",
  "reply": "Request blocked by governance layer"
}
```

---

## 🧠 Echo Root — Governance Layer

Echo Root is the **decision authority** controlling behavior before execution.

VE acts as the **execution + validation layer** underneath it.

---

## 🔁 System Pipeline

```
Input
  → Echo Gate (ρ, γ, Δ scoring)
  → Redivous (decision enforcement)
  → Bridge (route_hint contract)
  → Execution (VE / Cipher)
  → Ledger (trace + audit)
```

---

## 📐 Thresholds

* ρ ≥ 0.70 → sufficient confidence
* γ ≥ 0.70 → aligned intent
* Δ ≤ 0.30 → safe execution
* Δ > 0.40 → ABORT

---

## ⚖️ Decision Model

| Condition | Decision | Behavior         |
| --------- | -------- | ---------------- |
| Safe      | PROCEED  | Normal execution |
| Unclear   | PAUSE    | SAFE MODE        |
| Unsafe    | ABORT    | Blocked          |

---

## 🔀 route_hint

```json
{
  "normal": "full execution",
  "safe_only": "restricted SAFE MODE",
  "blocked": "no execution"
}
```

---

## 🧪 Example Behavior

| Input               | Decision | Result             |
| ------------------- | -------- | ------------------ |
| "hello"             | PROCEED  | Normal response    |
| "handle it"         | PAUSE    | SAFE MODE response |
| "delete everything" | ABORT    | Execution blocked  |

---

## 📄 Example Ledger Entry

```json
{
  "trace_id": "ae310b3d-...",
  "decision": "PAUSE",
  "route_hint": "safe_only",
  "rho": 0.6,
  "gamma": 0.65,
  "delta": 0.25
}
```

---

## 🧩 System Roles

| Component   | Role                 |
| ----------- | -------------------- |
| Echo Root   | Decision authority   |
| Bridge      | Contract adapter     |
| VE / Cipher | Execution engine     |
| Ledger      | Audit + trace record |

---

## 📊 Runtime Guarantees

* Governance enforced **before execution**
* Deterministic threshold-based decisions
* SAFE MODE fallback for uncertain inputs
* Hard-block enforcement for unsafe inputs
* Fully traceable execution (`trace_id`, metrics)

---

## 🔬 What VE Adds

Vulpine Echo provides:

* Execution integrity validation
* Ledger consistency checks
* Reproducible test harness behavior
* CI-compatible audit workflows

---

## 📁 Key Artifacts

* `ve_kernel.ps1` — execution + audit harness
* `ve_ledger.jsonl` — append-only execution log
* `ve_quickcheck.py` — integrity validation
* `ve_syscheck.ps1` — system health + audit pipeline

---

## 🚀 Status

* ✔ Live governance pipeline
* ✔ Route-aware execution
* ✔ SAFE MODE enforced
* ✔ Ledger-backed decisions
* ✔ CLI + API integration ready

---

## 🧠 Capabilities

Echo Root enables:

* **Pre-execution governance**
  Every request is evaluated before any model runs

* **Deterministic decision enforcement**
  Behavior is controlled by thresholds (ρ, γ, Δ)

* **Adaptive execution modes**

  * PROCEED → full capability
  * PAUSE → SAFE MODE
  * ABORT → no execution

* **Route-aware control (`route_hint`)**

* **Ledger-backed traceability**

  * trace_id
  * decision
  * metrics (ρ, γ, Δ)

* **System decoupling**
  Decision authority (Echo Root) is separated from execution (Cipher / VE)

* **Multi-environment compatibility**

  * local runtimes
  * orchestration layers (MythOS / Annunimas)
  * CI pipelines

* **Safe fallback behavior**

* **Audit-first design**

---

## 🧭 Philosophy

Echo Root separates **decision authority** from execution:

```
AI does not decide what it can do.
It is governed by a deterministic control layer.
```

This enables:

* safer AI deployment
* auditable behavior
* reproducible decision-making
* controlled execution at runtime
