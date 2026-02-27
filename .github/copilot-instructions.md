# DailyForm Repository Instructions

## Stack

- **Language:** Python 3.13+
- **Build System:** `pyproject.toml` (Setuptools)
- **Dependencies:** `requests`, `mako`
- **Testing:** `pytest`
- **Linting & Formatting:** `ruff`
- **Type Checking:** `pyright` (basic mode)
- **CI:** GitHub Actions

## Coding Standards

- Follow PEP 8 guidelines (enforced by `ruff`).
- Use `src`-layout for the package.
- Ensure all code is compatible with Python 3.13+.
- Use strict type hints where possible, aiming for `pyright` compliance.
- Write tests for all new functionality.
- Ensure `secrets` are not committed to the repository (use `dailyform/secrets.py` only for local development or mocks).

## Development

1.  **Install:** `pip install -e .`
2.  **Test:** `pytest tests/`
3.  **Lint:** `ruff check .`
4.  **Format:** `ruff format .`
5.  **Type Check:** `pyright .`
