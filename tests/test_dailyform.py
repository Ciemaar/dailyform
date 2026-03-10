"""Tests for the dailyform forms."""

import os
import unittest
from datetime import date
from unittest.mock import patch

from dailyform.form import DailyForm, PersistFactsMixin, TodoMixin, WeatherMixin


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
        mock_get_weather.return_value = {date.today(): {"low": {"fahrenheit": 32}, "conditions": "Cloudy"}}
        mock_get_todos.return_value = [{"title": "Mock Todo"}]

        # Test case 1: Forced weather failure
        dt = DailyForm("Andy")
        dt.fail_weather = True
        dt.prepare()
        dt.prepare()  # Second prepare calls analyze/format implicitly or explicitly
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)
        self.assertEqual(dt.errors.get("weather"), "Unable to retrieve")

        # Test case 2: Valid zip code
        dt = DailyForm("Andy")
        dt.facts["zip_code"] = "10001"
        dt.prepare()
        dt.prepare()
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)
        self.assertIn("32 degrees F Cloudy", output)

        # Test case 3: Default behavior
        dt = DailyForm("Andy")
        dt.prepare()
        dt.prepare()
        output = dt.render_text()
        self.assertIn("DailyForm for Andy", output)

        # Test case 4: Forced todo failure
        dt = DailyForm("Andy")
        dt.facts["username"] = "Andy"  # Ensure username is set so it doesn't return early
        dt.fail_todo = True
        dt.prepare()
        self.assertEqual(dt.errors.get("todo"), "Unable to retrieve")

    def test_persist_facts_mixin(self):
        """Test the PersistFactsMixin analysis."""

        class TestPersistForm(PersistFactsMixin):
            def __init__(self):
                super().__init__("TestType", "TestID", "2023-01-01")

        # First form creates the DB
        form1 = TestPersistForm()
        form1.facts["fact_1"] = "val1"
        form1.facts["weather"] = "sunny"
        # Force save and close the shelf explicitly to avoid ValueError on garbage collection
        form1.__del__()

        # Second form reads from DB if there's an error
        form2 = TestPersistForm()
        form2.errors["weather"] = "failed"
        form2.analyze()

        self.assertEqual(form2.facts["weather"], "sunny")
        # Ensure we close properly
        form2.__del__()

    def test_persist_facts_mixin_no_key(self):
        """Test PersistFactsMixin when key is not in shelf."""

        class TestPersistForm(PersistFactsMixin):
            def __init__(self):
                super().__init__("NewType", "NewID", "2023-01-01")

        form = TestPersistForm()
        form.analyze()  # Should return early since key isn't in shelf
        form.__del__()

    def test_place_form_missing_zip(self):
        """Test WeatherMixin handles missing zip code gracefully."""

        # Using a mock form class that inherits WeatherMixin but does NOT set zip_code in facts
        class MockPlaceForm(WeatherMixin):
            def __init__(self):
                super().__init__("TestType", "TestID", "2023-01-01")

            def getPlaceInfo(self):
                pass

        form = MockPlaceForm()
        form.prepare()
        # Missing zip code leads to partial prep True returned by WeatherMixin,
        # so state should be PARTIAL_PREP
        from dailyform.base import FormState

        self.assertEqual(form.state, FormState.PARTIAL_PREP)

    def test_user_form_missing_user(self):
        """Test TodoMixin handles missing username gracefully."""

        class MockUserForm(TodoMixin):
            def __init__(self):
                super().__init__("TestType", "TestID", "2023-01-01")

            def getUserInfo(self):
                pass

        form = MockUserForm()
        form.prepare()
        # Missing username leads to partial prep
        from dailyform.base import FormState

        self.assertEqual(form.state, FormState.PARTIAL_PREP)


if __name__ == "__main__":
    unittest.main()
