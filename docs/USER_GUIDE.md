# DailyForm User Guide

Welcome to DailyForm! This tool helps you generate a personal, daily checklist by pulling in your daily weather forecast and your todo list.

## Prerequisites

- Python 3.13 or higher.

## Installation

You can install the package directly from the source directory.

```bash
pip install .
```

## Configuration

DailyForm requires access to a couple of external APIs: Weather Underground and Toodledo. You must provide your API credentials for these services to work.

### 1. Toodledo Credentials

Create a file named `dailyform.cfg` in the directory from which you will run DailyForm. It must have the following structure:

```ini
[toodledo]
id = YOUR_TOODLEDO_APP_ID
token = YOUR_TOODLEDO_APP_TOKEN
username = YOUR_TOODLEDO_EMAIL
password = YOUR_TOODLEDO_PASSWORD
```

*Note: DailyForm uses the legacy Toodledo API v2, which requires these credentials for authentication.*

### 2. Weather Underground API Key

Create a file named `secrets.py` inside the `src/dailyform/` directory (or ensure it's accessible in your Python path under the `dailyform` package) with your API key:

```python
# src/dailyform/secrets.py
WU_API_KEY = "YOUR_WUNDERGROUND_API_KEY"
```

## Usage

Once installed and configured, you can generate your daily form using Python.

### Example Script

Create a Python script (e.g., `generate_form.py`):

```python
from dailyform.form import DailyForm

# Initialize the form with your name
dt = DailyForm("Your Name")

# (Optional) Set a specific zip code for the weather forecast
dt.facts["zip_code"] = "10001"

# Prepare the data (fetches weather and todos)
dt.prepare()

# Render and print the form
print(dt.render_text())
```

Run your script:

```bash
python generate_form.py
```

### Output Example

```text
DailyForm for Your Name
=================================
Today's Weather:  32 degrees F Partly Cloudy
Your Todo's:
Task 1
Task 2
```

## Troubleshooting

- **ConfigParser.NoSectionError**: Ensure `dailyform.cfg` exists in your working directory and has the `[toodledo]` section.
- **ImportError: cannot import name 'WU_API_KEY'**: Ensure `src/dailyform/secrets.py` exists and contains the `WU_API_KEY` variable.
