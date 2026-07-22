"""Database persistence layer for storing runs and research items."""

from datetime import datetime
from typing import Optional
import logging

from .models import ResearchItem, EvidenceGrade, StudyDesign
from .config import settings

logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import execute_batch
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not installed. Database persistence disabled.")


def get_connection():
    """Get a database connection using settings."""
    if not PSYCOPG2_AVAILABLE:
        raise ImportError("psycopg2 is required for database persistence")
    
    conn = psycopg2.connect(settings.database_url)
    return conn


def init_db():
    """Initialize the database schema."""
    if not PSYCOPG2_AVAILABLE:
        logger.warning("Cannot initialize database: psycopg2 not available")
        return
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create runs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id SERIAL PRIMARY KEY,
                    run_date DATE NOT NULL UNIQUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    items_count INTEGER NOT NULL DEFAULT 0,
                    errors_count INTEGER NOT NULL DEFAULT 0,
                    report_path TEXT
                )
            """)
            
            # Create research_items table with verification and evidence fields
            cur.execute("""
                CREATE TABLE IF NOT EXISTS research_items (
                    id SERIAL PRIMARY KEY,
                    run_id INTEGER REFERENCES runs(id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT NOT NULL,
                    published_at TIMESTAMP,
                    summary TEXT,
                    discovered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Verification fields
                    is_verified BOOLEAN DEFAULT FALSE,
                    verification_status TEXT DEFAULT 'pending',
                    verification_date TIMESTAMP,
                    verification_notes TEXT[],
                    
                    -- Evidence scoring fields
                    evidence_score REAL DEFAULT 0.0,
                    study_design TEXT DEFAULT 'unknown',
                    evidence_grade TEXT DEFAULT 'low',
                    
                    -- Metadata fields
                    doi TEXT,
                    pmid TEXT,
                    nct_id TEXT,
                    journal_name TEXT,
                    sample_size INTEGER,
                    has_control_group BOOLEAN DEFAULT FALSE,
                    is_randomized BOOLEAN DEFAULT FALSE,
                    is_blinded BOOLEAN DEFAULT FALSE,
                    funding_source TEXT,
                    conflicts_of_interest TEXT,
                    
                    UNIQUE(url, source)
                )
            """)
            
            # Create index on url for deduplication checks
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_research_items_url 
                ON research_items(url)
            """)
            
            # Create index on run_date for querying by date
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_run_date 
                ON runs(run_date)
            """)
            
            # Create index on evidence_score for quality filtering
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_research_items_evidence_score 
                ON research_items(evidence_score DESC)
            """)
            
            # Create index on evidence_grade for filtering by grade
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_research_items_evidence_grade 
                ON research_items(evidence_grade)
            """)
            
        conn.commit()
        logger.info("Database schema initialized successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()


def save_run(run_date: str, items_count: int, errors_count: int, report_path: Optional[str] = None) -> int:
    """Save a run record and return its ID."""
    if not PSYCOPG2_AVAILABLE:
        logger.warning("Cannot save run: psycopg2 not available")
        return -1
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO runs (run_date, items_count, errors_count, report_path)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (run_date) DO UPDATE SET
                    items_count = EXCLUDED.items_count,
                    errors_count = EXCLUDED.errors_count,
                    report_path = EXCLUDED.report_path
                RETURNING id
            """, (run_date, items_count, errors_count, report_path))
            
            run_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Saved run {run_id} for date {run_date}")
        return run_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to save run: {e}")
        raise
    finally:
        conn.close()


def save_research_items(run_id: int, items: list[ResearchItem]):
    """Save research items for a given run."""
    if not PSYCOPG2_AVAILABLE:
        logger.warning("Cannot save items: psycopg2 not available")
        return
    
    if not items:
        return
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Prepare data for batch insert
            data = []
            for item in items:
                data.append((
                    run_id,
                    item.title,
                    item.source,
                    item.url,
                    item.published_at,
                    item.summary,
                    # Verification fields
                    item.is_verified,
                    item.verification_status,
                    item.verification_date,
                    item.verification_notes if item.verification_notes else None,
                    # Evidence scoring fields
                    item.evidence_score,
                    item.study_design.value if item.study_design else 'unknown',
                    item.evidence_grade.value if item.evidence_grade else 'low',
                    # Metadata fields
                    item.doi,
                    item.pmid,
                    item.nct_id,
                    item.journal_name,
                    item.sample_size,
                    item.has_control_group,
                    item.is_randomized,
                    item.is_blinded,
                    item.funding_source,
                    item.conflicts_of_interest
                ))
            
            # Use execute_batch for efficient insertion
            execute_batch(
                cur,
                """
                INSERT INTO research_items (
                    run_id, title, source, url, published_at, summary,
                    is_verified, verification_status, verification_date, verification_notes,
                    evidence_score, study_design, evidence_grade,
                    doi, pmid, nct_id, journal_name, sample_size,
                    has_control_group, is_randomized, is_blinded,
                    funding_source, conflicts_of_interest
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url, source) DO UPDATE SET
                    is_verified = EXCLUDED.is_verified,
                    verification_status = EXCLUDED.verification_status,
                    verification_date = EXCLUDED.verification_date,
                    verification_notes = EXCLUDED.verification_notes,
                    evidence_score = EXCLUDED.evidence_score,
                    study_design = EXCLUDED.study_design,
                    evidence_grade = EXCLUDED.evidence_grade,
                    doi = EXCLUDED.doi,
                    pmid = EXCLUDED.pmid,
                    nct_id = EXCLUDED.nct_id,
                    journal_name = EXCLUDED.journal_name,
                    sample_size = EXCLUDED.sample_size,
                    has_control_group = EXCLUDED.has_control_group,
                    is_randomized = EXCLUDED.is_randomized,
                    is_blinded = EXCLUDED.is_blinded,
                    funding_source = EXCLUDED.funding_source,
                    conflicts_of_interest = EXCLUDED.conflicts_of_interest
                """,
                data
            )
        conn.commit()
        logger.info(f"Saved {len(items)} research items for run {run_id}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to save research items: {e}")
        raise
    finally:
        conn.close()


def get_existing_urls(sources: list[str]) -> set[str]:
    """Get set of URLs already in the database for deduplication."""
    if not PSYCOPG2_AVAILABLE:
        return set()
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            placeholders = ','.join(['%s'] * len(sources))
            cur.execute(f"""
                SELECT url FROM research_items
                WHERE source IN ({placeholders})
            """, sources)
            
            existing = {row[0] for row in cur.fetchall()}
        return existing
    except Exception as e:
        logger.error(f"Failed to get existing URLs: {e}")
        return set()
    finally:
        conn.close()


def get_runs(limit: int = 30) -> list[dict]:
    """Get recent runs."""
    if not PSYCOPG2_AVAILABLE:
        return []
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, run_date, items_count, errors_count, report_path, created_at
                FROM runs
                ORDER BY run_date DESC
                LIMIT %s
            """, (limit,))
            
            columns = ['id', 'run_date', 'items_count', 'errors_count', 'report_path', 'created_at']
            runs = [dict(zip(columns, row)) for row in cur.fetchall()]
        return runs
    except Exception as e:
        logger.error(f"Failed to get runs: {e}")
        return []
    finally:
        conn.close()


def get_items_for_run(run_id: int) -> list[ResearchItem]:
    """Get research items for a specific run."""
    if not PSYCOPG2_AVAILABLE:
        return []
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT title, source, url, published_at, summary,
                       is_verified, verification_status, verification_date, verification_notes,
                       evidence_score, study_design, evidence_grade,
                       doi, pmid, nct_id, journal_name, sample_size,
                       has_control_group, is_randomized, is_blinded,
                       funding_source, conflicts_of_interest
                FROM research_items
                WHERE run_id = %s
                ORDER BY id
            """, (run_id,))
            
            items = []
            for row in cur.fetchall():
                # Convert study_design string back to enum
                study_design = StudyDesign.UNKNOWN
                if row[10]:  # study_design column
                    try:
                        study_design = StudyDesign(row[10])
                    except ValueError:
                        study_design = StudyDesign.UNKNOWN
                
                # Convert evidence_grade string back to enum
                evidence_grade = EvidenceGrade.LOW
                if row[11]:  # evidence_grade column
                    try:
                        evidence_grade = EvidenceGrade(row[11])
                    except ValueError:
                        evidence_grade = EvidenceGrade.LOW
                
                items.append(ResearchItem(
                    title=row[0],
                    source=row[1],
                    url=row[2],
                    published_at=row[3],
                    summary=row[4],
                    # Verification fields
                    is_verified=row[5] or False,
                    verification_status=row[6] or 'pending',
                    verification_date=row[7],
                    verification_notes=row[8] or [],
                    # Evidence scoring fields
                    evidence_score=row[9] or 0.0,
                    study_design=study_design,
                    evidence_grade=evidence_grade,
                    # Metadata fields
                    doi=row[12],
                    pmid=row[13],
                    nct_id=row[14],
                    journal_name=row[15],
                    sample_size=row[16],
                    has_control_group=row[17] or False,
                    is_randomized=row[18] or False,
                    is_blinded=row[19] or False,
                    funding_source=row[20],
                    conflicts_of_interest=row[21]
                ))
        return items
    except Exception as e:
        logger.error(f"Failed to get items for run: {e}")
        return []
    finally:
        conn.close()
