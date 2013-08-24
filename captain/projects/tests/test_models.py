from django.core.exceptions import PermissionDenied

from django_nose.tools import assert_raises, assert_true
from guardian.shortcuts import assign_perm
from mock import patch

from captain.base.tests import TestCase
from captain.projects.models import CommandLog
from captain.projects.tests import ProjectFactory
from captain.users.tests import UserFactory


class ProjectTests(TestCase):
    def test_send_command_no_permission(self):
        """
        If the user doesn't have permission to run a command for this project, raise
        PermissionDenied.
        """
        user = UserFactory.create()
        project = ProjectFactory.create()

        with assert_raises(PermissionDenied):
            project.send_command(user, 'asdf')

    def test_send_command_has_permission(self):
        """
        If the user has permission to run a command for this project, send the command to shove and
        create a log entry for it.
        """
        user = UserFactory.create()
        project = ProjectFactory.create(queue='qwer', project_name='blah')
        assign_perm('can_run_commands', user, project)

        with patch('captain.projects.models.shove') as shove:
            project.send_command(user, 'asdf')
        shove.send_command.assert_called_once_with('qwer', 'blah', 'asdf')
        assert_true(CommandLog.objects.filter(project=project, user=user, command='asdf').exists())
