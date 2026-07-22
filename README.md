# Chronic Lyme Research Agent

An autonomous research agent that discovers, scores, stores, and emails daily evidence updates about chronic Lyme disease / PTLDS.

## What It Does

- Runs daily from GitHub Actions
- Searches PubMed and ClinicalTrials.gov for new Lyme-related items
- Sends a compact email summary to `devayanmandal@gmail.com`
- Archives each generated report in the repo workflow artifacts path

## Why This Repo Exists

This project is built to show a complete long-horizon research-agent workflow:

- evidence-aware discovery
- daily reporting
- GitHub Actions automation
- Gmail delivery through secrets
- a path toward memory, deduplication, and evidence scoring

## Current Capabilities

- Daily workflow scheduling
- Live Gmail SMTP delivery
- PubMed discovery
- ClinicalTrials.gov discovery
- Markdown report generation
- Simulation mode for local testing

## Required GitHub Secrets

- `EMAIL_USER`
- `EMAIL_APP_PASSWORD`
- `RECIPIENT_EMAIL`

## Run Modes

- `SIMULATION_MODE=true` for local testing without sending email
- `SIMULATION_MODE=false` for live email delivery

## Next Up

- Persist discoveries in Postgres
- Add evidence grading and contradiction tracking
- Add richer report sections and release notes
