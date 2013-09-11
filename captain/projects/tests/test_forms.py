from django_nose.tools import assert_false, assert_true

from captain.base.tests import TestCase
from captain.projects.forms import RunCommandForm


class RunCommandFormTests(TestCase):
    def test_whitespace_command(self):
        """If a command consists only of whitespace, the form should be invalid."""
        form = RunCommandForm({'command': '     '})
        assert_false(form.is_valid())

        form = RunCommandForm({'command': '\t\t'})
        assert_false(form.is_valid())

        form = RunCommandForm({'command': '\n\n\n\n'})
        assert_false(form.is_valid())

    def test_non_whitespace_command(self):
        """If a command has non-whitespace characters, the form should be valid."""
        form = RunCommandForm({'command': '   whitespace but not blank   '})
        assert_true(form.is_valid())
