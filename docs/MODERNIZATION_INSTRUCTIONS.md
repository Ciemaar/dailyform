# Modernization Instructions and Session History

This document serves as a historical record of all the explicit instructions and directives provided by the user during the modernization of the DailyForm codebase. It outlines the journey from a legacy Python 2 script to a fully modernized Python 3.13+ package.

## 1. Initial Modernization Mandate

- **Goal:** Modernize a legacy Python 2 codebase to Python 3.13+ standards.
- **Project Restructuring:** Convert to a standard `src`-layout (`src/<package_name>`) and use `pyproject.toml` to manage build configuration, dependencies, and tool settings (replacing `setup.py`).
- **Code Migration:** Convert all code from Python 2 to 3 (e.g., `print`, exception handling, dictionary iteration), update standard library imports (`urllib`, `http.client`), and ensure correct handling of bytes vs. str.
- **Dependencies:** Update relevant libraries.
- **Testing & CI:** Migrate existing tests to `pytest`, configure `tox` for multi-environment testing (py310, py311, py312), and create a GitHub Actions workflow (`.github/workflows/ci.yml`) for CI.
- **Quality Assurance:** Configure and run `ruff` for linting and formatting, and `pyright` for type checking (basic mode). Create repository instructions in `.github/copilot-instructions.md`.
- **Documentation:** Update `README.md` with modern installation (`pip install .`), usage, and development instructions.

## 2. API Replacements & Architecture

- **Legacy APIs:** Check if the external APIs used (Weather Underground, Toodledo v2) are still available. Add replacements/alternatives and suggest similar sites without implementing them.
- **Modernization:** Replace Wunderground with OpenWeatherMap and switch to the newest API for Toodledo (API v3).
- **Security:** Address Codacy warnings regarding the use of the MD5 hash algorithm (used in legacy Toodledo authentication). *(Note: Migrating to Toodledo v3 inherently solved this by using OAuth2 instead of MD5 signatures).*

## 3. Tooling & Configuration Refinements

- **Markdown Formatting:** Add and run a markdown formatter (`mdformat`) in the project, making it part of the checks run by GitHub on every PR.
- **Tooling Evaluation:** Evaluate and test alternative tools for formatting, linting, testing, type checking, and documentation. Keep notes on their suitability (`docs/TOOLING_EVALUATION.md`) and adopt the best set of tools.
- **Configuration Consolidation:** Move settings as much as possible into `pyproject.toml` (e.g., migrating `tox.ini` into `pyproject.toml`).
- **Pydantic:** Migrate configuration management to use "pedantic config" (`pydantic-settings` with `.env` files) instead of legacy `ConfigParser` and scattered `secrets.py` files.
- **Pre-commit:** Ensure `pytest` and other development tools are properly included in `pyproject.toml` so developers can install them easily via `[dev]` optional dependencies. Implement `pre-commit` hooks.

## 4. Code Quality & Test Coverage

- **Docstrings:** Enable `ruff` checks for module and function-level docstrings (`D` rules). Add missing docstrings rather than ignoring the rules. Ensure all docstrings are highly meaningful and convey architectural context, not just placeholder text to pass tests.
- **Code Duplication:** Analyze the difference between `form.py` and `form2.py` and factor out as much common code as possible to simplify them (resulting in the creation of `base.py`). Update docstrings to make the intended differences between the two forms clear.
- **State Enums:** Convert loose form state constants (`NEW`, `PREPARED`, etc.) into a strict `IntEnum`.
- **Coverage:** Add checking for test coverage in GitHub hooks. No PR should reduce test coverage. Review test coverage results and add necessary tests to achieve and enforce 100% line coverage.

## 5. Documentation Deliverables

- Add comprehensive User and Developer documentation (`USER_GUIDE.md`, `DEVELOPER_GUIDE.md`).
- Check spelling, punctuation, and grammar of all documentation files.
- Create this document detailing the instructions given throughout the session.
