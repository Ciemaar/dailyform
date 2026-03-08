"""Tests for the dailyform forms."""

import os
import unittest
from datetime import date
from unittest.mock import patch

from dailyform.form import DailyForm


class TestDailyForm(unittest.TestCase):
    """Test suite for the DailyForm class."""

    def setUp(self):
        """Set up the test environment."""
        if os.path.exists("oldfacts.db"):
            os.remove("oldfacts.db")

    def tearDown(self):
        """Clean up the test environment."""
        if os.path.exists("oldfacts.db"):
            try:
                os.remove("oldfacts.db")
            except OSError:
                pass

    @patch("dailyform.form.get_weather_forecast")
    @patch("dailyform.form.get_todos")
    def test_daily_form_output(self, mock_get_todos, mock_get_weather):
        """Test the output of the DailyForm under various conditions."""
        mock_get_weather.return_value = {
            date.today(): {
                "low": {"fahrenheit": 32},
                "conditions": "Cloudy"
            }
        }
        mock_get_todos.return_value = [{"title": "Mock Todo"}]

        # Test case 1: Forced weather failure
        dt = DailyForm("Andy")
        dt.fail_weather = True
        dt.prepare()
        dt.prepare()  # Second prepare calls analyze/format implicitly or explicitly
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)

        # Test case 2: Valid zip code
        dt = DailyForm("Andy")
        dt.facts["zip_code"] = "10001"
        dt.prepare()
        dt.prepare()
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)

        # Test case 3: Default behavior
        dt = DailyForm("Andy")
        dt.prepare()
        dt.prepare()
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)


if __name__ == "__main__":
    unittest.main()
