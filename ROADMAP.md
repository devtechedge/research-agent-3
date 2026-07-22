# Roadmap

## Phase 1 ✅ COMPLETED

- Finalize architecture and repo conventions

## Phase 2 🔄 IN PROGRESS

- ✅ Add real source connectors for PubMed and ClinicalTrials.gov
- ✅ Persist runs and items in Postgres (IMPLEMENTED)
- 📋 Generate richer daily reports (NEXT)

## Phase 3 📋 PLANNED

- 📋 Add deduplication, contradiction tracking, and citation verification
  - ✅ Basic database deduplication implemented
  - 📋 Advanced deduplication algorithms
  - 📋 Contradiction tracking
  - 📋 Citation verification
- 📋 Improve memory and retrieval
- 📋 Expand report formats and alerts

## Completed Features

### Persistence Layer (v0.2.0)
- PostgreSQL database schema with `runs` and `research_items` tables
- Automatic saving of daily runs and discovered items
- Database-driven deduplication to filter previously seen items
- Query functions for historical data retrieval
- Configurable via `DATABASE_URL` and `USE_DATABASE` environment variables
- Graceful fallback when database is unavailable

### Configuration
- Added `database_url` setting for PostgreSQL connection
- Added `use_database` flag to enable/disable persistence
- Environment variable support: `DATABASE_URL`, `USE_DATABASE`

### Dependencies
- Added `psycopg2-binary>=2.9` for PostgreSQL connectivity

### Documentation
- Updated ARCHITECTURE.md with persistence layer details
- Database schema documentation
- Configuration and usage instructions

### Tests
- Created tests directory with persistence layer tests
- Unit tests for models and configuration
- Integration test framework ready for database testing
