# Architecture

This project uses a small modular pipeline:

- GitHub Actions for scheduling
- Gmail SMTP for delivery
- Provider-agnostic runtime design
- Postgres persistence for runs and research items (implemented)
- Source connectors for literature discovery (PubMed, ClinicalTrials.gov)
- Simulation mode for safe local testing

## Persistence Layer

The persistence layer (`src/lyme_agent/persistence.py`) provides PostgreSQL storage for:

- **Runs table**: Tracks daily pipeline executions with date, item counts, error counts, and report paths
- **Research items table**: Stores discovered items with title, source, URL, publication date, and summary
- **Deduplication**: Automatic filtering of previously seen items using URL-based uniqueness
- **Query functions**: Retrieve runs and items for historical analysis

### Database Schema

```sql
runs (
    id SERIAL PRIMARY KEY,
    run_date DATE NOT NULL UNIQUE,
    created_at TIMESTAMP,
    items_count INTEGER,
    errors_count INTEGER,
    report_path TEXT
)

research_items (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES runs(id),
    title TEXT,
    source TEXT,
    url TEXT,
    published_at TIMESTAMP,
    summary TEXT,
    discovered_at TIMESTAMP,
    UNIQUE(url, source)
)
```

### Configuration

Enable database persistence by setting environment variables:

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://localhost:5432/lyme_agent`)
- `USE_DATABASE`: Set to `true` to enable persistence (default: `false`)

### Usage

The orchestrator automatically saves runs and items to the database when `USE_DATABASE=true`.
The discovery module filters out previously seen items using the database.
