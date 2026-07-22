from __future__ import annotations

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from .models import ResearchItem

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV_BASE = "https://clinicaltrials.gov/api/query/study_fields"


def _http_get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _pubmed_items() -> list[ResearchItem]:
    today = datetime.now(timezone.utc).date()
    queries = [
        (
            "recent",
            '("Lyme Disease"[Title/Abstract] OR PTLDS[Title/Abstract] OR '
            '"post-treatment Lyme disease syndrome"[Title/Abstract] OR '
            '"Lyme disease treatment"[Title/Abstract] OR Borrelia[Title/Abstract]) '
            f'AND ("{today - timedelta(days=30)}"[Date - Publication] : "{today}"[Date - Publication])',
        ),
        (
            "latest",
            '("Lyme Disease"[Title/Abstract] OR PTLDS[Title/Abstract] OR '
            '"post-treatment Lyme disease syndrome"[Title/Abstract] OR '
            '"Lyme disease treatment"[Title/Abstract] OR Borrelia[Title/Abstract])',
        ),
    ]
    items: list[ResearchItem] = []
    seen_pmids: set[str] = set()

    for mode, term in queries:
        params = urllib.parse.urlencode(
            {
                "db": "pubmed",
                "term": term,
                "retmax": 8 if mode == "recent" else 5,
                "sort": "pub date",
                "retmode": "xml",
            }
        )
        search_xml = _http_get(f"{PUBMED_BASE}/esearch.fcgi?{params}")
        root = ET.fromstring(search_xml)
        ids = [node.text for node in root.findall(".//Id") if node.text]
        if not ids:
            continue

        fetch_params = urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}
        )
        fetch_xml = _http_get(f"{PUBMED_BASE}/efetch.fcgi?{fetch_params}")
        fetch_root = ET.fromstring(fetch_xml)
        for article in fetch_root.findall(".//PubmedArticle"):
            title = (article.findtext(".//ArticleTitle") or "Untitled PubMed item").strip()
            pmid = (article.findtext(".//PMID") or "").strip()
            if pmid and pmid in seen_pmids:
                continue
            if pmid:
                seen_pmids.add(pmid)
            abstract_nodes = article.findall(".//Abstract/AbstractText")
            abstract = " ".join(
                "".join(node.itertext()).strip()
                for node in abstract_nodes
                if "".join(node.itertext()).strip()
            )
            year = article.findtext(".//PubDate/Year")
            month = article.findtext(".//PubDate/Month") or "01"
            day = article.findtext(".//PubDate/Day") or "01"
            published_at = None
            if year:
                try:
                    published_at = datetime.fromisoformat(f"{year}-{month}-{day}")
                except ValueError:
                    published_at = None
            items.append(
                ResearchItem(
                    title=title,
                    source="PubMed",
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "https://pubmed.ncbi.nlm.nih.gov/",
                    published_at=published_at,
                    summary=abstract[:500] if abstract else None,
                )
            )
        if items:
            break
    return items


def _clinical_trials_items() -> list[ResearchItem]:
    queries = [
        'Lyme OR "post-treatment Lyme disease syndrome" OR PTLDS',
        '"Lyme disease" AND treatment',
    ]
    items: list[ResearchItem] = []
    seen_nct: set[str] = set()
    for expr in queries:
        params = urllib.parse.urlencode(
            {
                "expr": expr,
                "fields": "NCTId,BriefTitle,BriefSummary,StartDate",
                "min_rnk": 1,
                "max_rnk": 8,
                "fmt": "json",
            }
        )
        payload = json.loads(_http_get(f"{CTGOV_BASE}?{params}"))
        for study in payload.get("StudyFieldsResponse", {}).get("StudyFields", []):
            title = (study.get("BriefTitle", ["Untitled trial"])[0] or "Untitled trial").strip()
            nct_id = (study.get("NCTId", [""])[0] or "").strip()
            if nct_id and nct_id in seen_nct:
                continue
            if nct_id:
                seen_nct.add(nct_id)
            summary = (study.get("BriefSummary", [""])[0] or "").strip()
            start_date = (study.get("StartDate", [""])[0] or "").strip()
            published_at = None
            if start_date:
                try:
                    published_at = datetime.fromisoformat(start_date[:10])
                except ValueError:
                    published_at = None
            items.append(
                ResearchItem(
                    title=title,
                    source="ClinicalTrials.gov",
                    url=f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "https://clinicaltrials.gov/",
                    published_at=published_at,
                    summary=summary[:500] if summary else None,
                )
            )
        if items:
            break
    return items


def discover_items() -> list[ResearchItem]:
    items: list[ResearchItem] = []
    for fetcher in (_pubmed_items, _clinical_trials_items):
        try:
            items.extend(fetcher())
        except Exception:
            continue
    seen: set[str] = set()
    unique: list[ResearchItem] = []
    for item in items:
        key = item.url or item.title.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
