"""Tests for emailing module."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from src.lyme_agent.config import Settings
from src.lyme_agent.emailing import send_email


class TestSendEmail:
    """Test email sending functionality."""
    
    @patch('src.lyme_agent.emailing.settings')
    def test_simulation_mode_prints_message(self, mock_settings):
        """Test that simulation mode prints instead of sending."""
        mock_settings.simulation_mode = True
        
        with patch('builtins.print') as mock_print:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                body="Test Body"
            )
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "simulation" in call_args.lower()
            assert "test@example.com" in call_args
    
    @patch('src.lyme_agent.emailing.settings')
    def test_raises_error_without_credentials(self, mock_settings):
        """Test that missing credentials raise an error."""
        mock_settings.simulation_mode = False
        mock_settings.email_user = ""
        mock_settings.email_app_password = ""
        
        with pytest.raises(RuntimeError) as exc_info:
            send_email(
                recipient="test@example.com",
                subject="Test Subject",
                body="Test Body"
            )
        
        assert "EMAIL_USER" in str(exc_info.value) or "EMAIL_APP_PASSWORD" in str(exc_info.value)
    
    @patch('src.lyme_agent.emailing.smtplib.SMTP')
    @patch('src.lyme_agent.emailing.settings')
    def test_sends_email_with_credentials(self, mock_settings, mock_smtp):
        """Test successful email sending with credentials."""
        mock_settings.simulation_mode = False
        mock_settings.email_user = "test@gmail.com"
        mock_settings.email_app_password = "app_password"
        mock_settings.smtp_host = "smtp.gmail.com"
        mock_settings.smtp_port = 587
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = lambda s: mock_server
        mock_smtp.return_value.__exit__ = lambda s, *args: None
        
        send_email(
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@gmail.com", "app_password")
        mock_server.send_message.assert_called_once()
    
    @patch('src.lyme_agent.emailing.smtplib.SMTP')
    @patch('src.lyme_agent.emailing.settings')
    def test_email_content_structure(self, mock_settings, mock_smtp):
        """Test that email has correct structure."""
        from email.message import EmailMessage
        
        mock_settings.simulation_mode = False
        mock_settings.email_user = "sender@gmail.com"
        mock_settings.email_app_password = "password"
        mock_settings.smtp_host = "smtp.gmail.com"
        mock_settings.smtp_port = 587
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = lambda s: mock_server
        mock_smtp.return_value.__exit__ = lambda s, *args: None
        
        send_email(
            recipient="recipient@example.com",
            subject="Daily Report",
            body="# Research Report\n\nContent here"
        )
        
        # Verify send_message was called with proper EmailMessage
        assert mock_server.send_message.called
        sent_message = mock_server.send_message.call_args[0][0]
        assert isinstance(sent_message, EmailMessage)
        assert sent_message["From"] == "sender@gmail.com"
        assert sent_message["To"] == "recipient@example.com"
        assert sent_message["Subject"] == "Daily Report"
        assert "# Research Report" in sent_message.get_content()
