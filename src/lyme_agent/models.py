from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EvidenceGrade(Enum):
    """Evidence quality grades based on study design and reliability."""
    HIGH = "high"  # Systematic reviews, meta-analyses, large RCTs
    MODERATE = "moderate"  # Smaller RCTs, well-designed observational studies
    LOW = "low"  # Case series, case reports, expert opinion
    VERY_LOW = "very_low"  # Unverified, preliminary findings


class StudyDesign(Enum):
    """Types of study designs for evidence scoring."""
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    RANDOMIZED_CONTROLLED_TRIAL = "randomized_controlled_trial"
    COHORT_STUDY = "cohort_study"
    CASE_CONTROL_STUDY = "case_control_study"
    CROSS_SECTIONAL = "cross_sectional"
    CASE_SERIES = "case_series"
    CASE_REPORT = "case_report"
    EXPERT_OPINION = "expert_opinion"
    CLINICAL_TRIAL = "clinical_trial"  # For ClinicalTrials.gov entries
    UNKNOWN = "unknown"


@dataclass
class ResearchItem:
    title: str
    source: str
    url: str
    published_at: datetime | None = None
    summary: str | None = None
    
    # Verification & Quality fields
    is_verified: bool = False
    verification_date: datetime | None = None
    verification_status: str = "pending"  # pending, verified, failed, inconclusive
    
    # Evidence scoring
    evidence_score: float = 0.0  # 0-100 scale
    study_design: StudyDesign = StudyDesign.UNKNOWN
    evidence_grade: EvidenceGrade = EvidenceGrade.LOW
    
    # Additional metadata for verification
    doi: str | None = None
    pmid: str | None = None
    nct_id: str | None = None
    journal_name: str | None = None
    sample_size: int | None = None
    has_control_group: bool = False
    is_randomized: bool = False
    is_blinded: bool = False
    funding_source: str | None = None
    conflicts_of_interest: str | None = None
    
    # Verification notes
    verification_notes: list[str] = field(default_factory=list)
