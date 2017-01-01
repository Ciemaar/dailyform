import json
import urllib2
from datetime import date

from secrets import WU_API_KEY

zip_code = '10001'

f = urllib2.urlopen(
    'http://api.wunderground.com/api/{API_KEY}/geolookup/forecast10day/q/{zip_code}.json'.format(
        zip_code=zip_code, API_KEY=WU_API_KEY))

json_string = f.read()

parsed_json = json.loads(json_string)

for forecast in parsed_json['forecast']['simpleforecast']['forecastday']:
    print date(day=forecast['date']['day'], month=forecast['date']['month'],
               year=forecast['date']['year']), "{low} degrees F {conditions}".format(low=forecast['low']['fahrenheit'],
                                                                                     conditions=forecast[
                                                                                         'conditions']), forecast
f.close()
