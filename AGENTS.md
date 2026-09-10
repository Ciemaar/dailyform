# Agent Instructions

This repository contains specific guidelines and instructions for AI agents working on the codebase. Please adhere to the following rules:

## Project Structure & Tooling
* The repository uses a standard Python `src`-layout.
* `pyproject.toml` (Setuptools) is used for builds.
* `pytest` is used for testing.
* `ruff` is used for linting and formatting.
* `pyright` is used for type checking.
* The project requires Python 3.14+. Dependency installation commands like `pip install -e .[dev]` will fail on older Python versions (e.g., 3.13).

## Configuration & Secrets
* The project uses `.env` files parsed by `pydantic-settings` for configuration and secrets management.
* This replaces older legacy files like `dailyform.cfg` or `secrets.py`. Do not introduce or use these legacy configuration methods.

## Git Workflow & Commits
* All branches being merged and their matching PRs must be explicitly referenced in commit comments and any new PRs.
* When rebasing or merging, features added to the main branch in the intermediate interval must not be removed.

## Security & Privacy
* Avoid hardcoding Personal Identifiable Information (PII) such as real names in source code or tests; use generic placeholders like 'TestUser'.

## License
* The project uses the GPL-3.0-or-later copyleft license.
