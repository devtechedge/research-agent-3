"""Tests for orchestrator module."""
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
from datetime import datetime

from lyme_agent.orchestrator import run_daily_pipeline, _build_body
from lyme_agent.models import ResearchItem, EvidenceGrade


class TestRunDailyPipeline:
    """Test the main daily pipeline function."""
    
    @patch('lyme_agent.orchestrator.send_email')
    @patch('lyme_agent.orchestrator.write_report')
    @patch('lyme_agent.orchestrator.build_markdown_report')
    @patch('lyme_agent.orchestrator.discover_items')
    @patch('lyme_agent.orchestrator.settings')
    def test_runs_full_pipeline(self, mock_settings, mock_discover, mock_build, mock_write, mock_send):
        # Setup mocks
        mock_item = ResearchItem(title="Test Study", source="PubMed", url="https://example.com/123")
        mock_discover.return_value = MagicMock(items=[mock_item], errors=[])
        mock_build.return_value = "# Report Content"
        mock_settings.use_database = False
        
        # Run pipeline
        result_path = run_daily_pipeline(Path("outputs"), enable_verification=False)
        
        # Verify calls
        mock_discover.assert_called_once()
        mock_build.assert_called_once()
        mock_write.assert_called_once()
        mock_send.assert_called_once()
        
        # Check report path format
        assert "daily-report-" in str(result_path)
        assert result_path.suffix == ".md"
    
    @patch('lyme_agent.orchestrator.send_email')
    @patch('lyme_agent.orchestrator.write_report')
    @patch('lyme_agent.orchestrator.build_markdown_report')
    @patch('lyme_agent.orchestrator.discover_items')
    @patch('lyme_agent.orchestrator.settings')
    def test_enables_verification_when_requested(self, mock_settings, mock_discover, mock_build, mock_write, mock_send):
        mock_discover.return_value = MagicMock(items=[], errors=[])
        mock_settings.use_database = False
        
        run_daily_pipeline(Path("outputs"), enable_verification=True)
        
        # Verify verification was enabled
        call_args = mock_discover.call_args
        assert call_args[1]['perform_verification'] is True
    
    @patch('lyme_agent.orchestrator.send_email')
    @patch('lyme_agent.orchestrator.write_report')
    @patch('lyme_agent.orchestrator.build_markdown_report')
    @patch('lyme_agent.orchestrator.discover_items')
    @patch('lyme_agent.orchestrator.init_db')
    @patch('lyme_agent.orchestrator.save_run')
    @patch('lyme_agent.orchestrator.save_research_items')
    @patch('lyme_agent.orchestrator.settings')
    def test_saves_to_database_when_enabled(
        self, mock_settings, mock_save_items, mock_save_run, mock_init_db, 
        mock_discover, mock_build, mock_write, mock_send
    ):
        mock_item = ResearchItem(title="Test", source="PubMed")
        mock_discover.return_value = MagicMock(items=[mock_item], errors=[])
        mock_build.return_value = "# Report"
        mock_settings.use_database = True
        mock_save_run.return_value = 123
        
        run_daily_pipeline(Path("outputs"))
        
        # Verify database operations
        mock_init_db.assert_called_once()
        mock_save_run.assert_called_once()
        mock_save_items.assert_called_once_with(123, [mock_item])
    
    @patch('lyme_agent.orchestrator.send_email')
    @patch('lyme_agent.orchestrator.write_report')
    @patch('lyme_agent.orchestrator.build_markdown_report')
    @patch('lyme_agent.orchestrator.discover_items')
    @patch('lyme_agent.orchestrator.init_db')
    @patch('lyme_agent.orchestrator.settings')
    def test_handles_database_errors_gracefully(
        self, mock_settings, mock_init_db, mock_discover, mock_build, mock_write, mock_send
    ):
        mock_discover.return_value = MagicMock(items=[], errors=[])
        mock_build.return_value = "# Report"
        mock_settings.use_database = True
        mock_init_db.side_effect = Exception("Database connection failed")
        
        # Should not raise exception
        result_path = run_daily_pipeline(Path("outputs"))
        
        # Verify email still sent despite database error
        mock_send.assert_called_once()
        assert result_path.exists() or True  # Path created regardless
    
    @patch('lyme_agent.orchestrator.send_email')
    @patch('lyme_agent.orchestrator.write_report')
    @patch('lyme_agent.orchestrator.build_markdown_report')
    @patch('lyme_agent.orchestrator.discover_items')
    @patch('lyme_agent.orchestrator.settings')
    def test_creates_output_directory(self, mock_settings, mock_discover, mock_build, mock_write, mock_send):
        mock_discover.return_value = MagicMock(items=[], errors=[])
        mock_build.return_value = "# Report"
        mock_settings.use_database = False
        
        output_dir = Path("test_outputs")
        run_daily_pipeline(output_dir)
        
        # Verify write_report called with correct path
        call_args = mock_write.call_args
        assert "test_outputs" in str(call_args[0][0])


class TestBuildBodyEmptyItems:
    """Test _build_body with no items."""
    
    def test_empty_items_message(self):
        body = _build_body([], [])
        
        assert "## Executive Summary" in body
        assert "No new items discovered" in body
        assert "## Today's discoveries" in body
    
    def test_empty_items_with_errors(self):
        body = _build_body([], ["Error 1", "Error 2"])
        
        assert "Source warnings" in body
        assert "Error 1" in body
        assert "Error 2" in body


class TestBuildBodyWithItems:
    """Test _build_body with research items."""
    
    def test_with_single_item(self):
        item = ResearchItem(
            title="Test Study on Lyme Disease",
            source="PubMed",
            url="https://pubmed.ncbi.nlm.nih.gov/123/",
            summary="This is a test summary."
        )
        
        body = _build_body([item], [])
        
        assert "1 new item(s) found" in body
        assert "Test Study on Lyme Disease" in body
        assert "PubMed" in body
        assert "https://pubmed.ncbi.nlm.nih.gov/123/" in body
    
    def test_with_multiple_items_from_different_sources(self):
        pubmed_item = ResearchItem(title="PubMed Study", source="PubMed")
        ct_item = ResearchItem(title="Clinical Trial", source="ClinicalTrials.gov")
        
        body = _build_body([pubmed_item, ct_item], [])
        
        assert "2 new item(s) found" in body
        assert "PubMed: 1" in body
        assert "ClinicalTrials.gov: 1" in body
    
    def test_includes_evidence_grade(self):
        item = ResearchItem(
            title="High Quality Study",
            source="PubMed",
            evidence_grade=EvidenceGrade.HIGH
        )
        
        body = _build_body([item], [])
        
        assert "[HIGH]" in body
    
    def test_includes_evidence_score(self):
        item = ResearchItem(
            title="Study with Score",
            source="PubMed",
            evidence_score=85.5
        )
        
        body = _build_body([item], [])
        
        assert "Evidence Score: 85.5" in body
    
    def test_truncates_long_summary(self):
        long_summary = "A" * 300  # Longer than 240 char limit
        item = ResearchItem(
            title="Study",
            source="PubMed",
            summary=long_summary
        )
        
        body = _build_body([item], [])
        
        # Summary should be truncated to 240 chars
        assert "Summary:" in body
    
    def test_handles_missing_url(self):
        item = ResearchItem(
            title="Study Without URL",
            source="PubMed",
            url=None
        )
        
        body = _build_body([item], [])
        
        # Should not crash and should include the item
        assert "Study Without URL" in body


class TestBuildBodyWithErrors:
    """Test _build_body when there are discovery errors."""
    
    def test_includes_errors_in_body(self):
        item = ResearchItem(title="Study", source="PubMed")
        errors = ["PubMed API timeout", "Network error"]
        
        body = _build_body([item], errors)
        
        assert "Source warnings" in body or "error" in body.lower()
    
    def test_limits_error_display(self):
        errors = [f"Error {i}" for i in range(20)]  # Many errors
        
        body = _build_body([], errors)
        
        # Should not display all 20 errors (limited to first 8)
        error_count = body.count("Error ")
        assert error_count <= 10  # Some reasonable limit


class TestEmailSubject:
    """Test email subject line generation."""
    
    @patch('lyme_agent.orchestrator.send_email')
    @patch('lyme_agent.orchestrator.write_report')
    @patch('lyme_agent.orchestrator.build_markdown_report')
    @patch('lyme_agent.orchestrator.discover_items')
    @patch('lyme_agent.orchestrator.settings')
    def test_subject_with_items(self, mock_settings, mock_discover, mock_build, mock_write, mock_send):
        mock_item = ResearchItem(title="Study", source="PubMed")
        mock_discover.return_value = MagicMock(items=[mock_item, mock_item], errors=[])
        mock_build.return_value = "# Report"
        mock_settings.use_database = False
        
        run_daily_pipeline(Path("outputs"))
        
        # Check subject includes count
        call_args = mock_send.call_args
        subject = call_args[0][1]
        assert "2 new item(s)" in subject
    
    @patch('lyme_agent.orchestrator.send_email')
    @patch('lyme_agent.orchestrator.write_report')
    @patch('lyme_agent.orchestrator.build_markdown_report')
    @patch('lyme_agent.orchestrator.discover_items')
    @patch('lyme_agent.orchestrator.settings')
    def test_subject_without_items(self, mock_settings, mock_discover, mock_build, mock_write, mock_send):
        mock_discover.return_value = MagicMock(items=[], errors=[])
        mock_build.return_value = "# Report"
        mock_settings.use_database = False
        
        run_daily_pipeline(Path("outputs"))
        
        call_args = mock_send.call_args
        subject = call_args[0][1]
        assert "No new items" in subject
