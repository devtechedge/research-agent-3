"""Tests for discovery_real module."""
import pytest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
from datetime import datetime

from lyme_agent.discovery_real import (
    discover_items, 
    DiscoveryResult, 
    _pubmed_items, 
    _clinical_trials_items,
    _http_get
)
from lyme_agent.models import ResearchItem


class TestDiscoveryResult:
    """Test DiscoveryResult dataclass."""
    
    def test_default_initialization(self):
        result = DiscoveryResult()
        assert result.items == []
        assert result.errors == []
    
    def test_with_items_and_errors(self):
        items = [ResearchItem(title="Test", source="PubMed")]
        errors = ["Error 1", "Error 2"]
        result = DiscoveryResult(items=items, errors=errors)
        assert len(result.items) == 1
        assert len(result.errors) == 2


class TestHttpGet:
    """Test HTTP GET function."""
    
    @patch('urllib.request.urlopen')
    def test_http_get_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"test": "data"}'
        mock_response.__enter__ = lambda self: self
        mock_response.__exit__ = lambda self, *args: None
        mock_urlopen.return_value = mock_response
        
        result = _http_get("https://example.com/api")
        
        assert result == '{"test": "data"}'
        mock_urlopen.assert_called_once()


class TestPubmedItems:
    """Test PubMed discovery function."""
    
    @patch('lyme_agent.discovery_real._http_get')
    def test_pubmed_success(self, mock_http_get):
        # Mock ESearch response
        search_xml = """<?xml version="1.0"?>
        <eSearchResult>
            <Count>1</Count>
            <IdList><Id>12345678</Id></IdList>
        </eSearchResult>"""
        
        # Mock EFetch response
        fetch_xml = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345678</PMID>
                </MedlineCitation>
                <Article>
                    <ArticleTitle>Test Study on Lyme Disease</ArticleTitle>
                    <Abstract>
                        <AbstractText>This is a test abstract about Lyme disease.</AbstractText>
                    </Abstract>
                    <PubDate>
                        <Year>2024</Year>
                        <Month>01</Month>
                        <Day>15</Day>
                    </PubDate>
                </Article>
            </PubmedArticle>
        </PubmedArticleSet>"""
        
        mock_http_get.side_effect = [search_xml, fetch_xml]
        
        items, errors = _pubmed_items()
        
        assert len(items) == 1
        assert items[0].title == "Test Study on Lyme Disease"
        assert items[0].source == "PubMed"
        assert "12345678" in items[0].url
        assert errors == []
    
    @patch('lyme_agent.discovery_real._http_get')
    def test_pubmed_error_handling(self, mock_http_get):
        mock_http_get.side_effect = Exception("Network error")
        
        items, errors = _pubmed_items()
        
        assert items == []
        assert len(errors) > 0
        assert "PubMed" in errors[0]
    
    @patch('lyme_agent.discovery_real._http_get')
    def test_pubmed_no_results(self, mock_http_get):
        search_xml = """<?xml version="1.0"?>
        <eSearchResult>
            <Count>0</Count>
            <IdList></IdList>
        </eSearchResult>"""
        
        mock_http_get.return_value = search_xml
        
        items, errors = _pubmed_items()
        
        assert items == []
        assert errors == []


class TestClinicalTrialsItems:
    """Test ClinicalTrials.gov discovery function."""
    
    @patch('lyme_agent.discovery_real._http_get')
    def test_clinical_trials_success(self, mock_http_get):
        response_json = {
            "StudyFieldsResponse": {
                "StudyFields": [{
                    "NCTId": ["NCT01234567"],
                    "BriefTitle": ["Test Clinical Trial"],
                    "BriefSummary": ["This is a test trial summary."],
                    "StartDate": ["2024-01-15"]
                }]
            }
        }
        
        import json
        mock_http_get.return_value = json.dumps(response_json)
        
        items, errors = _clinical_trials_items()
        
        assert len(items) == 1
        assert items[0].title == "Test Clinical Trial"
        assert items[0].source == "ClinicalTrials.gov"
        assert "NCT01234567" in items[0].url
        assert errors == []
    
    @patch('lyme_agent.discovery_real._http_get')
    def test_clinical_trials_error_handling(self, mock_http_get):
        mock_http_get.side_effect = Exception("API error")
        
        items, errors = _clinical_trials_items()
        
        assert items == []
        assert len(errors) > 0
        assert "ClinicalTrials.gov" in errors[0]


class TestDiscoverItems:
    """Test main discover_items function."""
    
    @patch('lyme_agent.discovery_real._pubmed_items')
    @patch('lyme_agent.discovery_real._clinical_trials_items')
    def test_discovers_from_both_sources(self, mock_ct, mock_pubmed):
        pubmed_item = ResearchItem(title="PubMed Study", source="PubMed", url="https://pubmed.ncbi.nlm.nih.gov/123/")
        ct_item = ResearchItem(title="Clinical Trial", source="ClinicalTrials.gov", url="https://clinicaltrials.gov/study/NCT123")
        
        mock_pubmed.return_value = ([pubmed_item], [])
        mock_ct.return_value = ([ct_item], [])
        
        result = discover_items(skip_existing=False)
        
        assert len(result.items) == 2
        sources = {item.source for item in result.items}
        assert "PubMed" in sources
        assert "ClinicalTrials.gov" in sources
    
    @patch('lyme_agent.discovery_real._pubmed_items')
    @patch('lyme_agent.discovery_real._clinical_trials_items')
    def test_deduplication_by_url(self, mock_ct, mock_pubmed):
        item1 = ResearchItem(title="Study", source="PubMed", url="https://example.com/123")
        item2 = ResearchItem(title="Study", source="ClinicalTrials.gov", url="https://example.com/123")
        
        mock_pubmed.return_value = ([item1], [])
        mock_ct.return_value = ([item2], [])
        
        result = discover_items(skip_existing=False)
        
        # Should deduplicate by URL
        assert len(result.items) == 1
    
    @patch('lyme_agent.discovery_real.settings')
    @patch('lyme_agent.discovery_real._pubmed_items')
    @patch('lyme_agent.discovery_real._clinical_trials_items')
    def test_skips_existing_when_database_enabled(self, mock_ct, mock_pubmed, mock_settings):
        mock_settings.use_database = True
        
        item = ResearchItem(title="Study", source="PubMed", url="https://example.com/existing")
        
        mock_pubmed.return_value = ([item], [])
        mock_ct.return_value = ([], [])
        
        with patch('lyme_agent.discovery_real.get_existing_urls', return_value=["https://example.com/existing"]):
            result = discover_items(skip_existing=True)
            
            # Item should be filtered out as existing
            assert len(result.items) == 0
    
    @patch('lyme_agent.discovery_real._pubmed_items')
    @patch('lyme_agent.discovery_real._clinical_trials_items')
    def test_collects_errors_from_both_sources(self, mock_ct, mock_pubmed):
        mock_pubmed.return_value = ([], ["PubMed error"])
        mock_ct.return_value = ([], ["ClinicalTrials error"])
        
        result = discover_items(skip_existing=False)
        
        assert len(result.errors) == 2
        assert "PubMed error" in result.errors
        assert "ClinicalTrials error" in result.errors
    
    @patch('lyme_agent.discovery_real.verify_and_score_items')
    @patch('lyme_agent.discovery_real._pubmed_items')
    @patch('lyme_agent.discovery_real._clinical_trials_items')
    def test_performs_verification_when_enabled(self, mock_ct, mock_pubmed, mock_verify):
        item = ResearchItem(title="Study", source="PubMed", url="https://example.com/123")
        
        mock_pubmed.return_value = ([item], [])
        mock_ct.return_value = ([], [])
        mock_verify.return_value = [item]
        
        result = discover_items(skip_existing=False, perform_verification=True)
        
        mock_verify.assert_called_once()
    
    @patch('lyme_agent.discovery_real._pubmed_items')
    @patch('lyme_agent.discovery_real._clinical_trials_items')
    def test_handles_exceptions_gracefully(self, mock_ct, mock_pubmed):
        mock_pubmed.side_effect = Exception("Unexpected error")
        mock_ct.side_effect = Exception("Another error")
        
        result = discover_items(skip_existing=False)
        
        assert len(result.items) == 0
        assert len(result.errors) == 2


class TestDeduplication:
    """Test deduplication logic."""
    
    @patch('lyme_agent.discovery_real._pubmed_items')
    @patch('lyme_agent.discovery_real._clinical_trials_items')
    def test_deduplication_by_title_when_no_url(self, mock_ct, mock_pubmed):
        item1 = ResearchItem(title="Same Title", source="PubMed", url=None)
        item2 = ResearchItem(title="Same Title", source="ClinicalTrials.gov", url=None)
        
        mock_pubmed.return_value = ([item1], [])
        mock_ct.return_value = ([item2], [])
        
        result = discover_items(skip_existing=False)
        
        # Should deduplicate by title when URL is None
        assert len(result.items) == 1
