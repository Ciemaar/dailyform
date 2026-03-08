"""Alternative core form logic for dailyform."""

import os
from collections.abc import Mapping
from datetime import date

from mako.template import Template

NEW = 10
PARTIAL_PREP = 20
PREPARED = 30
ANALYZED = 40
FORMATTED = 50
RENDERED = 60
CORRUPT = 70


class BaseForm(Mapping):
    """Base class for all forms."""

    def __init__(self, form_type, form_id, form_date):
        self.form_type = form_type
        self.form_id = form_id
        self.form_date = form_date
        self.facts = dict(self.__dict__)  ## facts include form date, type, and id
        self.state = NEW
        self.analysis = {}
        self.formatted_strings = {}
        self.errors = {}
        self.failures = {}
        self.defaults = {}

    def prepare(self, partial=False):
        """Prepare the form.

        :param partial: Whether this is a partial preparation.
        """
        if partial:
            self.state = PARTIAL_PREP
        else:
            self.state = PREPARED

    def analyze(self):
        """Analyze the prepared form."""
        if not self.isPrepared:
            self.prepare()
        self.state = ANALYZED

    def format(self):
        """Format the form output."""
        if not self.isAnalyzed:
            self.analyze()
        self.state = FORMATTED

    @property
    def isCorrupt(self):
        """Return True if form is corrupt."""
        return self.state >= CORRUPT

    @property
    def isPrepared(self):
        """Return True if form is prepared."""
        return self.state >= PREPARED and not self.isCorrupt

    @property
    def isAnalyzed(self):
        """Return True if form is analyzed."""
        return self.state >= ANALYZED and not self.isCorrupt

    @property
    def isFormatted(self):
        """Return True if form is formatted."""
        return self.state >= FORMATTED and not self.isCorrupt

    def __getitem__(self, key):
        """BaseForm can be used as a dictionary, in which case it will search all three internal dicts."""
        return self.formatted_strings.get(key, self.analysis.get(key, self.facts[key]))

    def __iter__(self):
        for key in set(self.formatted_strings.keys()) | set(self.analysis.keys()) | set(self.facts.keys()):
            yield key

    def __len__(self):
        return len(set(self.formatted_strings.keys()) | set(self.analysis.keys()) | set(self.facts.keys()))


class WeatherMixin(BaseForm):
    """Mixin to add weather data to a form."""

    def __init__(self, *args, **kwargs):
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


class MakoForm(BaseForm):
    """Form that renders using Mako templates."""

    def __init__(self, form_type, form_id, form_date, filename):
        super(MakoForm, self).__init__(form_type, form_id, form_date)
        self.template = Template(filename)

    def render_html(self):
        """Render the form as HTML."""
        if not self.isFormatted:
            self.format()
        ret = self.template.render_context(self)
        self.state = RENDERED
        return ret


class TextForm(BaseForm):
    """Form that renders using standard string formatting."""

    def __init__(self, form_type, form_id, form_date, template):
        super(TextForm, self).__init__(form_type, form_id, form_date)
        self.template = template

    def render_text(self):
        """Render the form as plain text."""
        if not self.isFormatted:
            self.format()
        ret = self.template.format(**self)
        self.state = RENDERED
        return ret


class DailyForm(TextForm, WeatherMixin, TodoMixin):
    """A daily checklist form combining weather and tasks."""

    template = """
  {form_type} for {form_id}
  =================================
  Today's Weather:  {weather}
  Your Todo's:  {todos}
  """

    def __init__(self, form_id, form_date=None):
        if form_date is None:
            form_date = date.today()
        super(DailyForm, self).__init__(self.__class__.__name__, form_id, form_date, self.template)


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
