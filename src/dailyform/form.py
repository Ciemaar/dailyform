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
    """Form that includes place information."""

    def prepare(self, partial=False):
        """Prepare place information."""
        self.getPlaceInfo()  # will insert zip_code in facts
        super(PlaceForm, self).prepare(partial)

    def getPlaceInfo(self):
        """Retrieve place info."""
        pass


class UserForm(BaseForm):
    """Form that includes user information."""

    def prepare(self, partial=False):
        """Prepare user information."""
        self.getUserInfo()  # will insert username in facts
        super(UserForm, self).prepare(partial)

    def getUserInfo(self):
        """Retrieve user info."""
        pass


class WeatherMixin(PlaceForm):
    """Mixin to add weather data to a form."""

    def __init__(self, *args, **kwargs):
        super(WeatherMixin, self).__init__(*args, **kwargs)
        self.defaults["weather"] = "No weather"
        self.fail_weather = False

    def prepare(self, partial=False):
        """Prepare weather data."""
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
    """Mixin to add to-do list data to a form."""

    def __init__(self, *args, **kwargs):
        super(TodoMixin, self).__init__(*args, **kwargs)
        self.defaults["todo"] = "No todo"
        self.fail_todo = False

    def prepare(self, partial=False):
        """Prepare to-do list data."""
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
    """Mixin for a simple hardcoded user and place."""

    def getPlaceInfo(self):
        """Hardcode place info."""
        self.facts["zip_code"] = "10001"

    def getUserInfo(self):
        """Hardcode user info."""
        self.facts["username"] = "Andy"


class PersistFactsMixin(BaseForm):
    """Mixin to persist form facts to a local database."""

    def __init__(self, *args, **kwargs):
        super(PersistFactsMixin, self).__init__(*args, **kwargs)
        self.shelf = shelve.open("oldfacts.db")
        self.shelf_key = repr((self.form_type, self.form_id))
        self._closed = False

    def __del__(self):
        if getattr(self, "_closed", True):
            return
        self.shelf[self.shelf_key] = self.facts
        self.shelf.close()
        self._closed = True

    def analyze(self):
        """Analyze and restore persisted facts on failure."""
        if self.shelf_key not in self.shelf:
            return
        for errorKey in self.errors:
            if errorKey in self.shelf[self.shelf_key]:
                self.facts[errorKey] = self.shelf[self.shelf_key][errorKey]


class DailyForm(TextForm, WeatherMixin, TodoMixin, SimpleUserPlaceMixin):  # , PersistFactsMixin):
    """A daily checklist form combining weather and tasks."""

    def __init__(self, form_id, form_date=None):
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

    dt = DailyForm("Andy")
    dt.fail_weather = True
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt

    dt = DailyForm("Andy")
    dt.facts["zip_code"] = "10001"
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt

    dt = DailyForm("Andy")
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt

    dt = DailyForm("Andy")
    dt.fail_weather = True
    dt.prepare()
    dt.prepare()
    print(dt.render_text())
    del dt
