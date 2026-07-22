"""Tests for discovery module (discovery_real.py)."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.lyme_agent.models import ResearchItem
from src.lyme_agent.discovery_real import (
    DiscoveryResult,
    discover_items,
)


class TestDiscoveryResult:
    """Test DiscoveryResult dataclass."""
    
    def test_default_initialization(self):
        """Test default field values."""
        result = DiscoveryResult()
        assert result.items == []
        assert result.errors == []
    
    def test_with_items(self):
        """Test initialization with items."""
        item = ResearchItem(
            title="Test Study",
            source="PubMed",
            url="https://example.com"
        )
        result = DiscoveryResult(items=[item], errors=["test error"])
        assert len(result.items) == 1
        assert len(result.errors) == 1
        assert result.items[0].title == "Test Study"


class TestDiscoverItems:
    """Test main discover_items function."""
    
    @patch('src.lyme_agent.discovery_real._pubmed_items')
    @patch('src.lyme_agent.discovery_real._clinical_trials_items')
    def test_combines_sources(self, mock_ct, mock_pubmed):
        """Test that items from both sources are combined."""
        pubmed_item = ResearchItem(
            title="PubMed Study",
            source="PubMed",
            url="https://pubmed.example.com/1"
        )
        ct_item = ResearchItem(
            title="Clinical Trial",
            source="ClinicalTrials.gov",
            url="https://clinicaltrials.gov/study/NCT12345678"
        )
        
        mock_pubmed.return_value = ([pubmed_item], [])
        mock_ct.return_value = ([ct_item], [])
        
        result = discover_items(skip_existing=False, perform_verification=False)
        
        assert len(result.items) == 2
        assert any(item.source == "PubMed" for item in result.items)
        assert any(item.source == "ClinicalTrials.gov" for item in result.items)
    
    @patch('src.lyme_agent.discovery_real._pubmed_items')
    @patch('src.lyme_agent.discovery_real._clinical_trials_items')
    def test_collects_errors_from_both_sources(self, mock_ct, mock_pubmed):
        """Test that errors from both sources are collected."""
        mock_pubmed.return_value = ([], ["PubMed error"])
        mock_ct.return_value = ([], ["ClinicalTrials error"])
        
        result = discover_items(skip_existing=False, perform_verification=False)
        
        assert len(result.errors) == 2
        assert "PubMed error" in result.errors
        assert "ClinicalTrials error" in result.errors
