"""Alternative, offline core form logic for dailyform.

This module provides a "dummy" or offline implementation of the forms.
Instead of making external API calls, it uses hardcoded placeholder
data for weather and tasks. It is useful for testing, demonstrations,
or situations where network access is unavailable. It also introduces
a distinct `failures` tracking mechanism not present in the live form.
"""

import os
from datetime import date

from .base import BaseForm, TextForm


class WeatherMixin(BaseForm):
    """Mixin to add weather data to a form."""

    def __init__(self, *args, **kwargs):
        """Initialize the WeatherMixin."""
        super(WeatherMixin, self).__init__(*args, **kwargs)
        self.defaults["weather"] = "Partly Cloudy"
        self.fail_weather = False

    def prepare(self, partial=False):
        """Prepare weather data."""
        if getattr(self, "fail_weather", None):
            self.failures["weather"] = "Forced Failure on weather"
            super(WeatherMixin, self).prepare(partial=True)
        self.facts["weather"] = "Partly Sunny"
        super(WeatherMixin, self).prepare(partial)


class TodoMixin(BaseForm):
    """Mixin to add to-do list data to a form."""

    def __init__(self, *args, **kwargs):
        """Initialize the TodoMixin."""
        super(TodoMixin, self).__init__(*args, **kwargs)
        self.defaults["todos"] = ["Revise todo list"]
        self.fail_todo = False

    def prepare(self, partial=False):
        """Prepare to-do list data."""
        if getattr(self, "fail_todo", False):
            self.failures["todos"] = "Forced Failure on todos"
            super(TodoMixin, self).prepare(partial=True)
        self.facts["todos"] = ["teach class", "prepare class"]
        super(TodoMixin, self).prepare(partial)


class DailyForm(TextForm, WeatherMixin, TodoMixin):
    """A daily checklist form combining weather and tasks."""

    template = """
  {form_type} for {form_id}
  =================================
  Today's Weather:  {weather}
  Your Todo's:  {todos}
  """

    def __init__(self, form_id, form_date=None):
        """Initialize the DailyForm dummy."""
        if form_date is None:
            form_date = date.today()
        super(DailyForm, self).__init__(self.__class__.__name__, form_id, form_date, self.template)


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
