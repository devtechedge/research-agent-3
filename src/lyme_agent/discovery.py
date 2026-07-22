"""Stub discovery module - deprecated in favor of discovery_real.py.

This module is kept for backward compatibility but should not be used.
Use lyme_agent.discovery_real.discover_items() instead.
"""
from __future__ import annotations

import logging

from .models import ResearchItem
from .discovery_real import discover_items as real_discover_items, DiscoveryResult

logger = logging.getLogger(__name__)


def discover_items(
    skip_existing: bool = True,
    perform_verification: bool = False
) -> list[ResearchItem]:
    """Discover research items from PubMed and ClinicalTrials.gov.
    
    This is a wrapper around discovery_real.discover_items() that returns
    only the items list for backward compatibility.
    
    Args:
        skip_existing: If True, filter out items already in the database.
        perform_verification: If True, verify citations and score evidence quality.
    
    Returns:
        List of discovered ResearchItem objects.
    
    Deprecated:
        Use lyme_agent.discovery_real.discover_items() which returns a
        DiscoveryResult with both items and errors.
    """
    logger.warning(
        "discovery.discover_items() is deprecated. "
        "Use discovery_real.discover_items() instead."
    )
    result: DiscoveryResult = real_discover_items(
        skip_existing=skip_existing,
        perform_verification=perform_verification
    )
    return result.items
