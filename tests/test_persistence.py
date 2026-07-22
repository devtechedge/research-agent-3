"""Tests for the persistence layer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime
from lyme_agent.models import ResearchItem
from lyme_agent.persistence import (
    PSYCOPG2_AVAILABLE,
    init_db,
    save_run,
    save_research_items,
    get_existing_urls,
    get_runs,
    get_items_for_run,
)


def test_psycopg2_available():
    """Test that psycopg2 is installed."""
    assert PSYCOPG2_AVAILABLE, "psycopg2 should be available"
    print("✓ psycopg2 is available")


def test_research_item_model():
    """Test ResearchItem model creation."""
    item = ResearchItem(
        title="Test Study",
        source="PubMed",
        url="https://pubmed.ncbi.nlm.nih.gov/12345/",
        published_at=datetime.now(),
        summary="Test summary",
    )
    assert item.title == "Test Study"
    assert item.source == "PubMed"
    assert "pubmed" in item.url
    print("✓ ResearchItem model works correctly")


def test_persistence_functions_exist():
    """Test that all persistence functions are defined."""
    assert callable(init_db), "init_db should be callable"
    assert callable(save_run), "save_run should be callable"
    assert callable(save_research_items), "save_research_items should be callable"
    assert callable(get_existing_urls), "get_existing_urls should be callable"
    assert callable(get_runs), "get_runs should be callable"
    assert callable(get_items_for_run), "get_items_for_run should be callable"
    print("✓ All persistence functions are defined")


def test_database_connection_configured():
    """Test that database configuration is available."""
    from lyme_agent.config import settings
    
    assert hasattr(settings, 'database_url'), "Settings should have database_url"
    assert hasattr(settings, 'use_database'), "Settings should have use_database"
    assert settings.database_url.startswith('postgresql://'), "DATABASE_URL should be a PostgreSQL URL"
    print("✓ Database configuration is properly set up")


if __name__ == "__main__":
    print("Running persistence tests...\n")
    
    test_psycopg2_available()
    test_research_item_model()
    test_persistence_functions_exist()
    test_database_connection_configured()
    
    print("\n✓ All tests passed!")
    print("\nNote: Full integration tests require a running PostgreSQL database.")
    print("To test database operations, set USE_DATABASE=true and provide a valid DATABASE_URL.")
