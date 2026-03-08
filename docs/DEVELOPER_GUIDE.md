# DailyForm Developer Guide

This guide provides information for developers who want to contribute to, test, or extend the DailyForm codebase.

## Project Structure

The project has been modernized to use a standard Python `src`-layout:

- `src/dailyform/`: Contains the main package code.
  - `form.py`, `form2.py`: The core form generation logic and mixins.
  - `toodledo.py`: Interaction with the legacy Toodledo API.
  - `weather.py`: Interaction with the Weather Underground API.
  - `secrets.py.example`: Example file for required API keys.
- `tests/`: Contains the `pytest` test suite.
- `pyproject.toml`: Project metadata, dependencies, and tooling configuration.
- `tox.ini`: Configuration for multi-environment testing.
- `.github/workflows/ci.yml`: GitHub Actions CI pipeline.

## Setting Up the Development Environment

1. Clone the repository.
1. Create and activate a virtual environment.
1. Install the package in editable mode with development dependencies:

```bash
pip install -e .[dev]
```

## Testing

We use `pytest` for running tests. The tests are designed to run without needing real API credentials or network access by heavily mocking external dependencies (`requests`, `urllib`).

To run the test suite:

```bash
pytest tests/
```

To run tests across multiple Python versions (3.10, 3.11, 3.12, 3.13), use `tox`:

```bash
tox
```

### Note on Legacy Code Testing

The `toodledo.py` and `weather.py` modules execute code at the module level (e.g., making API requests immediately upon import). To make these testable, the test files (`tests/test_*.py`) mock the relevant standard library and third-party modules (`requests`, `urllib.request`, `configparser`) in `sys.modules` *before* importing the `dailyform` modules.

## Code Quality

We enforce code quality using several tools, all configured in `pyproject.toml`.

### Linting and Formatting (Ruff)

We use `ruff` to ensure code style consistency and catch common errors.

```bash
# Check for linting errors
ruff check .

# Automatically fix fixable linting errors
ruff check --fix .

# Format the code
ruff format .
```

### Type Checking (Pyright)

We use `pyright` in "basic" mode for static type checking.

```bash
pyright .
```

### Markdown Formatting (mdformat)

Documentation and markdown files should be formatted using `mdformat`.

```bash
# Format markdown files
mdformat .

# Check formatting (used in CI)
mdformat --check .
```

## Legacy API Constraints

### Toodledo API v2 & MD5

The `toodledo.py` module interacts with an older version of the Toodledo API which strictly requires the use of the **MD5** hashing algorithm for generating authentication signatures and keys.

Because MD5 is considered cryptographically insecure, security linters (like Bandit or Codacy) will flag its usage. To address this while maintaining compatibility with the API, we use `usedforsecurity=False` in the `hashlib.md5()` calls:

```python
hashlib.md5(..., usedforsecurity=False)
```

This explicitly signals that the algorithm is being used for non-security purposes (legacy API compatibility), preventing it from blocking execution in FIPS-compliant environments and silencing some security warnings. **Do not replace MD5 with a more secure algorithm like SHA-256 unless the Toodledo API endpoint is updated to support it.**
