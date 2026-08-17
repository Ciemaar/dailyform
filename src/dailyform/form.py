"""Core form logic for dailyform.

This module provides the primary, "live" implementation of the forms.
It actively integrates with external APIs (OpenWeatherMap for weather
and Toodledo for tasks) to fetch real data when generating the form.
"""

import os
import shelve
from datetime import date

from .base import BaseForm, TextForm
from .toodledo import get_todos
from .weather import get_weather_forecast


class PlaceForm(BaseForm):
    """Base mixin for forms requiring geographical location context."""

    def prepare(self, partial=False):
        """Inject place data into the form facts before continuing the pipeline."""
        self.getPlaceInfo()  # will insert zip_code in facts
        super(PlaceForm, self).prepare(partial)

    def getPlaceInfo(self):
        """Retrieve and store place info (e.g. zip_code) into `self.facts`.

        Must be implemented by concrete subclasses.
        """
        pass


class UserForm(BaseForm):
    """Base mixin for forms requiring user context."""

    def prepare(self, partial=False):
        """Inject user data into the form facts before continuing the pipeline."""
        self.getUserInfo()  # will insert username in facts
        super(UserForm, self).prepare(partial)

    def getUserInfo(self):
        """Retrieve and store user info (e.g. username) into `self.facts`.

        Must be implemented by concrete subclasses.
        """
        pass


class WeatherMixin(PlaceForm):
    """Mixin that fetches live weather forecasts for the form's zip code."""

    def __init__(self, *args, **kwargs):
        """Initialize defaults and failure state flags for the weather module."""
        super(WeatherMixin, self).__init__(*args, **kwargs)
        self.defaults["weather"] = "No weather"
        self.fail_weather = False

    def prepare(self, partial=False):
        """Fetch the 5-day forecast from OpenWeatherMap and store it in facts."""
        if "zip_code" not in self.facts:
            return super(WeatherMixin, self).prepare(True)
        if getattr(self, "fail_weather", False):
            self.errors["weather"] = "Unable to retrieve"
            return super(WeatherMixin, self).prepare(True)

        zip_code = self.facts.get("zip_code", "10001")
        daily_forecasts = get_weather_forecast(zip_code)

        self.facts["weather"] = daily_forecasts

        super(WeatherMixin, self).prepare(partial)

    def format(self):
        """Format weather output string."""
        today = self.facts.get("weather", {}).get(date.today(), None)
        if today:
            self.formatted_strings["weather"] = "{low} degrees F {conditions}".format(
                low=today["low"]["fahrenheit"], conditions=today["conditions"]
            )
        super(WeatherMixin, self).format()


class TodoMixin(UserForm):
    """Mixin that fetches live task lists from the Toodledo API."""

    def __init__(self, *args, **kwargs):
        """Initialize defaults and failure state flags for the to-do module."""
        super(TodoMixin, self).__init__(*args, **kwargs)
        self.defaults["todo"] = "No todo"
        self.fail_todo = False

    def prepare(self, partial=False):
        """Fetch uncompleted tasks from Toodledo and store them in facts."""
        if "username" not in self.facts:
            return super(TodoMixin, self).prepare(True)
        if getattr(self, "fail_todo", False):
            self.errors["todo"] = "Unable to retrieve"
        self.facts["todo"] = get_todos()
        super(TodoMixin, self).prepare(partial)

    def format(self):
        """Format to-do output string."""
        todos = self.facts.get("todo", [])
        self.formatted_strings["todo"] = "\n".join(x["title"] for x in todos if "title" in x)
        super(TodoMixin, self).format()


class SimpleUserPlaceMixin(UserForm, PlaceForm):
    """Utility mixin that fulfills user and place dependencies with static data."""

    def getPlaceInfo(self):
        """Inject a static Manhattan zip code (10001) into facts."""
        self.facts["zip_code"] = "10001"

    def getUserInfo(self):
        """Inject a static username ('TestUser') into facts."""
        self.facts["username"] = "TestUser"


class PersistFactsMixin(BaseForm):
    """Mixin that caches successfully fetched facts to a local disk database.

    This allows the form to degrade gracefully. If a subsequent fetch fails
    (e.g. API is down), it can restore the last known good facts during analysis.
    """

    def __init__(self, *args, **kwargs):
        """Open the local shelf database using the form's identity as a key."""
        super(PersistFactsMixin, self).__init__(*args, **kwargs)
        self.shelf = shelve.open("oldfacts.db")
        self.shelf_key = repr((self.form_type, self.form_id))
        self._closed = False

    def __del__(self):
        """Save the current facts to the shelf database and safely close it."""
        if getattr(self, "_closed", True):
            return
        self.shelf[self.shelf_key] = self.facts
        self.shelf.close()
        self._closed = True

    def analyze(self):
        """Restore missing or failed facts from the persistent local cache."""
        if self.shelf_key not in self.shelf:
            return
        for errorKey in self.errors:
            if errorKey in self.shelf[self.shelf_key]:
                self.facts[errorKey] = self.shelf[self.shelf_key][errorKey]
        super(PersistFactsMixin, self).analyze()


class DailyForm(TextForm, WeatherMixin, TodoMixin, SimpleUserPlaceMixin):  # , PersistFactsMixin):
    """A daily checklist form combining weather and tasks."""

    def __init__(self, form_id, form_date=None):
        """Initialize the DailyForm with a preset template."""
        template = """
    {form_type} for {form_id}
    ==========================
    {weather}
    {todo}
    """
        super(DailyForm, self).__init__(
            form_type=self.__class__.__name__, form_id=form_id, form_date=form_date, template=template
        )


if __name__ == "__main__":
    if os.path.exists("oldfacts.db"):
        os.remove("oldfacts.db")

    dt = DailyForm("TestUser")
    dt.fail_weather = True
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt

    dt = DailyForm("TestUser")
    dt.facts["zip_code"] = "10001"
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt

    dt = DailyForm("TestUser")
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt

    dt = DailyForm("TestUser")
    dt.fail_weather = True
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt
