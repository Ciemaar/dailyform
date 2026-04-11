"""Client integration with Toodledo API."""

from pprint import pprint

import requests

from .config import config


def get_todos():
    """Fetch uncompleted tasks from Toodledo using API v3."""
    access_token = config.toodledo_access_token
    if not access_token:
        print("Error: Toodledo access_token not configured")
        return []

    url = "https://api.toodledo.com/3/tasks/get.php"
    params = {
        "access_token": access_token,
        "comp": 0,  # Only get uncompleted tasks
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Toodledo v3 returns an array where the first element is metadata
        # e.g., [{"num": 1, "total": 1}, {"id": 1234, "title": "Buy milk", ...}]
        if isinstance(data, list) and len(data) > 1:
            return data[1:]
        return []
    except Exception as e:
        print(f"Error fetching to-dos from Toodledo: {e}")
        return []


if __name__ == "__main__":
    todos = get_todos()
    pprint(todos)
