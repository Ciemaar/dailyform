# DailyForm Developer Guide

This guide provides information for developers who want to contribute to, test, or extend the DailyForm codebase.

## Project Structure

The project has been modernized to use a standard Python `src`-layout:

- `src/dailyform/`: Contains the main package code.
  - `form.py`, `form2.py`: The core form generation logic and mixins.
  - `toodledo.py`: Interaction with the Toodledo API v3.
  - `weather.py`: Interaction with the OpenWeatherMap API.
  - `config.py`: Pydantic settings configuration.
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

## External APIs

The codebase integrates with modern, fully supported APIs:

### 1. Toodledo API v3

The `toodledo.py` module fetches incomplete tasks via the modern Toodledo API v3 (`https://api.toodledo.com/3/tasks/get.php`). Authentication relies on an OAuth2 `access_token` read from the configuration file.

### 2. OpenWeatherMap API

The `weather.py` module uses the OpenWeatherMap 5-Day / 3-Hour Forecast API to retrieve data, parsing the JSON chunks to compute daily low temperatures and generic weather conditions.

### Legacy Context

*Historically, this project used Weather Underground and Toodledo API v2 (which required MD5 hashing for signatures). Those dependencies have been stripped and fully modernized.*
