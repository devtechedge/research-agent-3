from dataclasses import dataclass
from datetime import datetime


@dataclass
class ResearchItem:
    title: str
    source: str
    url: str
    published_at: datetime | None = None
    summary: str | None = None
