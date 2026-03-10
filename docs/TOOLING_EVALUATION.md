# Tooling Evaluation Notes

As part of the modernization effort for DailyForm, several tools were evaluated for code formatting, linting, type checking, and testing.

## Formatting & Linting

**Winner: `ruff`**

- **Ruff vs Black & Flake8:** Traditionally, Python projects relied on a combination of `black` for formatting and `flake8` (along with many plugins) for linting. We evaluated `ruff`, a Rust-based tool that performs both duties.
- **Why Ruff?** It is orders of magnitude faster than the traditional tools and correctly formats code to be highly compatible with `black`'s style. It also consolidates dozens of separate `flake8` plugins (like `pydocstyle` for `D` rules) into a single dependency, dramatically simplifying `pyproject.toml`.

## Type Checking

**Winner: `pyright`**

- **Pyright vs Mypy:** `mypy` is the oldest and most standard type checker for Python. However, during evaluation, running `mypy` natively failed due to missing stubs for third-party libraries like `requests` and `mako` (requiring manual installation of `types-requests`, etc.).
- **Why Pyright?** `pyright` (which powers VS Code's Pylance) operates exceptionally well in "basic" mode without requiring an exhaustive suite of third-party stub packages to be explicitly defined. It infers types well and is significantly faster, making it a better fit for a legacy migration where fully annotating every external library boundary is out of scope.

## Testing

**Winner: `pytest` + `pytest-cov`**

- **Pytest vs Unittest:** While `unittest` is built into the standard library, `pytest` offers a much more powerful fixture system, easier-to-read assertion introspection, and a vast plugin ecosystem.
- **Coverage:** We adopted `pytest-cov` to enforce 100% line coverage automatically, natively integrating with `pytest` via `pyproject.toml` configuration.

## Documentation Formatting

**Winner: `mdformat`**

- To ensure consistent documentation formatting, we evaluated `mdformat`. It enforces a strict, standard markdown style without the configuration overhead of heavier tools.

## Pre-commit Framework

**Winner: `pre-commit`**

- To tie these disparate tools together and enforce them locally *before* code is pushed to CI, we adopted `pre-commit`. It natively supports hooks for `ruff`, `mdformat`, and `pyright`, ensuring developers catch issues instantly.
