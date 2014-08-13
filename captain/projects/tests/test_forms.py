from django_nose.tools import assert_equal, assert_false, assert_true

from captain.base.tests import TestCase
from captain.projects.forms import CreateScheduledCommandForm, RunCommandForm
from captain.projects.tests import ProjectFactory, ShoveInstanceFactory


class RunCommandFormTests(TestCase):
    def test_whitespace_command(self):
        """If a command consists only of whitespace, the form should be invalid."""
        project = ProjectFactory.create()
        shove_instance = ShoveInstanceFactory.create()
        project.shove_instances.add(shove_instance)

        form = RunCommandForm({'command': '     ', 'shove_instances': [shove_instance.pk]},
                              project=project)
        assert_false(form.is_valid())

        form = RunCommandForm({'command': '\t\t', 'shove_instances': [shove_instance.pk]},
                              project=project)
        assert_false(form.is_valid())

        form = RunCommandForm({'command': '\n\n\n\n', 'shove_instances': [shove_instance.pk]},
                              project=project)
        assert_false(form.is_valid())

    def test_non_whitespace_command(self):
        """If a command has non-whitespace characters, the form should be valid."""
        project = ProjectFactory.create()
        shove_instance = ShoveInstanceFactory.create()
        project.shove_instances.add(shove_instance)

        form_data = {
            'command': '   whitespace but not blank   ',
            'shove_instances': [shove_instance.pk]
        }
        form = RunCommandForm(form_data, project=project)
        assert_true(form.is_valid())


class CreateScheduledCommandFormTests(TestCase):
    def test_clean_hostnames(self):
        """
        The cleaned hostname value should be a comma-separated list of
        hostnames of the selected ShoveInstances.
        """
        project = ProjectFactory.create()
        instance1 = ShoveInstanceFactory.create(hostname='foo.bar')
        instance2 = ShoveInstanceFactory.create(hostname='baz.biff')
        project.shove_instances.add(instance1)
        project.shove_instances.add(instance2)

        form = CreateScheduledCommandForm({
            'command': 'test',
            'hostnames': [instance1.pk, instance2.pk],
        }, project=project)
        form.is_valid()
        hostnames = form.cleaned_data['hostnames'].split(',')
        assert_equal(set(hostnames), set(['foo.bar', 'baz.biff']))
