# VE Replay Report

`ve_replay_report.py` renders forensic replay output into operator-readable reports.

It produces:

- HTML HUD-style report
- Markdown summary report

The signed JSONL audit chain remains the evidence source. The report is a readable surface over replay results.

## Run

```powershell
py -3.11 ve_replay_report.py `
  --ledger ve_data/gate_pipeline_audit.jsonl `
  --html-out ve_data/gate_replay_report.html `
  --markdown-out ve_data/gate_replay_report.md
```

## What It Shows

- audit chain validity
- records replayed
- advisory events
- adverse events
- classifier changes
- max twin delta
- per-session summaries
- per-record replay class

## Rule

Readable report surfaces do not replace signed audit evidence.
