"""Tests for the dummy form implementation."""

import unittest
from datetime import date

from dailyform.form2 import DailyForm


class TestDailyFormDummy(unittest.TestCase):
    """Test suite for the dummy DailyForm class."""

    def test_dummy_form_render(self):
        """Test rendering the dummy form."""
        form = DailyForm("TestID")
        self.assertEqual(form.form_id, "TestID")
        self.assertEqual(form.form_type, "DailyForm")

        # Test default form_date
        self.assertEqual(form.form_date, date.today())

        form.prepare()
        result = form.render_text()

        self.assertIn("DailyForm for TestID", result)
        self.assertIn("Today's Weather:  Partly Sunny", result)
        self.assertIn("Your Todo's:  ['teach class', 'prepare class']", result)

    def test_dummy_form_weather_fail(self):
        """Test weather failure condition."""
        form = DailyForm("TestID")
        form.fail_weather = True
        form.prepare()
        self.assertEqual(form.failures["weather"], "Forced Failure on weather")
        self.assertTrue(form.isPrepared)

    def test_dummy_form_todo_fail(self):
        """Test todo failure condition."""
        form = DailyForm("TestID")
        form.fail_todo = True
        form.prepare()
        self.assertEqual(form.failures["todos"], "Forced Failure on todos")
        self.assertTrue(form.isPrepared)
