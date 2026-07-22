# GitHub Repository Metadata

Use the following information to update your GitHub repository settings at:
https://github.com/devtechedge/research-agent-3/settings

## Repository Description

Copy and paste this into the "About" section:

```
Autonomous research agent that daily scans PubMed and ClinicalTrials.gov for Lyme disease/PTLDS studies, verifies citations, scores evidence quality, and delivers email summaries with markdown reports.
```

## Topics

Add these topics to your repository (comma-separated):

```
lyme-disease, research-agent, pubmed, clinical-trials, evidence-scoring, citation-verification, github-actions, python, postgresql, automated-research, ptlds, medical-research, literature-review, evidence-grading
```

## Recommended Categories

- **Primary Category**: Science / Health & Medicine
- **Secondary Category**: Automation / Research Tools

## Social Preview Image Suggestions

Consider adding a social preview image that includes:
- Project name: "Chronic Lyme Research Agent"
- Tagline: "Automated Evidence Discovery & Verification"
- Visual elements: Medical/research icons, data flow diagram

## Release Notes Template

When creating releases on GitHub, use this template:

```markdown
## What's Changed

### New Features
- [List key features]

### Improvements
- [List improvements]

### Bug Fixes
- [List fixes]

### Technical Changes
- [List technical updates]

## Installation

```bash
git clone https://github.com/devtechedge/research-agent-3.git
cd research-agent-3
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `GMAIL_SMTP_PASSWORD`: Gmail app password for email delivery
- `PUBMED_API_KEY`: NCBI API key for PubMed access

## Contributors

Thanks to all contributors!

## Full Changelog

See CHANGELOG.md for complete history.
```

## Repository Badges

Add these badges to your README.md:

```markdown
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![GitHub Actions](https://github.com/devtechedge/research-agent-3/workflows/Daily%20Research%20Run/badge.svg)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)
![Last Run](https://img.shields.io/badge/dynamic/json?label=last%20run&query=$.last_run&url=https://raw.githubusercontent.com/devtechedge/research-agent-3/qwen-code/data/runs.json)
```

## GitHub Pages (Optional)

To enable a project website:
1. Go to Settings > Pages
2. Select branch: `qwen-code` or `main`
3. Folder: `/docs` (after creating docs folder)
4. Save

This can host auto-generated documentation in the future.
