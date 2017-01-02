import os
from collections import Mapping
from datetime import date

import mako

NEW = 10
PARTIAL_PREP = 20
PREPARED = 30
ANALYZED = 40
FORMATTED = 50
RENDERED = 60
CORRUPT = 70


class BaseForm(Mapping):
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
        if partial:
            self.state = PARTIAL_PREP
        else:
            self.state = PREPARED

    def analyze(self):
        if not self.isPrepared:
            self.prepare()
        self.state = ANALYZED

    def format(self):
        if not self.isAnalyzed:
            self.analyze
        self.state = FORMATTED

    @property
    def isCorrupt(self):
        return self.state >= CORRUPT

    @property
    def isPrepared(self):
        return self.state >= PREPARED and not self.isCorrupt

    @property
    def isAnalyzed(self):
        return self.state >= ANALYZED and not self.isCorrupt

    @property
    def isFormatted(self):
        return self.state >= FORMATTED and not self.isCorrupt

    def __getitem__(self, key):
        """BaseForm can be used as a dictionary, in which case it will search all three internal dicts"""
        return self.formatted_strings.get(key, self.analysis.get(key, self.facts[key]))

    def __iter__(self):
        for key in set(self.formatted_strings.keys() + self.analysis.keys() + self.facts.keys()):
            yield key

    def __len__(self):
        return len(set(self.formatted_strings.keys() + self.analysis.keys() + self.facts.keys()))

class WeatherMixin(BaseForm):
    def __init__(self, *args, **kwargs):
        super(WeatherMixin, self).__init__(*args, **kwargs)
        self.defaults['weather'] = 'Partly Cloudy'

    def prepare(self, partial=False):
        if getattr(self, 'fail_weather',None):
            self.failures['weather'] = 'Forced Failure on weather'
            super(WeatherMixin, self).prepare(partial=True)
        self.facts['weather'] = 'Partly Sunny'
        super(WeatherMixin, self).prepare(partial)


class TodoMixin(BaseForm):
    def __init__(self, *args, **kwargs):
        super(TodoMixin, self).__init__(*args, **kwargs)
        self.defaults['todos'] = ['Revise todo list']

    def prepare(self, partial=False):
        if getattr(self, 'fail_todo',False):
            self.failures['todos'] = 'Forced Failure on todos'
            super(TodoMixin, self).prepare(partial=True)
        self.facts['todos'] = ['teach class', 'prepare class']
        super(TodoMixin, self).prepare(partial)


class MakoForm(BaseForm):
    def __init__(self, form_type, form_id, form_date, filename):
        super(MakoForm, self, form_type, form_id, form_date).__init__()
        self.template = mako.template.Template(filename)

    def render_html(self):
        if not self.isFormatted:
            self.format()
        ret = self.template.render_context(self)
        self.state = RENDERED
        return ret


class TextForm(BaseForm):
    def __init__(self, form_type, form_id, form_date, template):
        super(TextForm, self).__init__(form_type, form_id, form_date)
        self.template = template

    def render_text(self):
        if not self.isFormatted:
            self.format()
        ret = self.template.format(**self)
        self.state = RENDERED
        return ret


class DailyForm(TextForm, WeatherMixin, TodoMixin):
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

if __name__ == '__main__':
    if os.path.exists("oldfacts.db"):
        os.remove("oldfacts.db")

    dt = DailyForm("Andy")
    dt.fail_weather = True
    dt.prepare()
    dt.prepare()
    print dt.render_text()
    del dt

    dt = DailyForm("Andy")
    dt.facts["zip_code"] = "10001"
    dt.prepare()
    dt.prepare()
    print dt.render_text()
    del dt

    dt = DailyForm("Andy")
    dt.prepare()
    dt.prepare()
    print dt.render_text()
    del dt

    dt = DailyForm("Andy")
    dt.fail_weather = True
    dt.prepare()
    dt.prepare()
    print dt.render_text()
    del dt