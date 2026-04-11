"""Common base classes and constants for forms."""

from collections.abc import Mapping
from enum import IntEnum

from mako.template import Template


class FormState(IntEnum):
    """Enumeration of possible form states."""

    NEW = 10
    PARTIAL_PREP = 20
    PREPARED = 30
    ANALYZED = 40
    FORMATTED = 50
    RENDERED = 60
    CORRUPT = 70


class BaseForm(Mapping):
    """Abstract base class that models a form as a dictionary-like state machine.

    A form progresses through stages: NEW -> PREPARED -> ANALYZED -> FORMATTED.
    It aggregates data across several internal dictionaries (defaults, facts,
    analysis, formatted_strings) allowing template engines to access all context
    transparently.
    """

    def __init__(self, form_type, form_id, form_date):
        """Initialize the core form state and internal storage dictionaries.

        Args:
            form_type (str): The class name or type identifier of the form.
            form_id (str): A unique identifier for the subject of the form (e.g., username).
            form_date (datetime.date): The date the form applies to.

        """
        self.form_type = form_type
        self.form_id = form_id
        self.form_date = form_date
        self.facts = dict(self.__dict__)  ## facts include form date, type, and id
        self.state = FormState.NEW
        self.analysis = {}
        self.formatted_strings = {}
        self.errors = {}
        self.failures = {}  # Exists in form2, harmless to add to base
        self.defaults = {}

    def prepare(self, partial=False):
        """Transition the form into a prepared state, gathering initial facts.

        Subclasses should override this to trigger API calls or data fetching.

        Args:
            partial (bool): If True, signifies that some data could not be
                prepared due to missing prerequisites, halting the pipeline.

        """
        if partial:
            self.state = FormState.PARTIAL_PREP
        else:
            self.state = FormState.PREPARED

    def analyze(self):
        """Process the facts gathered during the preparation stage.

        This step is used to compute derived values, check for errors, or apply
        business logic before formatting.
        """
        if not self.isPrepared:
            self.prepare()
        self.state = FormState.ANALYZED

    def format(self):
        """Convert raw facts and analysis into human-readable strings.

        Populates the `formatted_strings` dictionary for use by templates.
        """
        if not self.isAnalyzed:
            self.analyze()
        self.state = FormState.FORMATTED

    @property
    def isCorrupt(self):
        """Return True if form is corrupt."""
        return self.state >= FormState.CORRUPT

    @property
    def isPrepared(self):
        """Return True if form is prepared."""
        return self.state >= FormState.PREPARED and not self.isCorrupt

    @property
    def isAnalyzed(self):
        """Return True if form is analyzed."""
        return self.state >= FormState.ANALYZED and not self.isCorrupt

    @property
    def isFormatted(self):
        """Return True if form is formatted."""
        return self.state >= FormState.FORMATTED and not self.isCorrupt

    def __getitem__(self, key):
        """BaseForm can be used as a dictionary, in which case it will search all internal dicts."""
        return self.formatted_strings.get(
            key, self.analysis.get(key, self.facts.get(key, self.defaults.get(key, None)))
        )

    def __iter__(self):
        """Iterate over the keys of the form dictionary."""
        for key in (
            set(self.formatted_strings.keys())
            | set(self.analysis.keys())
            | set(self.facts.keys())
            | set(self.defaults.keys())
        ):
            yield key

    def __len__(self):
        """Return the total number of unique keys in the form."""
        return len(
            set(self.formatted_strings.keys())
            | set(self.analysis.keys())
            | set(self.facts.keys())
            | set(self.defaults.keys())
        )

    def __call__(self):
        """Execute the full form lifecycle pipeline sequentially.

        Ensures the form passes through preparation, analysis, and formatting
        if those steps have not already been completed.
        """
        if not self.isPrepared:
            self.prepare()
        if not self.isAnalyzed:
            self.analyze()
        if not self.isFormatted:
            self.format()


class MakoForm(BaseForm):
    """A form subclass that uses Mako templates for HTML generation."""

    def __init__(self, form_type, form_id, form_date, filename):
        """Initialize the form and compile the Mako template from a file.

        Args:
            form_type (str): The class name or type identifier of the form.
            form_id (str): A unique identifier for the subject of the form.
            form_date (datetime.date): The date the form applies to.
            filename (str): The path to the Mako template file.

        """
        super(MakoForm, self).__init__(form_type, form_id, form_date)
        self.template = Template(filename=filename)

    def render_html(self):
        """Render the form as HTML."""
        if not self.isFormatted:
            self.format()
        # Mako's render_context expects a mako.runtime.Context.
        # However, if we just want to render text using the template and kwargs:
        ret = self.template.render(**{k: self[k] for k in self})
        self.state = FormState.RENDERED
        return ret


class TextForm(BaseForm):
    """A form subclass that renders output via standard Python string formatting."""

    def __init__(self, form_type, form_id, form_date, template):
        """Initialize the form with an inline formatting template.

        Args:
            form_type (str): The class name or type identifier of the form.
            form_id (str): A unique identifier for the subject of the form.
            form_date (datetime.date): The date the form applies to.
            template (str): The string format template.

        """
        super(TextForm, self).__init__(form_type, form_id, form_date)
        self.template = template

    def render_text(self):
        """Render the form as plain text."""
        if not self.isFormatted:
            self.format()
        ret = self.template.format(**self)
        self.state = FormState.RENDERED
        return ret
