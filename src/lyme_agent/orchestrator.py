from datetime import datetime
from pathlib import Path

from .config import settings
from .discovery_real import discover_items
from .emailing import send_email
from .reporting import build_markdown_report, write_report


def _build_body(items) -> str:
    if not items:
        return "## Today's discoveries\n\n- No new items discovered."

    pubmed = [item for item in items if item.source == "PubMed"]
    trials = [item for item in items if item.source == "ClinicalTrials.gov"]
    total = len(items)

    lines = [
        "## Executive Summary",
        f"- {total} new item(s) found today",
        f"- PubMed: {len(pubmed)}",
        f"- ClinicalTrials.gov: {len(trials)}",
        "",
        "## Today's discoveries",
    ]

    for item in items:
        lines.append(f"- [{item.source}] {item.title}")
        if item.url:
            lines.append(f"  - Link: {item.url}")
        if item.summary:
            snippet = item.summary.replace("\n", " ").strip()
            lines.append(f"  - Summary: {snippet[:240]}")
    return "\n".join(lines)


def run_daily_pipeline(output_dir: Path) -> Path:
    items = discover_items()
    date_text = datetime.now().strftime("%Y-%m-%d")
    body = _build_body(items)
    report = build_markdown_report(date_text, body)
    report_path = output_dir / f"daily-report-{date_text}.md"
    write_report(report_path, report)
    subject_prefix = f"{len(items)} new item(s)" if items else "No new items"
    subject = f"Daily research report {date_text} | {subject_prefix}"
    send_email(settings.recipient_email, subject, report)
    return report_path
