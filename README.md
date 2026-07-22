# Chronic Lyme Research Agent

An autonomous research agent that discovers, scores, stores, and emails daily evidence updates about chronic Lyme disease / PTLDS.

## Goals

- Daily discovery of new evidence
- Strong provenance and citation tracking
- Low-cost incremental updates
- Automated daily email report
- Long-term memory and archival history

## Required GitHub Secrets

- `EMAIL_USER`
- `EMAIL_APP_PASSWORD`
- `RECIPIENT_EMAIL`

## Run Modes

- `SIMULATION_MODE=true` for local testing without sending email
- `SIMULATION_MODE=false` for live email delivery
