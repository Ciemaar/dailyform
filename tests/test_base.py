"""Tests for the base classes."""

import unittest

from dailyform.base import BaseForm, MakoForm, TextForm


class TestBaseForm(unittest.TestCase):
    """Test suite for the BaseForm class."""

    def test_base_form_properties(self):
        """Test the state properties of BaseForm."""
        form = BaseForm("TestType", "TestID", "2023-01-01")

        # New state
        self.assertFalse(form.isPrepared)
        self.assertFalse(form.isAnalyzed)
        self.assertFalse(form.isFormatted)
        self.assertFalse(form.isCorrupt)

        # Prepare
        form.prepare(partial=True)
        self.assertFalse(form.isPrepared)  # Partial is not fully prepared
        form.prepare(partial=False)
        self.assertTrue(form.isPrepared)

        # Analyze
        form.analyze()
        self.assertTrue(form.isAnalyzed)

        # Format
        form.format()
        self.assertTrue(form.isFormatted)

    def test_base_form_dict_methods(self):
        """Test the dictionary-like methods of BaseForm."""
        form = BaseForm("TestType", "TestID", "2023-01-01")

        form.defaults["default_key"] = "default_val"
        form.facts["fact_key"] = "fact_val"
        form.analysis["analysis_key"] = "analysis_val"
        form.formatted_strings["formatted_key"] = "formatted_val"

        # Test __getitem__
        self.assertEqual(form["default_key"], "default_val")
        self.assertEqual(form["fact_key"], "fact_val")
        self.assertEqual(form["analysis_key"], "analysis_val")
        self.assertEqual(form["formatted_key"], "formatted_val")
        self.assertIsNone(form["missing_key"])

        # Test __iter__ and __len__
        keys = set(form)
        self.assertIn("default_key", keys)
        self.assertIn("fact_key", keys)
        self.assertIn("analysis_key", keys)
        self.assertIn("formatted_key", keys)
        self.assertEqual(len(form), len(keys))

    def test_base_form_call(self):
        """Test the __call__ method of BaseForm."""
        form = BaseForm("TestType", "TestID", "2023-01-01")
        form()
        self.assertTrue(form.isPrepared)
        self.assertTrue(form.isAnalyzed)
        self.assertTrue(form.isFormatted)


class TestTextForm(unittest.TestCase):
    """Test suite for the TextForm class."""

    def test_text_form_render(self):
        """Test rendering of TextForm."""
        form = TextForm("TestType", "TestID", "2023-01-01", "Type: {form_type}")
        result = form.render_text()
        self.assertEqual(result, "Type: TestType")
        self.assertTrue(form.isFormatted)


class TestMakoForm(unittest.TestCase):
    """Test suite for the MakoForm class."""

    def test_mako_form_render(self):
        """Test rendering of MakoForm."""
        import os
        import tempfile

        # Create a temporary mako template
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Type: ${form_type}")
            temp_name = f.name

        try:
            # mako Template takes a string as the first arg 'text', and `filename` as kwarg.
            # If we pass temp_name as a positional argument, it thinks it's template text.
            form = MakoForm("TestType", "TestID", "2023-01-01", filename=temp_name)

            result = form.render_html()
            self.assertEqual(result.strip(), "Type: TestType")
            self.assertTrue(form.isFormatted)
        finally:
            os.remove(temp_name)

    def test_base_form_corrupt(self):
        """Test the corrupt state property."""
        form = BaseForm("Test", "1", "2023-01-01")
        from dailyform.base import FormState

        form.state = FormState.CORRUPT
        self.assertTrue(form.isCorrupt)
        self.assertFalse(form.isPrepared)
        self.assertFalse(form.isAnalyzed)
        self.assertFalse(form.isFormatted)


if __name__ == "__main__":
    unittest.main()
