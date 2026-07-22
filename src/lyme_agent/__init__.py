"""Chronic Lyme Research Agent - Autonomous research agent for chronic Lyme disease / PTLDS.

This package provides an automated system for discovering, verifying, and reporting
on new research related to chronic Lyme disease and Post-Treatment Lyme Disease Syndrome (PTLDS).

Main Components:
    - discovery_real: Discovers research items from PubMed and ClinicalTrials.gov
    - verification: Verifies citations and scores evidence quality
    - orchestrator: Runs the daily research pipeline
    - reporting: Generates markdown reports
    - emailing: Sends email notifications
    - persistence: Stores research data in PostgreSQL database

Example Usage:
    >>> from lyme_agent.discovery_real import discover_items
    >>> result = discover_items(perform_verification=True)
    >>> print(f"Found {len(result.items)} new research items")
    
    >>> from lyme_agent.orchestrator import run_daily_pipeline
    >>> from pathlib import Path
    >>> report_path = run_daily_pipeline(Path("outputs"), enable_verification=True)

For more information, see the README.md file.
"""

__version__ = "0.1.0"
__author__ = "Chronic Lyme Research Team"
__all__ = [
    "config",
    "discovery_real",
    "discovery",
    "emailing",
    "models",
    "orchestrator",
    "persistence",
    "reporting",
    "verification",
]

from . import config
from . import models
from . import discovery_real
from . import discovery
from . import emailing
from . import orchestrator
from . import persistence
from . import reporting
from . import verification

__version_tuple__ = tuple(int(x) for x in __version__.split("."))
