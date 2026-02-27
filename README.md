# DailyForm

A rough start at a system for printing a personal, daily checklist.

## Installation

This project uses a standard Python package structure.

```bash
pip install .
```

For development, install in editable mode with test dependencies:

```bash
pip install -e .[dev]
```

## Configuration

Create a `dailyform.cfg` file in the root directory (or where you run the script) with the following structure:

```ini
[toodledo]
id = YOUR_APP_ID
token = YOUR_APP_TOKEN
password = YOUR_PASSWORD
username = YOUR_USERNAME
```

Create a `src/dailyform/secrets.py` file with your Weather Underground API key:

```python
WU_API_KEY = "YOUR_WU_API_KEY"
```

## Usage

To generate a daily form:

```python
from dailyform.form import DailyForm

dt = DailyForm("User")
dt.prepare()
print(dt.render_text())
```

## Development

### Running Tests

```bash
pytest tests/
```

### Linting & Formatting

```bash
ruff check .
ruff format .
```

### Type Checking

```bash
pyright .
```
