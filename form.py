from datetime import date
import os
import shelve
import urllib2
import json
from collections import MutableMapping, Mapping
import mako
import requests
from toodledo import get_todos

from util import *

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
        self.facts = dict(self.__dict__)
        self.state = NEW
        self.analysis = {}
        self.formatted_strings = {}
        self.errors = {}
        self.defaults = {}

    def prepare(self, partial=False):
        if partial:
            self.state = PARTIAL_PREP
        else:
            self.state = PREPARED

    def analyze(self):
        self.state = ANALYZED

    def format(self):
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
        return self.formatted_strings.get(key, self.analysis.get(key, self.facts.get(key, self.defaults.get(key,None))))

    def __iter__(self):
        for key in set(self.formatted_strings.keys() + self.analysis.keys() + self.facts.keys() + self.defaults.keys()):
            yield key

    def __len__(self):
        return len(set(self.formatted_strings.keys() + self.analysis.keys() + self.facts.keys() + self.defaults.keys()))

    def __call__(self):
        if not self.isPrepared:
            self.prepare()
        if not self.isAnalyzed:
            self.analyze()
        if not self.isFormatted:
            self.format()


class PlaceForm(BaseForm):
    def prepare(self, partial=False):
        self.getPlaceInfo()  # will insert zip_code in facts
        super(PlaceForm, self).prepare(partial)
    def getPlaceInfo(self):
        #self.facts['zip_code'] = ""
        pass

class UserForm(BaseForm):
    def prepare(self, partial=False):
        self.getUserInfo()  # will insert username in facts
        super(UserForm, self).prepare(partial)
    def getUserInfo(self):
        #self.facts['username'] = ""
        pass


class WeatherMixin(PlaceForm):
    def __init__(self, *args, **kwargs):
        super(WeatherMixin, self).__init__(*args, **kwargs)
        self.defaults['weather'] = "No weather"

    def prepare(self, partial=False):
        if "zip_code" not in self.facts:
            return super(WeatherMixin, self).prepare(True)
        if getattr(self, 'fail_weather', False):
            self.errors['weather'] = "Unable to retrieve"
            return super(WeatherMixin, self).prepare(True)

        f = urllib2.urlopen(
            'http://api.wunderground.com/api/3937ebdc37ddd735/geolookup/forecast10day/q/{zip_code}.json'.format(**self))
        json_string = f.read()
        parsed_json = json.loads(json_string)
        self.facts['weather'] = {}
        for forecast in parsed_json['forecast']['simpleforecast']['forecastday']:
            self.facts['weather'][date(day=forecast['date']['day'], month=forecast['date']['month'],
                year=forecast['date']['year'])] = forecast
        f.close()
        super(WeatherMixin, self).prepare(partial)

    def format(self):
        today = self.facts.get('weather', {}).get(date.today(), None)
        if today:
            self.formatted_strings['weather'] = "{low} degrees F {conditions}".format(low=today['low']['fahrenheit'],
                conditions=today['conditions'])
        super(WeatherMixin, self).format()


class TodoMixin(UserForm):
    def __init__(self, *args, **kwargs):
        super(TodoMixin, self).__init__(*args, **kwargs)
        self.defaults['todo'] = "No todo"

    def prepare(self, partial=False):
        """

        :param partial:
        :return:
        """
        if "username" not in self.facts:
            return super(TodoMixin, self).prepare(True)
        if getattr(self, 'fail_todo', False):
            self.errors['todo'] = "Unable to retrieve"
        self.facts['todo'] = get_todos()
        super(TodoMixin, self).prepare(partial)

    def format(self):
        todos = self.facts.get('todo', [])
        self.formatted_strings['todo'] = "\n".join(x['title'] for x in todos if 'title' in x)
        super(TodoMixin, self).format()


class SimpleUserPlaceMixin(UserForm, PlaceForm):
    def getPlaceInfo(self):
        self.facts['zip_code'] = "07307"

    def getUserInfo(self):
        self.facts['username'] = "Andy"


class PersistFactsMixin(BaseForm):
    def __init__(self, *args, **kwargs):
        super(PersistFactsMixin, self).__init__(*args, **kwargs)
        self.shelf = shelve.open('oldfacts.db')
        self.shelf_key = repr((self.form_type, self.form_id))

    def __del__(self):
        self.shelf[self.shelf_key] = self.facts
        self.shelf.close()

    def analyze(self):
        if self.shelf_key not in self.shelf:
            return
        for errorKey in self.errors:
            if errorKey in self.shelf[self.shelf_key]:
                self.facts[errorKey] = self.shelf[self.shelf_key][errorKey]


class MakoForm(BaseForm):
    def __init__(self, form_type, form_id, form_date, filename):
        super(MakoForm, self, form_type, form_id, form_date).__init__()
        self.template = mako.template.Template(filename)

    def render_html(self):
        if not self.isFormatted:
            self()
        ret = self.template.render_context(self)
        self.state = RENDERED
        return ret


class TextForm(BaseForm):
    def __init__(self, form_type, form_id, form_date, template):
        super(TextForm, self).__init__(form_type, form_id, form_date)
        self.template = template

    def render_text(self):
        if not self.isFormatted:
            self()
        ret = self.template.format(**self)
        self.state = RENDERED
        return ret


class DailyForm(TextForm, WeatherMixin, TodoMixin, SimpleUserPlaceMixin):#, PersistFactsMixin):
    def __init__(self, form_id, form_date=None):
        template = """
    {form_type} for {form_id}
    ==========================
    {weather}
    {todo}
    """
        super(DailyForm, self).__init__(form_type=self.__class__.__name__,
            form_id=form_id,
            form_date=form_date,
            template=template)

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