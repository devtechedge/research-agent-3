# Roadmap

## Phase 1 ✅ COMPLETED

- Finalize architecture and repo conventions

## Phase 2 ✅ COMPLETED

- ✅ Add real source connectors for PubMed and ClinicalTrials.gov
- ✅ Persist runs and items in Postgres (IMPLEMENTED)
- ✅ Generate richer daily reports with evidence quality metrics (IMPLEMENTED)

## Phase 3 ✅ COMPLETED - Verification & Quality

- ✅ Citation verification - URLs are verified for accessibility
- ✅ Evidence scoring - 0-100 score based on study design, sample size, methodology, recency
- ✅ Evidence grading - HIGH/MODERATE/LOW/VERY_LOW grades using established hierarchies
- ✅ Study design detection - Automatic classification (RCT, meta-analysis, cohort, etc.)
- ✅ Metadata extraction - PMID, NCT ID, DOI, journal name, sample size
- ✅ Methodological quality flags - Randomization, blinding, control groups
- ✅ Database schema updated with verification and evidence fields
- ✅ Reports enhanced with evidence quality summaries and grade distributions
- ✅ High-quality item filtering for focused insights

## Phase 4 📋 PLANNED

- 📋 Advanced deduplication algorithms (beyond URL-based)
- 📋 Contradiction tracking between studies
- 📋 Memory and retrieval system
- 📋 Expanded report formats (PDF, JSON API)
- 📋 Alert system for high-priority findings
- 📋 Comprehensive test suite
- 📋 Logging configuration
- 📋 Release tagging and versioning

## Completed Features

### Verification & Evidence Scoring (v0.3.0)
- **Citation Verification**: Automatic URL accessibility checking with HTTP status validation
- **Evidence Scoring Algorithm**: 
  - Study design scoring (0-40 points): Meta-analyses and systematic reviews ranked highest
  - Sample size scoring (0-25 points): Larger studies receive higher scores
  - Methodological quality (0-25 points): Points for randomization, blinding, control groups
  - Recency scoring (0-10 points): Recent publications weighted more heavily
- **Evidence Grading**: Four-tier system (HIGH, MODERATE, LOW, VERY_LOW) based on Oxford CEBM principles
- **Study Design Detection**: Keyword-based classification for 10+ study types
- **Metadata Extraction**: Automatic extraction of PMID, NCT ID, DOI, journal names, sample sizes
- **Quality Indicators**: Boolean flags for randomization, blinding, and control groups
- **Summary Statistics**: Aggregate quality metrics including grade distribution and verification rates
- **High-Quality Filtering**: Filter items by minimum score and grade thresholds

### Persistence Layer (v0.2.0)
- PostgreSQL database schema with `runs` and `research_items` tables
- Extended schema with verification fields (`is_verified`, `verification_status`, `verification_notes`)
- Evidence scoring fields (`evidence_score`, `study_design`, `evidence_grade`)
- Metadata fields (`pmid`, `nct_id`, `doi`, `journal_name`, `sample_size`, etc.)
- Automatic saving of daily runs and discovered items with full quality metrics
- Database-driven deduplication to filter previously seen items
- Indexes on evidence_score and evidence_grade for efficient quality filtering
- Query functions for historical data retrieval
- Configurable via `DATABASE_URL` and `USE_DATABASE` environment variables
- Graceful fallback when database is unavailable

### Enhanced Reporting
- Daily reports now include Evidence Quality Summary section
- Average evidence scores displayed for each day's findings
- Grade distribution breakdown (count by HIGH/MODERATE/LOW/VERY_LOW)
- Verification rate statistics
- Individual item evidence scores and grades shown in discoveries list
- Color-coded grade badges in report output

### Configuration
- Added `database_url` setting for PostgreSQL connection
- Added `use_database` flag to enable/disable persistence
- Environment variable support: `DATABASE_URL`, `USE_DATABASE`
- New `enable_verification` parameter in orchestrator pipeline

### Dependencies
- Added `psycopg2-binary>=2.9` for PostgreSQL connectivity

### Documentation
- Updated ARCHITECTURE.md with persistence and verification layer details
- Database schema documentation with all evidence fields
- Configuration and usage instructions
- API documentation for verification module

### Tests
- Created comprehensive test suite for verification module (37 tests)
- Unit tests for study design detection
- Unit tests for metadata extraction
- Unit tests for evidence scoring and grading
- Integration tests for full quality assessment pipeline
- Unit tests for persistence layer
- Unit tests for models and configuration
