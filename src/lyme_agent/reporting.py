from pathlib import Path


def build_markdown_report(date_text: str, body: str) -> str:
    return f"# Daily Research Report - {date_text}\n\n{body}\n"


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
