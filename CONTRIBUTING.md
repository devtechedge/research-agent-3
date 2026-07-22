# Contributing to Chronic Lyme Research Agent

Thank you for your interest in contributing to the Chronic Lyme Research Agent project! This document provides guidelines and instructions for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming and inclusive community.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/research-agent-3.git
   cd research-agent-3
   ```
3. Set up the upstream remote:
   ```bash
   git remote add upstream https://github.com/devtechedge/research-agent-3.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Coding Standards

### Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting (line length: 88)
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Write type hints for function parameters and return values

### Running Linters

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/ tests/
```

### Pre-commit Hooks

This project uses pre-commit hooks to automatically check code quality. Install them with:
```bash
pre-commit install
```

Hooks will run automatically before each commit. You can also run them manually:
```bash
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/lyme_agent

# Run specific test file
pytest tests/test_discovery.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Write tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names: `test_<function>_<scenario>_<expected_result>`
- Aim for high test coverage, especially for critical modules
- Mock external API calls using `unittest.mock` or `pytest-mock`

### Test Coverage Goals

We aim for:
- Overall coverage: >80%
- Critical modules (discovery, verification, orchestrator): >90%

## Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following coding standards

3. **Run tests and linters**:
   ```bash
   pytest --cov=src/lyme_agent
   black --check src/ tests/
   ruff check src/ tests/
   ```

4. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "feat: add advanced deduplication logic"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** against the `main` branch
   - Describe your changes clearly
   - Reference any related issues
   - Include test results and coverage information

7. **Address review feedback** promptly

## Reporting Issues

When reporting issues, please include:

- **Description**: Clear description of the problem
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, package versions
- **Logs/Error Messages**: Relevant error messages or logs

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing! 🎉
