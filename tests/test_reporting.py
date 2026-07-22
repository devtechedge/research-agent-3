"""Tests for reporting module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.lyme_agent.reporting import build_markdown_report, write_report


class TestBuildMarkdownReport:
    """Test markdown report building."""
    
    def test_basic_report_structure(self):
        """Test that report has correct structure."""
        date_text = "2024-01-15"
        body = "## Summary\n\nNo new items found."
        
        report = build_markdown_report(date_text, body)
        
        assert "# Daily Research Report - 2024-01-15" in report
        assert "## Summary" in report
        assert "No new items found." in report
    
    def test_report_with_discoveries(self):
        """Test report with actual discoveries."""
        date_text = "2024-06-20"
        body = """## Executive Summary
- 5 new item(s) found today
- PubMed: 3
- ClinicalTrials.gov: 2

## Today's discoveries
- [PubMed] Study about Lyme disease
- [ClinicalTrials.gov] Trial NCT12345678"""
        
        report = build_markdown_report(date_text, body)
        
        assert "# Daily Research Report - 2024-06-20" in report
        assert "5 new item(s)" in report
        assert "PubMed: 3" in report
        assert "ClinicalTrials.gov: 2" in report
    
    def test_empty_body(self):
        """Test report with empty body."""
        date_text = "2024-01-01"
        body = ""
        
        report = build_markdown_report(date_text, body)
        
        assert "# Daily Research Report - 2024-01-01" in report
        # Body can be empty, just check header exists


class TestWriteReport:
    """Test report writing functionality."""
    
    @patch('src.lyme_agent.reporting.Path')
    def test_creates_parent_directories(self, mock_path_class):
        """Test that parent directories are created."""
        mock_path = MagicMock()
        mock_path.parent = MagicMock()
        mock_path.parent.mkdir = MagicMock()
        mock_path.write_text = MagicMock()
        mock_path_class.return_value = mock_path
        
        content = "# Test Report"
        write_report(mock_path, content)
        
        mock_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_path.write_text.assert_called_once_with(content, encoding="utf-8")
    
    def test_writes_content_to_file(self, tmp_path):
        """Test actual file writing."""
        report_file = tmp_path / "subdir" / "report.md"
        content = "# Test Report\n\nThis is test content."
        
        write_report(report_file, content)
        
        assert report_file.exists()
        assert report_file.read_text(encoding="utf-8") == content
    
    def test_preserves_encoding(self, tmp_path):
        """Test that UTF-8 encoding is preserved."""
        report_file = tmp_path / "report_utf8.md"
        content = "# Report with Unicode: café, naïve, 研究"
        
        write_report(report_file, content)
        
        written_content = report_file.read_text(encoding="utf-8")
        assert written_content == content
        assert "café" in written_content
        assert "研究" in written_content
    
    @patch('src.lyme_agent.reporting.Path')
    def test_mkdir_called_with_correct_params(self, mock_path_class):
        """Test mkdir parameters."""
        mock_path = MagicMock()
        mock_path.parent = MagicMock()
        mock_path.write_text = MagicMock()
        mock_path_class.return_value = mock_path
        
        write_report(mock_path, "content")
        
        mock_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
