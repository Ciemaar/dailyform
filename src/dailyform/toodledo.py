from configparser import ConfigParser
from pprint import pprint

import requests

config = ConfigParser()
# Safely read config without failing if it doesn't exist
config.read(["dailyform.cfg"])

try:
    access_token = config.get("toodledo", "access_token")
except Exception:
    access_token = None

def get_todos():
    """
    Fetches uncompleted tasks from Toodledo using API v3.
    """
    if not access_token:
        print("Error: Toodledo access_token not configured in dailyform.cfg")
        return []

    url = "https://api.toodledo.com/3/tasks/get.php"
    params = {
        "access_token": access_token,
        "comp": 0 # Only get uncompleted tasks
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
