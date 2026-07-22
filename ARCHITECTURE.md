# Architecture

This project uses a small modular pipeline:

- GitHub Actions for scheduling
- Gmail SMTP for delivery
- Provider-agnostic runtime design
- Future Postgres persistence for runs and evidence
- Future source connectors for literature discovery
- Simulation mode for safe local testing
