"""Tests for the weather module."""

import json
import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from dailyform import weather


class TestWeather(unittest.TestCase):
    """Test suite for the weather module."""

    @patch("dailyform.weather.config")
    @patch("dailyform.weather.urllib.request.urlopen")
    def test_get_weather_forecast(self, mock_urlopen, mock_config):
        """Test successfully fetching and parsing weather forecasts."""
        mock_config.owm_api_key = "TEST_API_KEY"

        mock_response = MagicMock()
        mock_json = {
            "list": [
                {
                    "dt_txt": "2023-01-01 12:00:00",
                    "main": {"temp_min": 32.5},
                    "weather": [{"main": "Clouds"}],
                },
                {
                    "dt_txt": "2023-01-01 15:00:00",
                    "main": {"temp_min": 28.0},  # Lower temp on same day
                    "weather": [{"main": "Snow"}],
                },
                {
                    "dt_txt": "2023-01-02 12:00:00",
                    "main": {"temp_min": 45.0},
                    "weather": [{"main": "Clear"}],
                },
            ]
        }
        mock_response.read.return_value = json.dumps(mock_json).encode("utf-8")

        # Make the context manager work
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        forecasts = weather.get_weather_forecast("10001")

        self.assertEqual(len(forecasts), 2)

        day1 = date(2023, 1, 1)
        day2 = date(2023, 1, 2)

        self.assertIn(day1, forecasts)
        self.assertIn(day2, forecasts)

        # It should record the lowest temp (28.0) but might keep the first condition encountered (Clouds)
        self.assertEqual(forecasts[day1]["low"]["fahrenheit"], 28.0)
        self.assertEqual(forecasts[day1]["conditions"], "Clouds")

        self.assertEqual(forecasts[day2]["low"]["fahrenheit"], 45.0)
        self.assertEqual(forecasts[day2]["conditions"], "Clear")

    @patch("dailyform.weather.config")
    def test_get_weather_forecast_no_key(self, mock_config):
        """Test fetching weather without an API key."""
        mock_config.owm_api_key = None
        forecasts = weather.get_weather_forecast("10001")
        self.assertEqual(forecasts, {})

    @patch("dailyform.weather.config")
    @patch("dailyform.weather.urllib.request.urlopen")
    def test_get_weather_forecast_exception(self, mock_urlopen, mock_config):
        """Test fetching weather when an exception occurs."""
        mock_config.owm_api_key = "TEST_API_KEY"
        mock_urlopen.side_effect = Exception("API Error")

        forecasts = weather.get_weather_forecast("10001")
        self.assertEqual(forecasts, {})


if __name__ == "__main__":
    unittest.main()
