from datetime import datetime
from pathlib import Path

from .config import settings
from .discovery_real import discover_items
from .emailing import send_email
from .reporting import build_markdown_report, write_report


def _build_body(items, errors) -> str:
    if not items:
        lines = [
            "## Executive Summary",
            "- No new items discovered",
            "",
            "## Today's discoveries",
            "- No matching items were returned by PubMed or ClinicalTrials.gov.",
        ]
        if errors:
            lines.extend(["", "## Source warnings"])
            for err in errors[:8]:
                lines.append(f"- {err}")
        return "\n".join(lines)

    pubmed = [item for item in items if item.source == "PubMed"]
    trials = [item for item in items if item.source == "ClinicalTrials.gov"]
    total = len(items)

    # Calculate quality summary if evidence scoring is available
    quality_summary = None
    if hasattr(items[0], 'evidence_score') and items[0].evidence_score > 0:
        try:
            from .verification import summarize_evidence_quality
            quality_summary = summarize_evidence_quality(items)
        except Exception:
            pass

    lines = [
        "## Executive Summary",
        f"- {total} new item(s) found today",
        f"- PubMed: {len(pubmed)}",
        f"- ClinicalTrials.gov: {len(trials)}",
    ]
    
    # Add quality summary if available
    if quality_summary:
        lines.extend([
            "",
            "## Evidence Quality Summary",
            f"- Average evidence score: {quality_summary['average_score']}/100",
            f"- High-quality items: {quality_summary['high_quality_count']} ({quality_summary['high_quality_rate']*100:.0f}%)",
            f"- Verified citations: {quality_summary['verified_count']} ({quality_summary['verification_rate']*100:.0f}%)",
            "",
            "### Grade Distribution",
        ])
        for grade, count in quality_summary['grade_distribution'].items():
            lines.append(f"- {grade.title()}: {count}")

    lines.extend([
        "",
        "## Today's discoveries",
    ])

    for item in items:
        # Build item line with evidence grade if available
        grade_info = ""
        if hasattr(item, 'evidence_grade') and item.evidence_grade:
            grade_info = f" [{item.evidence_grade.value.upper()}]"
        
        lines.append(f"- [{item.source}]{grade_info} {item.title}")
        
        if item.url:
            lines.append(f"  - Link: {item.url}")
        
        # Add evidence score if available
        if hasattr(item, 'evidence_score') and item.evidence_score > 0:
            lines.append(f"  - Evidence Score: {item.evidence_score:.1f}/100")
        
        if item.summary:
            snippet = item.summary.replace("\n", " ").strip()
            lines.append(f"  - Summary: {snippet[:240]}")
            
    return "\n".join(lines)


def run_daily_pipeline(output_dir: Path, enable_verification: bool = False) -> Path:
    """Run the daily research pipeline.
    
    Args:
        output_dir: Directory to write reports to
        enable_verification: If True, verify citations and score evidence quality
    """
    discovery = discover_items(
        skip_existing=settings.use_database,
        perform_verification=enable_verification
    )
    items = discovery.items
    errors = discovery.errors
    date_text = datetime.now().strftime("%Y-%m-%d")
    body = _build_body(items, errors)
    report = build_markdown_report(date_text, body)
    report_path = output_dir / f"daily-report-{date_text}.md"
    write_report(report_path, report)
    
    # Save to database if enabled
    if settings.use_database:
        try:
            from .persistence import init_db, save_run, save_research_items
            
            # Initialize database schema if needed
            init_db()
            
            # Save run and get run_id
            run_id = save_run(
                run_date=date_text,
                items_count=len(items),
                errors_count=len(errors),
                report_path=str(report_path)
            )
            
            # Save research items with verification data
            save_research_items(run_id, items)
        except Exception as e:
            errors.append(f"Database persistence failed: {e}")
    
    subject_prefix = f"{len(items)} new item(s)" if items else "No new items"
    subject = f"Daily research report {date_text} | {subject_prefix}"
    send_email(settings.recipient_email, subject, report)
    return report_path
