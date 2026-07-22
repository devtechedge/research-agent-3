"""Tests for verification and evidence scoring module."""

import pytest
from datetime import datetime, timedelta

from src.lyme_agent.models import (
    ResearchItem, EvidenceGrade, StudyDesign
)
from src.lyme_agent.verification import (
    verify_citation,
    detect_study_design,
    extract_metadata,
    calculate_evidence_score,
    assign_evidence_grade,
    assess_item_quality,
    verify_and_score_items,
    get_high_quality_items,
    summarize_evidence_quality,
)


class TestDetectStudyDesign:
    """Test study design detection from text."""
    
    def test_detects_meta_analysis(self):
        item = ResearchItem(
            title="Meta-Analysis of Lyme Disease Treatments",
            source="PubMed",
            url="https://example.com/1"
        )
        assert detect_study_design(item) == StudyDesign.META_ANALYSIS
    
    def test_detects_systematic_review(self):
        item = ResearchItem(
            title="Systematic Review of PTLDS Interventions",
            source="PubMed",
            url="https://example.com/2"
        )
        assert detect_study_design(item) == StudyDesign.SYSTEMATIC_REVIEW
    
    def test_detects_rct(self):
        item = ResearchItem(
            title="Randomized Controlled Trial of Doxycycline",
            source="PubMed",
            url="https://example.com/3"
        )
        assert detect_study_design(item) == StudyDesign.RANDOMIZED_CONTROLLED_TRIAL
    
    def test_detects_placebo_controlled(self):
        item = ResearchItem(
            title="Placebo-controlled trial of antibiotic therapy",
            source="PubMed",
            url="https://example.com/4"
        )
        assert detect_study_design(item) == StudyDesign.RANDOMIZED_CONTROLLED_TRIAL
    
    def test_detects_cohort_study(self):
        item = ResearchItem(
            title="Prospective cohort study of Lyme patients",
            source="PubMed",
            url="https://example.com/5"
        )
        assert detect_study_design(item) == StudyDesign.COHORT_STUDY
    
    def test_detects_case_control(self):
        item = ResearchItem(
            title="Case-control study of risk factors",
            source="PubMed",
            url="https://example.com/6"
        )
        assert detect_study_design(item) == StudyDesign.CASE_CONTROL_STUDY
    
    def test_detects_case_series(self):
        item = ResearchItem(
            title="Case series of 20 patients with Lyme carditis",
            source="PubMed",
            url="https://example.com/7"
        )
        assert detect_study_design(item) == StudyDesign.CASE_SERIES
    
    def test_detects_case_report(self):
        item = ResearchItem(
            title="Case report: unusual presentation",
            source="PubMed",
            url="https://example.com/8"
        )
        assert detect_study_design(item) == StudyDesign.CASE_REPORT
    
    def test_detects_clinical_trial_from_source(self):
        item = ResearchItem(
            title="Study of new diagnostic test",
            source="ClinicalTrials.gov",
            url="https://clinicaltrials.gov/study/NCT12345678"
        )
        assert detect_study_design(item) == StudyDesign.CLINICAL_TRIAL
    
    def test_detects_expert_opinion(self):
        item = ResearchItem(
            title="Editorial: perspectives on Lyme research",
            source="PubMed",
            url="https://example.com/9"
        )
        assert detect_study_design(item) == StudyDesign.EXPERT_OPINION
    
    def test_unknown_design(self):
        item = ResearchItem(
            title="Some study about stuff",
            source="PubMed",
            url="https://example.com/10"
        )
        assert detect_study_design(item) == StudyDesign.UNKNOWN


class TestExtractMetadata:
    """Test metadata extraction from items."""
    
    def test_extracts_pmid_from_url(self):
        item = ResearchItem(
            title="Test",
            source="PubMed",
            url="https://pubmed.ncbi.nlm.nih.gov/12345678/"
        )
        extract_metadata(item)
        assert item.pmid == "12345678"
    
    def test_extracts_nct_id_from_url(self):
        item = ResearchItem(
            title="Test",
            source="ClinicalTrials.gov",
            url="https://clinicaltrials.gov/study/NCT12345678"
        )
        extract_metadata(item)
        assert item.nct_id == "NCT12345678"
    
    def test_extracts_sample_size(self):
        item = ResearchItem(
            title="Study with 150 patients",
            source="PubMed",
            url="https://example.com",
            summary="This study enrolled 150 participants over 2 years."
        )
        extract_metadata(item)
        assert item.sample_size == 150
    
    def test_extracts_sample_size_n_format(self):
        item = ResearchItem(
            title="Test",
            source="PubMed",
            url="https://example.com",
            summary="We studied 200 subjects (n=200) in this trial."
        )
        extract_metadata(item)
        assert item.sample_size == 200
    
    def test_detects_control_group(self):
        item = ResearchItem(
            title="Test",
            source="PubMed",
            url="https://example.com",
            summary="Patients were assigned to treatment or control group."
        )
        extract_metadata(item)
        assert item.has_control_group is True
    
    def test_detects_randomization(self):
        item = ResearchItem(
            title="Test",
            source="PubMed",
            url="https://example.com",
            summary="Participants were randomized to receive intervention."
        )
        extract_metadata(item)
        assert item.is_randomized is True
    
    def test_detects_blinding(self):
        item = ResearchItem(
            title="Test",
            source="PubMed",
            url="https://example.com",
            summary="This was a double-blind study."
        )
        extract_metadata(item)
        assert item.is_blinded is True


class TestCalculateEvidenceScore:
    """Test evidence score calculation."""
    
    def test_high_score_for_meta_analysis(self):
        item = ResearchItem(
            title="Meta-Analysis",
            source="PubMed",
            url="https://example.com",
            study_design=StudyDesign.META_ANALYSIS,
            sample_size=5000,
            published_at=datetime.now() - timedelta(days=100)
        )
        score = calculate_evidence_score(item)
        assert score >= 70  # Should be high quality
    
    def test_low_score_for_case_report(self):
        item = ResearchItem(
            title="Case Report",
            source="PubMed",
            url="https://example.com",
            study_design=StudyDesign.CASE_REPORT,
            sample_size=1,
            published_at=datetime.now() - timedelta(days=100)
        )
        score = calculate_evidence_score(item)
        assert score < 40  # Should be low quality
    
    def test_score_increases_with_sample_size(self):
        small = ResearchItem(
            title="Small study",
            source="PubMed",
            url="https://example.com/1",
            sample_size=20
        )
        large = ResearchItem(
            title="Large study",
            source="PubMed",
            url="https://example.com/2",
            sample_size=1000
        )
        assert calculate_evidence_score(large) > calculate_evidence_score(small)
    
    def test_score_increases_with_methodological_quality(self):
        basic = ResearchItem(
            title="Basic study",
            source="PubMed",
            url="https://example.com/1"
        )
        rigorous = ResearchItem(
            title="Rigorous study",
            source="PubMed",
            url="https://example.com/2",
            has_control_group=True,
            is_randomized=True,
            is_blinded=True
        )
        assert calculate_evidence_score(rigorous) > calculate_evidence_score(basic)
    
    def test_recent_studies_score_higher(self):
        old = ResearchItem(
            title="Old study",
            source="PubMed",
            url="https://example.com/1",
            published_at=datetime.now() - timedelta(days=2000)
        )
        recent = ResearchItem(
            title="Recent study",
            source="PubMed",
            url="https://example.com/2",
            published_at=datetime.now() - timedelta(days=100)
        )
        assert calculate_evidence_score(recent) > calculate_evidence_score(old)
    
    def test_score_bounds(self):
        item = ResearchItem(
            title="Test",
            source="PubMed",
            url="https://example.com"
        )
        score = calculate_evidence_score(item)
        assert 0 <= score <= 100


class TestAssignEvidenceGrade:
    """Test evidence grade assignment."""
    
    def test_high_grade_for_high_score_meta_analysis(self):
        grade = assign_evidence_grade(80, StudyDesign.META_ANALYSIS)
        assert grade == EvidenceGrade.HIGH
    
    def test_moderate_grade_for_medium_score_meta_analysis(self):
        grade = assign_evidence_grade(55, StudyDesign.META_ANALYSIS)
        assert grade == EvidenceGrade.MODERATE
    
    def test_high_grade_for_high_score_rct(self):
        grade = assign_evidence_grade(80, StudyDesign.RANDOMIZED_CONTROLLED_TRIAL)
        assert grade == EvidenceGrade.HIGH
    
    def test_low_grade_for_case_report(self):
        grade = assign_evidence_grade(30, StudyDesign.CASE_REPORT)
        assert grade == EvidenceGrade.VERY_LOW
    
    def test_moderate_grade_for_clinical_trial(self):
        grade = assign_evidence_grade(50, StudyDesign.CLINICAL_TRIAL)
        assert grade == EvidenceGrade.MODERATE


class TestAssessItemQuality:
    """Test complete quality assessment."""
    
    def test_full_assessment(self):
        item = ResearchItem(
            title="Randomized controlled trial with 200 patients",
            source="PubMed",
            url="https://pubmed.ncbi.nlm.nih.gov/12345/",
            summary="Double-blind, placebo-controlled RCT with 200 participants.",
            published_at=datetime.now() - timedelta(days=100)
        )
        assess_item_quality(item)
        
        assert item.study_design == StudyDesign.RANDOMIZED_CONTROLLED_TRIAL
        assert item.evidence_score > 0
        assert item.evidence_grade in [EvidenceGrade.HIGH, EvidenceGrade.MODERATE, EvidenceGrade.LOW, EvidenceGrade.VERY_LOW]
        assert item.pmid == "12345"
        assert item.sample_size == 200
        assert item.is_randomized is True
        assert item.is_blinded is True


class TestVerifyAndScoreItems:
    """Test batch verification and scoring."""
    
    def test_processes_multiple_items(self):
        items = [
            ResearchItem(
                title="RCT Study",
                source="PubMed",
                url="https://example.com/1"
            ),
            ResearchItem(
                title="Case Report",
                source="PubMed",
                url="https://example.com/2"
            ),
        ]
        result = verify_and_score_items(items, skip_verification=True)
        
        assert len(result) == 2
        assert all(item.evidence_score > 0 for item in result)
        assert all(item.verification_status == "pending" for item in result)
    
    def test_sets_verification_status_when_skipped(self):
        item = ResearchItem(
            title="Test",
            source="PubMed",
            url="https://example.com"
        )
        result = verify_and_score_items([item], skip_verification=True)
        assert result[0].verification_status == "pending"


class TestGetHighQualityItems:
    """Test filtering for high-quality items."""
    
    def test_filters_by_score_and_grade(self):
        items = [
            ResearchItem(
                title="High quality",
                source="PubMed",
                url="https://example.com/1",
                evidence_score=85.0,
                evidence_grade=EvidenceGrade.HIGH
            ),
            ResearchItem(
                title="Low quality",
                source="PubMed",
                url="https://example.com/2",
                evidence_score=25.0,
                evidence_grade=EvidenceGrade.VERY_LOW
            ),
        ]
        high_quality = get_high_quality_items(items, min_score=70.0)
        
        assert len(high_quality) == 1
        assert high_quality[0].title == "High quality"
    
    def test_returns_empty_when_no_high_quality(self):
        items = [
            ResearchItem(
                title="Low quality",
                source="PubMed",
                url="https://example.com",
                evidence_score=25.0,
                evidence_grade=EvidenceGrade.VERY_LOW
            ),
        ]
        high_quality = get_high_quality_items(items, min_score=70.0)
        assert len(high_quality) == 0


class TestSummarizeEvidenceQuality:
    """Test quality summary generation."""
    
    def test_summary_statistics(self):
        items = [
            ResearchItem(
                title="High 1",
                source="PubMed",
                url="https://example.com/1",
                evidence_score=85.0,
                evidence_grade=EvidenceGrade.HIGH,
                is_verified=True
            ),
            ResearchItem(
                title="High 2",
                source="PubMed",
                url="https://example.com/2",
                evidence_score=90.0,
                evidence_grade=EvidenceGrade.HIGH,
                is_verified=True
            ),
            ResearchItem(
                title="Low",
                source="PubMed",
                url="https://example.com/3",
                evidence_score=25.0,
                evidence_grade=EvidenceGrade.VERY_LOW,
                is_verified=False
            ),
        ]
        summary = summarize_evidence_quality(items)
        
        assert summary['total_items'] == 3
        assert summary['verified_count'] == 2
        assert summary['high_quality_count'] == 2
        assert abs(summary['average_score'] - 66.67) < 0.1
        assert 'high' in summary['grade_distribution']
        assert 'very_low' in summary['grade_distribution']
    
    def test_empty_items(self):
        summary = summarize_evidence_quality([])
        assert summary['total_items'] == 0
        assert summary['average_score'] == 0


class TestVerifyCitation:
    """Test citation verification."""
    
    def test_skip_without_url(self):
        item = ResearchItem(
            title="No URL",
            source="PubMed",
            url=""
        )
        is_verified, status, notes = verify_citation(item)
        assert is_verified is False
        assert status == "pending"
        assert any("No URL" in note for note in notes)
