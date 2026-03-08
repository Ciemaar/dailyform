"""Client integration with OpenWeatherMap API."""

import json
import urllib.request
from datetime import date

from .config import config


def get_weather_forecast(zip_code):
    """Fetch the 5-day / 3-hour forecast from OpenWeatherMap for a given US zip code.

    Groups the forecast by day and returns the minimum temperature and general conditions.
    """
    api_key = config.owm_api_key
    if not api_key:
        print("Error: OpenWeatherMap API key not configured")
        return {}

    url = f"http://api.openweathermap.org/data/2.5/forecast?zip={zip_code},us&units=imperial&appid={api_key}"

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            json_string = response.read()
            parsed_json = json.loads(json_string)

            daily_forecasts = {}
            for item in parsed_json.get('list', []):
                # OWM returns data in 3-hour chunks.
                # dt_txt format: "YYYY-MM-DD HH:MM:SS"
                date_str = item['dt_txt'].split(' ')[0]
                y, m, d = map(int, date_str.split('-'))
                forecast_date = date(year=y, month=m, day=d)

                temp = item['main']['temp_min']
                condition = item['weather'][0]['main']

                if forecast_date not in daily_forecasts:
                    daily_forecasts[forecast_date] = {
                        "low": {"fahrenheit": temp},
                        "conditions": condition
                    }
                else:
                    # Update to find the true daily low
                    if temp < daily_forecasts[forecast_date]["low"]["fahrenheit"]:
                        daily_forecasts[forecast_date]["low"]["fahrenheit"] = temp

            return daily_forecasts
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return {}


if __name__ == "__main__":
    zip_code = '10001'
    forecasts = get_weather_forecast(zip_code)
    for forecast_date, forecast in sorted(forecasts.items()):
        print(forecast_date, "{low} degrees F {conditions}".format(low=forecast['low']['fahrenheit'],
                                                                   conditions=forecast['conditions']), forecast)
