from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

from ve_gate_replay import replay_gate_audit


def render_html(summary: dict) -> str:
    sessions = "\n".join(
        "<tr>"
        f"<td>{escape(item['pairing_id'])}</td>"
        f"<td>{item['records']}</td>"
        f"<td>{item['advisory_events']}</td>"
        f"<td>{item['adverse_events']}</td>"
        f"<td>{item['classifier_changes']}</td>"
        f"<td>{item['max_twin_delta']:.3f}</td>"
        "</tr>"
        for item in summary["sessions"]
    )
    records = "\n".join(
        "<tr>"
        f"<td>{escape(item['trace_id'])}</td>"
        f"<td>{escape(item['pairing_id'])}</td>"
        f"<td>{escape(item['action_class'])}</td>"
        f"<td>{escape(item['actual_decision'])}</td>"
        f"<td>{escape(item['replay_deviation_class'])}</td>"
        f"<td>{item['twin_delta']:.3f}</td>"
        f"<td>{'yes' if item['classifier_changed'] else 'no'}</td>"
        "</tr>"
        for item in summary["records"]
    )
    chain_status = "VALID" if summary["audit_chain_valid"] else "INVALID"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VE Gate Replay Report</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #071014;
      --panel: #0f2027;
      --panel-2: #132a32;
      --ink: #e7fbff;
      --muted: #91aeb7;
      --line: #24515c;
      --accent: #26e3c2;
      --warn: #f2b84b;
      --bad: #ff6b6b;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
    }}
    header, main {{
      padding: 28px clamp(20px, 5vw, 64px);
    }}
    header {{
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 4vw, 42px);
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    p {{
      color: var(--muted);
      margin: 0;
      line-height: 1.5;
      max-width: 860px;
    }}
    main {{
      display: grid;
      gap: 28px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
    }}
    article {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      display: grid;
      gap: 8px;
    }}
    article strong {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    article span {{
      font-size: 28px;
      font-weight: 700;
    }}
    .valid {{
      color: var(--accent);
    }}
    .invalid {{
      color: var(--bad);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      background: var(--panel-2);
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    code {{
      color: var(--accent);
    }}
    @media (max-width: 760px) {{
      table {{
        display: block;
        overflow-x: auto;
        white-space: nowrap;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>VE Gate Replay Report</h1>
    <p>Forensic replay of signed gate decisions. This report is a readable surface over the audit chain; the signed JSONL remains the evidence source.</p>
  </header>
  <main>
    <section class="metrics">
      <article><strong>Audit Chain</strong><span class="{'valid' if summary['audit_chain_valid'] else 'invalid'}">{chain_status}</span></article>
      <article><strong>Records Replayed</strong><span>{summary['records_replayed']}</span></article>
      <article><strong>Advisory Events</strong><span>{summary['advisory_events']}</span></article>
      <article><strong>Adverse Events</strong><span>{summary['adverse_events']}</span></article>
      <article><strong>Classifier Changes</strong><span>{summary['classifier_changes']}</span></article>
      <article><strong>Max Twin Delta</strong><span>{summary['max_twin_delta']:.3f}</span></article>
    </section>
    <section>
      <h2>Sessions</h2>
      <table>
        <thead><tr><th>Pairing</th><th>Records</th><th>Advisory</th><th>Adverse</th><th>Classifier Changes</th><th>Max Twin Delta</th></tr></thead>
        <tbody>{sessions}</tbody>
      </table>
    </section>
    <section>
      <h2>Records</h2>
      <table>
        <thead><tr><th>Trace</th><th>Pairing</th><th>Action</th><th>Decision</th><th>Replay Class</th><th>Twin Delta</th><th>Classifier Changed</th></tr></thead>
        <tbody>{records}</tbody>
      </table>
    </section>
    <p>Replay diff shows whether current classifier logic reinterprets historical signed records.</p>
  </main>
</body>
</html>
"""


def render_markdown(summary: dict) -> str:
    status = "VALID" if summary["audit_chain_valid"] else "INVALID"
    session_rows = "\n".join(
        f"| {item['pairing_id']} | {item['records']} | {item['advisory_events']} | {item['adverse_events']} | {item['classifier_changes']} | {item['max_twin_delta']:.3f} |"
        for item in summary["sessions"]
    )
    return f"""# VE Gate Replay Report

| Metric | Value |
| --- | ---: |
| Audit chain | {status} |
| Records replayed | {summary['records_replayed']} |
| Advisory events | {summary['advisory_events']} |
| Adverse events | {summary['adverse_events']} |
| Classifier changes | {summary['classifier_changes']} |
| Max twin delta | {summary['max_twin_delta']:.3f} |

## Sessions

| Pairing | Records | Advisory | Adverse | Classifier Changes | Max Twin Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
{session_rows}
"""


def write_replay_report(ledger: Path, html_out: Path, markdown_out: Path, signing_key: str) -> dict:
    summary = replay_gate_audit(ledger, signing_key)
    html_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    html_out.write_text(render_html(summary), encoding="utf-8")
    markdown_out.write_text(render_markdown(summary), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate VE gate replay HUD-style reports")
    parser.add_argument("--ledger", default="ve_data/gate_pipeline_audit.jsonl")
    parser.add_argument("--html-out", default="ve_data/gate_replay_report.html")
    parser.add_argument("--markdown-out", default="ve_data/gate_replay_report.md")
    parser.add_argument("--signing-key", default="demo-local-signing-key")
    args = parser.parse_args()
    summary = write_replay_report(Path(args.ledger), Path(args.html_out), Path(args.markdown_out), args.signing_key)
    print(f"wrote_reports=true audit_chain_valid={str(summary['audit_chain_valid']).lower()} records={summary['records_replayed']}")
    return 0 if summary["audit_chain_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
