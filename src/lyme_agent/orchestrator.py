from datetime import datetime
from pathlib import Path

from .config import settings
from .discovery import discover_items
from .emailing import send_email
from .reporting import build_markdown_report, write_report


def run_daily_pipeline(output_dir: Path) -> Path:
    items = discover_items()
    date_text = datetime.now().strftime("%Y-%m-%d")
    body = "\n".join(f"- {item.title}" for item in items) or "- No new items discovered."
    report = build_markdown_report(date_text, body)
    report_path = output_dir / f"daily-report-{date_text}.md"
    write_report(report_path, report)
    send_email(settings.recipient_email, f"Daily research report {date_text}", report)
    return report_path
