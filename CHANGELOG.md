# Changelog

## Unreleased

### Persistence & Storage (v0.2.0)
- Implemented PostgreSQL persistence layer with automatic schema creation
- Added `runs` table for tracking daily research runs with status, counts, and timestamps
- Added `research_items` table for storing discovered items with deduplication support
- Integrated database operations into orchestrator pipeline
- Added graceful fallback when database is unavailable
- Added environment configuration via DATABASE_URL and USE_DATABASE
- Implemented comprehensive test suite for persistence layer

### Verification & Quality (v0.3.0)
- Implemented citation verification with URL accessibility checking
- Added evidence scoring system (0-100 scale) based on:
  - Study design (0-40 points)
  - Sample size (0-25 points)
  - Methodological quality (0-25 points)
  - Recency (0-10 points)
- Implemented evidence grading (HIGH/MODERATE/LOW/VERY_LOW) using Oxford CEBM principles
- Added study design detection from metadata
- Enhanced database schema with verification_status, score, grade, and metadata fields
- Updated reports to include quality summaries and verification statistics
- Added comprehensive test suite for verification and scoring modules

### Previous Features
- Added the initial autonomous research agent scaffold
- Added daily GitHub Actions workflow
- Added Gmail SMTP email delivery using GitHub Secrets
- Added repository instructions and project docs
- Added real PubMed and ClinicalTrials.gov discovery
- Improved the daily email subject and body with counts, links, and summaries

## Release Notes

### 0.1.0

First working version of the research-agent scaffold.

Includes:
- daily GitHub Actions automation
- Gmail SMTP delivery
- initial repository documentation
- live research discovery from PubMed and ClinicalTrials.gov
- daily markdown report generation
