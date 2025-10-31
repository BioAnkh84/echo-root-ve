# Vulpine Echo (VE) – Test Suite v0.1a

Vulpine Echo (VE) is a **trust-gated audit + exec harness** for Echo Root OS. It’s designed to prove that every run is:
- **Ledgered** (JSONL receipts)
- **Deterministic enough** to catch corruption
- **Auditable** from PowerShell, Python, or CI
- **Safe to demo** to partners (Grok, Gemini, internal)

## Quickstart

git clone https://github.com/BioAnkh84/echo-root-ve.git
cd .\echo-root-ve\VE_Test_Suite_v0.1a
powershell -ExecutionPolicy Bypass -File .\ve_prepush_check.ps1

If it prints [AUDIT] OK, VE, and Windows, you’re clean.
