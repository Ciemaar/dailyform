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
    """Base class for all forms."""

    def __init__(self, form_type, form_id, form_date):
        """Initialize the base form properties."""
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
        """Prepare the form.

        :param partial: Whether this is a partial preparation.
        """
        if partial:
            self.state = FormState.PARTIAL_PREP
        else:
            self.state = FormState.PREPARED

    def analyze(self):
        """Analyze the prepared form."""
        if not self.isPrepared:
            self.prepare()
        self.state = FormState.ANALYZED

    def format(self):
        """Format the form output."""
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
        """Prepare, analyze, and format the form."""
        if not self.isPrepared:
            self.prepare()
        if not self.isAnalyzed:
            self.analyze()
        if not self.isFormatted:
            self.format()


class MakoForm(BaseForm):
    """Form that renders using Mako templates."""

    def __init__(self, form_type, form_id, form_date, filename):
        """Initialize the MakoForm with a template file."""
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
    """Form that renders using standard string formatting."""

    def __init__(self, form_type, form_id, form_date, template):
        """Initialize the TextForm with a template string."""
        super(TextForm, self).__init__(form_type, form_id, form_date)
        self.template = template

    def render_text(self):
        """Render the form as plain text."""
        if not self.isFormatted:
            self.format()
        ret = self.template.format(**self)
        self.state = FormState.RENDERED
        return ret
