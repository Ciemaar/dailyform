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

DailyForm requires access to a couple of external APIs: OpenWeatherMap and Toodledo API v3. You must provide your API credentials for these services to work.

Create a `.env` file in the root directory from which you will run DailyForm with your API credentials:

```ini
TOODLEDO_ACCESS_TOKEN=YOUR_TOODLEDO_API_V3_ACCESS_TOKEN
OWM_API_KEY=YOUR_OPENWEATHERMAP_API_KEY
```

*Note: You can also export these directly as environment variables. The Toodledo API v3 requires an OAuth2 access token. You can obtain one by registering an application in your Toodledo developer console.*

## Recommended Alternatives

If you wish to fork and extend this tool, you could adapt the API modules to use other alternatives:

### Weather Alternatives

- **[WeatherAPI](https://www.weatherapi.com/):** Another popular option with a generous free tier.
- **[National Weather Service API (US Only)](https://www.weather.gov/documentation/services-web-api):** Completely free and requires no API key.

### Todo List Alternatives

- **[Google Tasks API](https://developers.google.com/tasks):** A lightweight API that integrates seamlessly with Google Workspace.
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
