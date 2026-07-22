# Chronic Lyme Research Agent

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![GitHub Actions](https://github.com/devtechedge/research-agent-3/actions/workflows/daily.yml/badge.svg)](https://github.com/devtechedge/research-agent-3/actions)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://postgresql.org)
[![Keep a Changelog](https://img.shields.io/badge/changelog-Keep%20a%20Changelog-blue)](CHANGELOG.md)

An autonomous research agent that discovers, verifies, scores, stores, and emails daily evidence updates about chronic Lyme disease / PTLDS from PubMed and ClinicalTrials.gov.

## 🎯 What It Does

- **Runs daily** from GitHub Actions on a scheduled basis
- **Searches PubMed and ClinicalTrials.gov** for new Lyme-related research items
- **Verifies citations** by checking URL accessibility
- **Scores evidence quality** using a 0-100 point scale based on study design, sample size, methodology, and recency
- **Grades evidence** using Oxford CEBM principles (HIGH/MODERATE/LOW/VERY_LOW)
- **Stores discoveries** in PostgreSQL database with deduplication support
- **Sends compact email summaries** with counts, links, and quality metrics
- **Generates markdown reports** archived in workflow artifacts

## 🔬 Why This Repo Exists

This project demonstrates a complete long-horizon research-agent workflow with:

- Evidence-aware discovery with real-time API integration
- Citation verification and quality scoring
- Daily automated reporting with email delivery
- GitHub Actions automation and scheduling
- Gmail delivery through encrypted secrets
- PostgreSQL persistence layer with deduplication
- Evidence grading using established medical hierarchies
- Path toward memory, contradiction tracking, and advanced analytics

## ✨ Current Capabilities

### Core Features
- ✅ Daily workflow scheduling via GitHub Actions
- ✅ Live Gmail SMTP email delivery
- ✅ Real PubMed API discovery connector
- ✅ Real ClinicalTrials.gov API discovery connector
- ✅ Markdown report generation with quality metrics
- ✅ Simulation mode for local testing without live API calls

### Verification & Quality (v0.3.0)
- ✅ Citation verification with URL accessibility checking
- ✅ Evidence scoring system (0-100 points)
- ✅ Evidence grading (HIGH/MODERATE/LOW/VERY_LOW)
- ✅ Study design detection and classification
- ✅ Metadata extraction (PMID, NCT ID, DOI)

### Persistence & Storage (v0.2.0)
- ✅ PostgreSQL database integration
- ✅ Runs table for tracking daily executions
- ✅ Research items table with deduplication
- ✅ Graceful fallback when database unavailable
- ✅ Environment-based configuration

## 📋 Required Configuration

### GitHub Secrets

Set these in your repository settings (Settings → Secrets and variables → Actions):

| Secret | Description | Required |
|--------|-------------|----------|
| `EMAIL_USER` | Gmail address for sending emails | Yes* |
| `EMAIL_APP_PASSWORD` | Gmail app-specific password | Yes* |
| `RECIPIENT_EMAIL` | Email address to receive summaries | Yes* |
| `PUBMED_API_KEY` | NCBI API key for PubMed access | Recommended |
| `DATABASE_URL` | PostgreSQL connection string | Optional |

\* Required for email delivery. Set `SIMULATION_MODE=true` to test without email.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SIMULATION_MODE` | Run without live API calls or email | `false` |
| `USE_DATABASE` | Enable PostgreSQL persistence | `false` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `PUBMED_API_KEY` | NCBI API key | - |
| `GMAIL_SMTP_PASSWORD` | Gmail app password | - |

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/devtechedge/research-agent-3.git
cd research-agent-3
pip install -r requirements.txt
```

### Local Testing

1. Create a `.env` file:
```bash
SIMULATION_MODE=true
USE_DATABASE=false
RECIPIENT_EMAIL=test@example.com
```

2. Run the orchestrator:
```bash
python src/orchestrator.py
```

### Production Deployment

1. Configure GitHub Secrets in repository settings
2. (Optional) Set up PostgreSQL database and add `DATABASE_URL` secret
3. Enable GitHub Actions in repository settings
4. The daily workflow will run automatically at scheduled times

## 📊 Database Schema

The PostgreSQL database includes two main tables:

### runs
- `id`: Primary key
- `run_date`: Date of the research run
- `status`: Run status (completed/failed/partial)
- `items_discovered`: Count of items found
- `items_verified`: Count of items verified
- `started_at`, `completed_at`: Timestamps
- `error_message`: Error details if failed

### research_items
- `id`: Primary key
- `url`: Unique identifier (with constraint)
- `title`, `summary`: Item content
- `source`: PubMed/ClinicalTrials.gov
- `discovered_at`: Discovery timestamp
- `verification_status`: verified/failed/inconclusive/pending
- `score`: Evidence score (0-100)
- `grade`: Evidence grade (HIGH/MODERATE/LOW/VERY_LOW)
- `metadata`: JSONB field for PMID, NCT ID, DOI, etc.

## 📈 Roadmap

See [ROADMAP.md](docs/ROADMAP.md) for detailed future plans.

### In Progress
- [ ] Advanced deduplication beyond URL matching
- [ ] Contradiction tracking between studies
- [ ] Memory and retrieval system
- [ ] Richer daily report sections

### Planned
- [ ] Expanded report formats (PDF, HTML)
- [ ] Alert system for high-priority findings
- [ ] Release tagging and versioning
- [ ] Comprehensive logging configuration
- [ ] Additional data sources (Google Scholar, etc.)

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Test coverage includes:
- Persistence layer operations
- Citation verification
- Evidence scoring and grading
- Discovery connectors
- Report generation

## 📄 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Roadmap](docs/ROADMAP.md) - Future development plans
- [CHANGELOG](CHANGELOG.md) - Version history and release notes
- [Repository Metadata](REPO_METADATA.md) - GitHub setup instructions

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PubMed and ClinicalTrials.gov APIs for research data
- Oxford Centre for Evidence-Based Medicine for grading principles
- GitHub Actions for automation infrastructure
- The chronic Lyme disease research community

## 📧 Contact

For questions or suggestions, please open an issue in this repository.

---

**Built with ❤️ for advancing Lyme disease research**
