"""Tests for orchestrator module."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.lyme_agent.models import ResearchItem, EvidenceGrade
from src.lyme_agent.orchestrator import _build_body


class TestBuildBody:
    """Test email/report body building."""
    
    def test_empty_items_message(self):
        """Test body when no items found."""
        body = _build_body([], [])
        
        assert "No new items discovered" in body
        assert "No matching items" in body
    
    def test_with_items_summary(self):
        """Test body with discovered items."""
        items = [
            ResearchItem(
                title="PubMed Study",
                source="PubMed",
                url="https://pubmed.example.com/1"
            ),
            ResearchItem(
                title="Clinical Trial",
                source="ClinicalTrials.gov",
                url="https://clinicaltrials.gov/study/NCT12345678"
            ),
        ]
        
        body = _build_body(items, [])
        
        assert "2 new item(s) found today" in body
        assert "PubMed: 1" in body
        assert "ClinicalTrials.gov: 1" in body
    
    def test_with_errors(self):
        """Test body includes errors."""
        items = []
        errors = ["API timeout", "Connection refused"]
        
        body = _build_body(items, errors)
        
        assert "Source warnings" in body or "warnings" in body.lower()
        assert any(err in body for err in errors)
    
    def test_with_evidence_grades(self):
        """Test body includes evidence grades when available."""
        items = [
            ResearchItem(
                title="High Quality RCT",
                source="PubMed",
                url="https://example.com/1",
                evidence_score=85.0,
                evidence_grade=EvidenceGrade.HIGH
            ),
        ]
        
        body = _build_body(items, [])
        
        assert "[HIGH]" in body.upper() or "HIGH" in body
    
    def test_with_evidence_scores(self):
        """Test body includes evidence scores when available."""
        items = [
            ResearchItem(
                title="Study with Score",
                source="PubMed",
                url="https://example.com/1",
                evidence_score=75.5
            ),
        ]
        
        body = _build_body(items, [])
        
        # Should include score information
        assert "75.5" in body or "Evidence Score" in body or "score" in body.lower()
    
    def test_includes_url_and_summary(self):
        """Test that URLs and summaries are included."""
        items = [
            ResearchItem(
                title="Test Study",
                source="PubMed",
                url="https://example.com/test",
                summary="This is a test summary of the study."
            ),
        ]
        
        body = _build_body(items, [])
        
        assert "https://example.com/test" in body
        assert "Link:" in body
        assert "Summary:" in body or "test summary" in body.lower()
