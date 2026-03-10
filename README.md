# DailyForm

A rough start at a system for printing a personal, daily checklist. This legacy Python 2 codebase has been modernized to support Python 3.13+.

## Documentation

- **[User Guide](docs/USER_GUIDE.md)**: Instructions on how to install, configure, and use DailyForm to generate checklists.
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Information on project architecture, testing, code quality tools, and contribution guidelines.
- **[Tooling Evaluation](docs/TOOLING_EVALUATION.md)**: Notes and rationale on the selection of modern tools used in this project (`ruff`, `pyright`, etc.).

## Quick Start

### Installation

```bash
pip install .
```

For development:

```bash
pip install -e .[dev]
```

### Basic Usage

Before running, ensure you have configured `dailyform.cfg` and `src/dailyform/secrets.py` as detailed in the [User Guide](docs/USER_GUIDE.md).

```python
from dailyform.form import DailyForm

dt = DailyForm("User")
dt.prepare()
print(dt.render_text())
```

### Running Tests

```bash
pytest tests/
```
