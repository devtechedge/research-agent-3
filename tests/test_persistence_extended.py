"""Tests for persistence module."""
import pytest
from unittest.mock import patch, MagicMock, call
import sys

from lyme_agent.persistence import (
    init_db,
    get_connection,
    save_run,
    get_existing_urls,
    save_research_items,
    get_runs,
    get_items_for_run,
    PSYCOPG2_AVAILABLE
)
from lyme_agent.models import ResearchItem, EvidenceGrade, StudyDesign


@pytest.mark.skipif(not PSYCOPG2_AVAILABLE, reason="psycopg2 not installed")
class TestPersistenceWithPsycopg2:
    """Test persistence functions when psycopg2 is available."""
    
    @patch('lyme_agent.persistence.get_connection')
    def test_init_db_creates_tables(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda self: mock_cursor
        mock_conn.cursor.return_value.__exit__ = lambda self, *args: None
        mock_get_conn.return_value = mock_conn
        
        init_db()
        
        assert mock_cursor.execute.call_count >= 3  # At least 3 tables
        
    @patch('lyme_agent.persistence.psycopg2.connect')
    def test_get_connection_uses_settings(self, mock_connect):
        from lyme_agent.config import settings
        
        get_connection()
        
        mock_connect.assert_called_once_with(settings.database_url)
    
    @patch('lyme_agent.persistence.get_connection')
    def test_save_run_inserts_and_returns_id(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (123,)
        mock_conn.cursor.return_value.__enter__ = lambda self: mock_cursor
        mock_conn.cursor.return_value.__exit__ = lambda self, *args: None
        mock_get_conn.return_value = mock_conn
        
        run_id = save_run("2024-01-15", items_count=5, errors_count=1, report_path="/path/to/report.md")
        
        assert run_id == 123
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
    
    @patch('lyme_agent.persistence.get_connection')
    def test_get_existing_urls_returns_set(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("https://pubmed.ncbi.nlm.nih.gov/123/",),
            ("https://clinicaltrials.gov/study/NCT456",)
        ]
        mock_conn.cursor.return_value.__enter__ = lambda self: mock_cursor
        mock_conn.cursor.return_value.__exit__ = lambda self, *args: None
        mock_get_conn.return_value = mock_conn
        
        urls = get_existing_urls(["PubMed", "ClinicalTrials.gov"])
        
        assert isinstance(urls, set)
        assert len(urls) == 2
        assert "https://pubmed.ncbi.nlm.nih.gov/123/" in urls
    
    @patch('lyme_agent.persistence.get_connection')
    @patch('lyme_agent.persistence.execute_batch')
    def test_save_research_items_batch_inserts(self, mock_execute_batch, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda self: mock_cursor
        mock_conn.cursor.return_value.__exit__ = lambda self, *args: None
        mock_get_conn.return_value = mock_conn
        
        items = [
            ResearchItem(
                title="Test Study",
                source="PubMed",
                url="https://pubmed.ncbi.nlm.nih.gov/123/",
                summary="Test summary"
            ),
            ResearchItem(
                title="Another Study",
                source="ClinicalTrials.gov",
                url="https://clinicaltrials.gov/study/NCT456"
            )
        ]
        
        save_research_items(run_id=123, items=items)
        
        mock_execute_batch.assert_called_once()
    
    @patch('lyme_agent.persistence.get_connection')
    def test_get_runs_returns_list(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (123, "2024-01-15", 5, 1, "/path/to/report.md"),
            (122, "2024-01-14", 3, 0, "/path/to/report2.md")
        ]
        mock_conn.cursor.return_value.__enter__ = lambda self: mock_cursor
        mock_conn.cursor.return_value.__exit__ = lambda self, *args: None
        mock_get_conn.return_value = mock_conn
        
        runs = get_runs(limit=30)
        
        assert isinstance(runs, list)
        assert len(runs) == 2
    
    @patch('lyme_agent.persistence.get_connection')
    def test_get_items_for_run_returns_items(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("Study 1", "PubMed", "https://example.com/1", "Summary 1", None, None, None),
            ("Study 2", "ClinicalTrials.gov", "https://example.com/2", "Summary 2", None, None, None)
        ]
        mock_conn.cursor.return_value.__enter__ = lambda self: mock_cursor
        mock_conn.cursor.return_value.__exit__ = lambda self, *args: None
        mock_get_conn.return_value = mock_conn
        
        items = get_items_for_run(run_id=123)
        
        assert isinstance(items, list)
        assert len(items) == 2
        assert items[0].title == "Study 1"


class TestPersistenceWithoutPsycopg2:
    """Test behavior when psycopg2 is not available."""
    
    def test_persistence_disabled_when_psycopg2_missing(self):
        if PSYCOPG2_AVAILABLE:
            pytest.skip("psycopg2 is installed, skipping this test")
        
        # When psycopg2 is not available, functions should handle gracefully
        assert PSYCOPG2_AVAILABLE is False


class TestResearchItemModel:
    """Test ResearchItem model used in persistence."""
    
    def test_research_item_creation(self):
        item = ResearchItem(
            title="Test Study",
            source="PubMed",
            url="https://example.com/123",
            summary="Test summary",
            published_at=None
        )
        
        assert item.title == "Test Study"
        assert item.source == "PubMed"
        assert item.url == "https://example.com/123"
    
    def test_research_item_with_evidence_grade(self):
        item = ResearchItem(
            title="High Quality Study",
            source="PubMed",
            url="https://example.com/456",
            evidence_grade=EvidenceGrade.HIGH,
            evidence_score=85.5
        )
        
        assert item.evidence_grade == EvidenceGrade.HIGH
        assert item.evidence_score == 85.5


class TestDatabaseConnectionConfigured:
    """Test that database connection is properly configured."""
    
    def test_settings_database_url_exists(self):
        from lyme_agent.config import settings
        
        assert hasattr(settings, 'database_url')
        assert isinstance(settings.database_url, str)
        assert len(settings.database_url) > 0
    
    def test_use_database_setting(self):
        from lyme_agent.config import settings
        
        assert hasattr(settings, 'use_database')
        assert isinstance(settings.use_database, bool)
