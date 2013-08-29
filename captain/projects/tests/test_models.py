import shutil
import tempfile

from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile

from django_nose.tools import assert_raises, assert_equal
from guardian.shortcuts import assign_perm
from mock import patch

from captain.base.tests import TestCase
from captain.projects.models import CommandLog
from captain.projects.tests import CommandLogFactory, ProjectFactory
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
            log = project.send_command(user, 'asdf')
        shove.send_command.assert_called_once_with('qwer', 'blah', 'asdf', log.pk)

        assert_equal(log.project, project)
        assert_equal(log.user, user)
        assert_equal(log.command, 'asdf')


class CommandLogTests(TestCase):
    def setUp(self):
        self.temporary_media_directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temporary_media_directory)

    def test_read_logfile(self):
        """The log attribute should return the contents of the logfile."""
        log = CommandLogFactory.create()

        with self.settings(MEDIA_ROOT=self.temporary_media_directory):
            log.logfile.save(None, ContentFile('asdf'))

            log = CommandLog.objects.get(pk=log.pk)
            assert_equal(log.log, 'asdf')

    def test_write_logfile(self):
        log = CommandLogFactory.create()

        with self.settings(MEDIA_ROOT=self.temporary_media_directory):
            log.log = 'qwer'
            log.save()

            log = CommandLog.objects.get(pk=log.pk)
            with log.logfile as f:
                assert_equal(f.read(), 'qwer')
