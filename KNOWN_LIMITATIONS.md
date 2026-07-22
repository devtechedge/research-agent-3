# Known Limitations

Current limitations as of v0.3.0:

- Email content is minimal and could be enriched with more detailed findings
- Deduplication is primarily URL-based; title/abstract matching not yet implemented
- No contradiction tracking between studies with conflicting results
- Memory/retrieval system for historical context not yet implemented
- Limited to PubMed and ClinicalTrials.gov; other sources (Google Scholar, etc.) not integrated
- Evidence scoring uses heuristic rules; ML-based scoring not implemented
- No alert system for high-priority or breakthrough findings
- Report formats limited to markdown; PDF/HTML exports not available

## Completed (No Longer Limitations)

- ✅ Discovery connectors for PubMed and ClinicalTrials.gov implemented
- ✅ PostgreSQL persistence layer with deduplication support
- ✅ Citation verification with URL accessibility checking
- ✅ Evidence scoring system (0-100 points) implemented
- ✅ Evidence grading using Oxford CEBM principles
- ✅ Study design detection and classification
- ✅ Daily automated workflow scheduling via GitHub Actions
- ✅ Gmail SMTP email delivery
