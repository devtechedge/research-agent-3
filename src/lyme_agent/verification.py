"""Citation verification and evidence scoring module.

This module provides functionality to:
1. Verify citations by checking if URLs/PMIDs/NCT IDs are accessible and valid
2. Score evidence based on study design, sample size, and other quality indicators
3. Grade evidence using established hierarchies (e.g., Oxford CEBM levels)
"""

from __future__ import annotations

import logging
import re
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Tuple

from .models import ResearchItem, EvidenceGrade, StudyDesign

LOG = logging.getLogger(__name__)


def verify_citation(item: ResearchItem) -> Tuple[bool, str, list[str]]:
    """Verify a citation by checking accessibility and extracting metadata.
    
    Args:
        item: The research item to verify
        
    Returns:
        Tuple of (is_verified, status, notes)
        - is_verified: True if citation appears valid and accessible
        - status: One of 'verified', 'failed', 'inconclusive', 'pending'
        - notes: List of verification notes/messages
    """
    notes = []
    
    # Skip verification for items without URLs
    if not item.url:
        notes.append("No URL provided for verification")
        return False, "pending", notes
    
    try:
        # Create request with appropriate headers
        request = urllib.request.Request(
            item.url,
            headers={
                "User-Agent": "LymeWatch/0.1 (+https://github.com/devtechedge/research-agent-3)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        
        # Try to access the URL with timeout
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status == 200:
                notes.append(f"URL accessible (HTTP {response.status})")
                
                # Extract additional metadata if possible
                content_type = response.headers.get('Content-Type', '')
                notes.append(f"Content type: {content_type}")
                
                # Mark as verified
                return True, "verified", notes
            else:
                notes.append(f"URL returned HTTP {response.status}")
                return False, "failed", notes
                
    except urllib.error.HTTPError as e:
        notes.append(f"HTTP error accessing URL: {e.code} {e.reason}")
        if e.code == 404:
            return False, "failed", notes
        elif e.code in [500, 502, 503, 504]:
            notes.append("Server error - may be temporary")
            return False, "inconclusive", notes
        return False, "failed", notes
        
    except urllib.error.URLError as e:
        notes.append(f"URL error: {e.reason}")
        return False, "failed", notes
        
    except TimeoutError:
        notes.append("Request timed out")
        return False, "inconclusive", notes
        
    except Exception as e:
        notes.append(f"Verification failed: {str(e)}")
        return False, "failed", notes


def detect_study_design(item: ResearchItem) -> StudyDesign:
    """Detect study design from title, summary, and source.
    
    Uses keyword matching and heuristics to classify study design.
    
    Args:
        item: The research item to analyze
        
    Returns:
        StudyDesign enum value
    """
    text = f"{item.title or ''} {item.summary or ''}".lower()
    
    # Check for systematic reviews and meta-analyses
    if any(kw in text for kw in ['systematic review', 'meta-analysis', 'meta analysis']):
        if 'meta-analysis' in text or 'meta analysis' in text:
            return StudyDesign.META_ANALYSIS
        return StudyDesign.SYSTEMATIC_REVIEW
    
    # Check for randomized controlled trials
    rct_keywords = [
        'randomized controlled trial', 'randomised controlled trial',
        'rct', 'randomized trial', 'randomised trial',
        'placebo-controlled', 'placebo controlled'
    ]
    if any(kw in text for kw in rct_keywords):
        return StudyDesign.RANDOMIZED_CONTROLLED_TRIAL
    
    # Check for cohort studies
    cohort_keywords = ['cohort study', 'prospective cohort', 'retrospective cohort', 'longitudinal']
    if any(kw in text for kw in cohort_keywords):
        return StudyDesign.COHORT_STUDY
    
    # Check for case-control studies
    if 'case-control' in text or 'case control' in text or 'case–control' in text:
        return StudyDesign.CASE_CONTROL_STUDY
    
    # Check for cross-sectional studies
    if 'cross-sectional' in text or 'cross sectional' in text or 'prevalence study' in text:
        return StudyDesign.CROSS_SECTIONAL
    
    # Check for case series
    if 'case series' in text or 'series of cases' in text:
        return StudyDesign.CASE_SERIES
    
    # Check for case reports
    if 'case report' in text or 'case study' in text or 'single case' in text:
        return StudyDesign.CASE_REPORT
    
    # Check for clinical trials (from ClinicalTrials.gov)
    if item.source == "ClinicalTrials.gov" or (item.nct_id is not None):
        return StudyDesign.CLINICAL_TRIAL
    
    # Check for expert opinion / editorials
    expert_keywords = ['editorial', 'commentary', 'opinion', 'perspective', 'viewpoint']
    if any(kw in text for kw in expert_keywords):
        return StudyDesign.EXPERT_OPINION
    
    return StudyDesign.UNKNOWN


def extract_metadata(item: ResearchItem) -> None:
    """Extract additional metadata from title, summary, and URL.
    
    Populates fields like pmid, nct_id, doi, journal_name, etc.
    
    Args:
        item: The research item to extract metadata from (modified in place)
    """
    # Extract PMID from URL or text
    if item.source == "PubMed":
        pubmed_pattern = r'pubmed\.nih\.gov/(\d+)'
        match = re.search(pubmed_pattern, item.url or '')
        if match:
            item.pmid = match.group(1)
        else:
            # Try to find PMID in title/summary
            pmid_text_pattern = r'PMID[:\s]+(\d+)'
            match = re.search(pmid_text_pattern, f"{item.title or ''} {item.summary or ''}", re.IGNORECASE)
            if match:
                item.pmid = match.group(1)
        
        # If still no PMID, try extracting from URL path more broadly
        if not item.pmid and item.url:
            url_pmid_pattern = r'/(\d+)/?$'
            match = re.search(url_pmid_pattern, item.url)
            if match:
                item.pmid = match.group(1)
    
    # Extract NCT ID from URL or text
    if item.source == "ClinicalTrials.gov":
        nct_pattern = r'NCT(\d{8})'
        match = re.search(nct_pattern, item.url or '', re.IGNORECASE)
        if match:
            item.nct_id = f"NCT{match.group(1)}"
        else:
            # Try to find NCT ID in title/summary
            nct_text_pattern = r'(NCT\d{8})'
            match = re.search(nct_text_pattern, f"{item.title or ''} {item.summary or ''}", re.IGNORECASE)
            if match:
                item.nct_id = match.group(1).upper()
    
    # Extract DOI
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    match = re.search(doi_pattern, f"{item.title or ''} {item.summary or ''}", re.IGNORECASE)
    if match:
        item.doi = match.group(0)
    
    # Try to extract journal name from PubMed data if available
    if item.source == "PubMed" and item.summary:
        # Look for common journal patterns (simplified)
        journal_patterns = [
            r'published in ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'journal:? ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
        ]
        for pattern in journal_patterns:
            match = re.search(pattern, item.summary, re.IGNORECASE)
            if match:
                item.journal_name = match.group(1)
                break
    
    # Extract sample size indicators
    sample_patterns = [
        r'(\d+)\s*(?:patients?|participants?|subjects?|individuals)',
        r'n\s*=\s*(\d+)',
        r'sample size[:\s]+(\d+)',
    ]
    text = f"{item.title or ''} {item.summary or ''}"
    for pattern in sample_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                item.sample_size = int(match.group(1))
                break
            except ValueError:
                pass
    
    # Detect study characteristics
    text_lower = text.lower()
    item.has_control_group = any(kw in text_lower for kw in [
        'control group', 'control arm', 'comparison group', 'placebo group'
    ])
    item.is_randomized = any(kw in text_lower for kw in [
        'randomized', 'randomised', 'random allocation'
    ])
    item.is_blinded = any(kw in text_lower for kw in [
        'blinded', 'double-blind', 'single-blind', 'masked'
    ])


def calculate_evidence_score(item: ResearchItem) -> float:
    """Calculate an evidence quality score (0-100) for a research item.
    
    Scoring factors:
    - Study design (0-40 points)
    - Sample size (0-25 points)
    - Methodological quality (randomization, blinding, control) (0-25 points)
    - Recency (0-10 points)
    
    Args:
        item: The research item to score
        
    Returns:
        Evidence score from 0 to 100
    """
    score = 0.0
    
    # Study design score (0-40 points)
    design_scores = {
        StudyDesign.META_ANALYSIS: 40,
        StudyDesign.SYSTEMATIC_REVIEW: 38,
        StudyDesign.RANDOMIZED_CONTROLLED_TRIAL: 35,
        StudyDesign.COHORT_STUDY: 28,
        StudyDesign.CASE_CONTROL_STUDY: 25,
        StudyDesign.CROSS_SECTIONAL: 20,
        StudyDesign.CLINICAL_TRIAL: 30,  # Pending completion
        StudyDesign.CASE_SERIES: 15,
        StudyDesign.CASE_REPORT: 10,
        StudyDesign.EXPERT_OPINION: 8,
        StudyDesign.UNKNOWN: 15,  # Default moderate score for unknown
    }
    score += design_scores.get(item.study_design, 15)
    
    # Sample size score (0-25 points)
    if item.sample_size:
        if item.sample_size >= 1000:
            score += 25
        elif item.sample_size >= 500:
            score += 22
        elif item.sample_size >= 200:
            score += 18
        elif item.sample_size >= 100:
            score += 14
        elif item.sample_size >= 50:
            score += 10
        elif item.sample_size >= 20:
            score += 6
        else:
            score += 3
    else:
        # No sample size info - assume moderate
        score += 10
    
    # Methodological quality score (0-25 points)
    method_score = 0
    if item.has_control_group:
        method_score += 10
    if item.is_randomized:
        method_score += 10
    if item.is_blinded:
        method_score += 5
    score += min(method_score, 25)
    
    # Recency score (0-10 points)
    if item.published_at:
        days_old = (datetime.now() - item.published_at).days
        if days_old <= 365:  # Within last year
            score += 10
        elif days_old <= 730:  # Within last 2 years
            score += 8
        elif days_old <= 1825:  # Within last 5 years
            score += 6
        elif days_old <= 3650:  # Within last 10 years
            score += 3
        else:
            score += 1
    else:
        # Unknown date - moderate score
        score += 5
    
    return min(score, 100.0)


def assign_evidence_grade(score: float, study_design: StudyDesign) -> EvidenceGrade:
    """Assign an evidence grade based on score and study design.
    
    Args:
        score: Evidence score (0-100)
        study_design: The study design type
        
    Returns:
        EvidenceGrade enum value
    """
    # High-grade studies require both good design and high score
    if study_design in [StudyDesign.META_ANALYSIS, StudyDesign.SYSTEMATIC_REVIEW]:
        if score >= 70:
            return EvidenceGrade.HIGH
        elif score >= 50:
            return EvidenceGrade.MODERATE
    
    if study_design == StudyDesign.RANDOMIZED_CONTROLLED_TRIAL:
        if score >= 75:
            return EvidenceGrade.HIGH
        elif score >= 55:
            return EvidenceGrade.MODERATE
        elif score >= 35:
            return EvidenceGrade.LOW
    
    # Observational studies
    if study_design in [StudyDesign.COHORT_STUDY, StudyDesign.CASE_CONTROL_STUDY]:
        if score >= 70:
            return EvidenceGrade.MODERATE
        elif score >= 45:
            return EvidenceGrade.LOW
        else:
            return EvidenceGrade.VERY_LOW
    
    # Clinical trials (ongoing)
    if study_design == StudyDesign.CLINICAL_TRIAL:
        return EvidenceGrade.MODERATE  # Pending completion reduces grade
    
    # Lower-tier evidence
    if study_design in [StudyDesign.CASE_SERIES, StudyDesign.CASE_REPORT, StudyDesign.EXPERT_OPINION]:
        if score >= 50:
            return EvidenceGrade.LOW
        else:
            return EvidenceGrade.VERY_LOW
    
    # Unknown design - conservative grading
    if score >= 70:
        return EvidenceGrade.MODERATE
    elif score >= 40:
        return EvidenceGrade.LOW
    else:
        return EvidenceGrade.VERY_LOW


def assess_item_quality(item: ResearchItem) -> None:
    """Perform complete quality assessment on a research item.
    
    This function:
    1. Extracts metadata (PMID, NCT ID, DOI, etc.)
    2. Detects study design
    3. Calculates evidence score
    4. Assigns evidence grade
    
    Args:
        item: The research item to assess (modified in place)
    """
    # Extract metadata first
    extract_metadata(item)
    
    # Detect study design
    item.study_design = detect_study_design(item)
    
    # Calculate evidence score
    item.evidence_score = calculate_evidence_score(item)
    
    # Assign evidence grade
    item.evidence_grade = assign_evidence_grade(item.evidence_score, item.study_design)


def verify_and_score_items(items: list[ResearchItem], skip_verification: bool = False) -> list[ResearchItem]:
    """Verify citations and score evidence for a list of research items.
    
    Args:
        items: List of research items to process
        skip_verification: If True, skip URL verification (faster, less accurate)
        
    Returns:
        List of processed research items with updated quality metrics
    """
    LOG.info(f"Starting quality assessment for {len(items)} items")
    
    for i, item in enumerate(items):
        LOG.debug(f"Processing item {i+1}/{len(items)}: {item.title[:50]}...")
        
        # Perform quality assessment (metadata extraction, study design, scoring)
        assess_item_quality(item)
        
        # Verify citation if not skipped
        if not skip_verification:
            try:
                is_verified, status, notes = verify_citation(item)
                item.is_verified = is_verified
                item.verification_status = status
                item.verification_date = datetime.now()
                item.verification_notes.extend(notes)
                LOG.debug(f"Verification result: {status} - {notes[0] if notes else 'No notes'}")
            except Exception as e:
                LOG.warning(f"Verification failed for item: {e}")
                item.verification_status = "failed"
                item.verification_notes.append(f"Verification error: {str(e)}")
        else:
            item.verification_status = "pending"
            item.verification_notes.append("Verification skipped")
    
    LOG.info(f"Completed quality assessment for {len(items)} items")
    return items


def get_high_quality_items(items: list[ResearchItem], min_score: float = 70.0) -> list[ResearchItem]:
    """Filter items to return only high-quality evidence.
    
    Args:
        items: List of research items to filter
        min_score: Minimum evidence score threshold
        
    Returns:
        List of high-quality items
    """
    return [
        item for item in items
        if item.evidence_score >= min_score
        and item.evidence_grade in [EvidenceGrade.HIGH, EvidenceGrade.MODERATE]
    ]


def summarize_evidence_quality(items: list[ResearchItem]) -> dict:
    """Generate a summary of evidence quality across items.
    
    Args:
        items: List of research items to summarize
        
    Returns:
        Dictionary with quality summary statistics
    """
    if not items:
        return {
            'total_items': 0,
            'verified_count': 0,
            'grade_distribution': {},
            'average_score': 0,
            'high_quality_count': 0,
        }
    
    grade_counts = {}
    for item in items:
        grade = item.evidence_grade.value
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    verified_count = sum(1 for item in items if item.is_verified)
    high_quality_count = sum(
        1 for item in items
        if item.evidence_grade in [EvidenceGrade.HIGH, EvidenceGrade.MODERATE]
    )
    
    avg_score = sum(item.evidence_score for item in items) / len(items)
    
    return {
        'total_items': len(items),
        'verified_count': verified_count,
        'verification_rate': verified_count / len(items),
        'grade_distribution': grade_counts,
        'average_score': round(avg_score, 2),
        'high_quality_count': high_quality_count,
        'high_quality_rate': high_quality_count / len(items),
    }
