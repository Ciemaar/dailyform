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

⚠️ **WARNING: Deprecated APIs** ⚠️

DailyForm was originally built to integrate with the **Weather Underground API** and the **Toodledo API v2**.

- **Weather Underground** discontinued its free public API around 2018 (after acquisition by IBM). You can no longer get a new, free API key that works with the `/geolookup/forecast10day` endpoint used in this code.
- **Toodledo API v2** is a severely outdated legacy API (Toodledo moved to v3 and OAuth2 years ago).

While the codebase has been modernized to run on Python 3, **these integrations will likely fail** unless you possess grandfathered or enterprise access to these specific legacy endpoints.

If you are modifying this project for modern use, you will need to replace the API calls.

### Legacy Configuration (For Reference Only)

If you have legacy credentials, you can configure them as follows.

#### 1. Toodledo Credentials

Create a file named `dailyform.cfg` in the directory from which you will run DailyForm. It must have the following structure:

```ini
[toodledo]
id = YOUR_TOODLEDO_APP_ID
token = YOUR_TOODLEDO_APP_TOKEN
username = YOUR_TOODLEDO_EMAIL
password = YOUR_TOODLEDO_PASSWORD
```

*Note: DailyForm uses the legacy Toodledo API v2, which requires these credentials for authentication.*

#### 2. Weather Underground API Key

Create a file named `secrets.py` inside the `src/dailyform/` directory (or ensure it's accessible in your Python path under the `dailyform` package) with your API key:

```python
# src/dailyform/secrets.py
WU_API_KEY = "YOUR_WUNDERGROUND_API_KEY"
```

## Recommended Modern Alternatives

If you are a developer looking to adapt this tool, consider migrating to these modern, supported APIs:

### Weather Alternatives

- **[OpenWeatherMap](https://openweathermap.org/api):** Offers a robust free tier for current weather and forecasts.
- **[WeatherAPI](https://www.weatherapi.com/):** Another popular option with a generous free tier.
- **[National Weather Service API (US Only)](https://www.weather.gov/documentation/services-web-api):** Completely free and requires no API key.

### Todo List Alternatives

- **[Toodledo API v3](https://api.toodledo.com/3/):** The modern, supported version of Toodledo's API (uses OAuth2 instead of MD5 hashes).
- **[Todoist Developer API](https://developer.todoist.com/):** A very popular and well-documented REST API for todo lists.
- **[Microsoft To Do / Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/resources/todo-overview):** Powerful enterprise and personal task management API.

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
