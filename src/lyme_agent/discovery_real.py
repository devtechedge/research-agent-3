from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from dataclasses import dataclass, field

from .models import ResearchItem

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTGOV_BASE = "https://clinicaltrials.gov/api/query/study_fields"
LOG = logging.getLogger(__name__)


@dataclass
class DiscoveryResult:
    items: list[ResearchItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _http_get(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "LymeWatch/0.1 (+https://github.com/devtechedge/research-agent-3)",
            "Accept": "application/json,text/xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _pubmed_items() -> tuple[list[ResearchItem], list[str]]:
    query = '("Lyme Disease"[Title/Abstract] OR PTLDS[Title/Abstract] OR "post-treatment Lyme disease syndrome"[Title/Abstract] OR "Lyme disease treatment"[Title/Abstract] OR Borrelia[Title/Abstract])'
    items: list[ResearchItem] = []
    seen_pmids: set[str] = set()
    errors: list[str] = []
    search_specs = [
        {"reldate": 30, "retmax": 10},
        {"reldate": 3650, "retmax": 6},
    ]
    for spec in search_specs:
        params = urllib.parse.urlencode(
            {
                "db": "pubmed",
                "term": query,
                "reldate": spec["reldate"],
                "datetype": "pdat",
                "sort": "pub date",
                "retmax": spec["retmax"],
                "retmode": "xml",
                "tool": "LymeWatch",
                "email": "devayanmandal@gmail.com",
            }
        )
        try:
            search_xml = _http_get(f"{PUBMED_BASE}/esearch.fcgi?{params}")
            root = ET.fromstring(search_xml)
            ids = [node.text for node in root.findall(".//Id") if node.text]
            if not ids:
                continue

            fetch_params = urllib.parse.urlencode(
                {"db": "pubmed", "id": ",".join(ids), "retmode": "xml", "tool": "LymeWatch"}
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
        except Exception as exc:
            LOG.warning("PubMed lookup failed for reldate=%s: %s", spec["reldate"], exc)
            errors.append(f"PubMed reldate={spec['reldate']}: {exc}")
    return items, errors


def _clinical_trials_items() -> tuple[list[ResearchItem], list[str]]:
    queries = [
        'Lyme OR "post-treatment Lyme disease syndrome" OR PTLDS',
        '"Lyme disease" AND treatment',
    ]
    items: list[ResearchItem] = []
    seen_nct: set[str] = set()
    errors: list[str] = []
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
        try:
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
        except Exception as exc:
            LOG.warning("ClinicalTrials.gov lookup failed for expr=%r: %s", expr, exc)
            errors.append(f"ClinicalTrials.gov expr={expr!r}: {exc}")
    return items, errors


def discover_items(skip_existing: bool = True, perform_verification: bool = False) -> DiscoveryResult:
    """Discover research items from PubMed and ClinicalTrials.gov.
    
    Args:
        skip_existing: If True, filter out items already in the database.
        perform_verification: If True, verify citations and score evidence quality.
    """
    result = DiscoveryResult()
    for fetcher in (_pubmed_items, _clinical_trials_items):
        try:
            items, errors = fetcher()
            result.items.extend(items)
            result.errors.extend(errors)
        except Exception as exc:
            result.errors.append(str(exc))
    
    # Deduplicate by URL/title
    seen: set[str] = set()
    unique: list[ResearchItem] = []
    for item in result.items:
        key = item.url or item.title.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    
    # Filter out items already in database if persistence is enabled
    if skip_existing and settings.use_database:
        try:
            from .persistence import get_existing_urls
            sources = list(set(item.source for item in unique))
            existing_urls = get_existing_urls(sources)
            unique = [item for item in unique if item.url not in existing_urls]
            LOG.info(f"Filtered out duplicates, {len(unique)} new items remain")
        except Exception as exc:
            LOG.warning(f"Failed to check existing URLs in database: {exc}")
            result.errors.append(f"Database deduplication failed: {exc}")
    
    # Perform citation verification and evidence scoring if requested
    if perform_verification and unique:
        try:
            from .verification import verify_and_score_items
            LOG.info("Starting citation verification and evidence scoring...")
            unique = verify_and_score_items(unique, skip_verification=False)
            
            # Log quality summary
            from .verification import summarize_evidence_quality
            quality_summary = summarize_evidence_quality(unique)
            LOG.info(f"Quality assessment complete: {quality_summary}")
        except Exception as exc:
            LOG.warning(f"Verification/scoring failed: {exc}")
            result.errors.append(f"Verification failed: {exc}")
    
    result.items = unique
    return result
