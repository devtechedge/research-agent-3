"""Tests for configuration module."""

import pytest


class TestSettings:
    """Test settings configuration."""
    
    def test_default_values(self):
        """Test default settings values."""
        from src.lyme_agent.config import Settings
        
        # The module creates a singleton, so we test the actual values
        # Default SIMULATION_MODE env var is not set, but code defaults to "true"
        settings = Settings()
        assert settings.environment == "dev"
        assert settings.simulation_mode is True  # Default is "true".lower() == "true"
        assert settings.smtp_host == "smtp.gmail.com"
        assert settings.smtp_port == 587
    
    def test_simulation_mode_parsing_true_variants(self):
        """Test simulation mode parsing for true variants."""
        from src.lyme_agent.config import Settings
        import os
        from unittest.mock import patch
        
        for value in ["true", "True", "TRUE"]:
            with patch.dict(os.environ, {"SIMULATION_MODE": value}, clear=False):
                settings = Settings()
                assert settings.simulation_mode is True, f"Failed for SIMULATION_MODE={value}"


class TestSettingsSingleton:
    """Test the global settings instance."""
    
    def test_settings_instance_exists(self):
        """Test that global settings instance is created."""
        from src.lyme_agent.config import settings
        assert settings is not None
        assert isinstance(settings.environment, str)
        assert isinstance(settings.recipient_email, str)
        assert settings.simulation_mode is True  # default
