# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [0.3.0] - 2025-12-10

### Added
- Citation verification system with URL accessibility checking
- Evidence scoring algorithm (0-100 point scale)
- Evidence grading system (HIGH/MODERATE/LOW/VERY_LOW)
- Study design detection and classification
- Metadata extraction (PMID, NCT ID, DOI)
- Quality summary sections in daily reports
- Database fields for verification status, scores, and grades

### Changed
- Enhanced database schema to support verification and scoring data
- Improved report generation to include evidence quality metrics

### Fixed
- Proper error handling for unreachable URLs during verification
- Timeout management for citation verification requests

## [0.2.0] - 2025-12-09

### Added
- PostgreSQL persistence layer implementation
- Runs table for tracking daily research executions
- Research items table with deduplication support
- Database integration in orchestrator pipeline
- Environment variable configuration for database connection
- Graceful fallback mechanism when database is unavailable
- Comprehensive test suite for persistence layer

### Changed
- Modified data flow to persist runs and items to database
- Updated error handling to support optional database usage

## [0.1.0] - 2025-12-08

### Added
- Initial autonomous research agent scaffold
- Daily GitHub Actions workflow scheduling
- Gmail SMTP email delivery using GitHub Secrets
- Repository instructions and project documentation
- Real PubMed and ClinicalTrials.gov discovery connectors
- Daily markdown report generation
- Email summaries with counts, links, and research item details
- Configuration management and data models
- Project architecture and roadmap documentation

### Previous Features
- Core orchestration pipeline
- Discovery layer abstraction
- Report generator with markdown output
- Email sender with Gmail integration

---

## Release Notes Template

Use the following template when creating new releases on GitHub:

```markdown
## What's Changed

### New Features
- [List key features added in this release]

### Improvements
- [List improvements and enhancements]

### Bug Fixes
- [List bug fixes]

### Technical Changes
- [List technical updates and refactoring]

## Installation

```bash
git clone https://github.com/devtechedge/research-agent-3.git
cd research-agent-3
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:
- `DATABASE_URL`: PostgreSQL connection string (optional)
- `USE_DATABASE`: Set to 'true' to enable database persistence
- `GMAIL_SMTP_PASSWORD`: Gmail app password for email delivery
- `PUBMED_API_KEY`: NCBI API key for PubMed access
- `RECIPIENT_EMAIL`: Email address for daily summaries

## Contributors

Thanks to all contributors who made this release possible!

## Full Changelog

See CHANGELOG.md for the complete history of changes.
```
