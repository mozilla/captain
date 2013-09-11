import shutil
import tempfile
from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile

from django_nose.tools import assert_raises, assert_equal, assert_false, assert_true
from guardian.shortcuts import assign_perm
from mock import patch

from captain.base.tests import TestCase
from captain.projects.models import CommandLog
from captain.projects.tests import CommandLogFactory, ProjectFactory, ScheduledCommandFactory
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

    def test_send_command_no_user(self):
        """
        If None is passed in as the user, do not perform any permission checks and run the command.
        """
        project = ProjectFactory.create(queue='qwer', project_name='blah')

        with patch('captain.projects.models.shove') as shove:
            log = project.send_command(None, 'asdf')
        shove.send_command.assert_called_once_with('qwer', 'blah', 'asdf', log.pk)

        assert_equal(log.project, project)
        assert_equal(log.user, None)
        assert_equal(log.command, 'asdf')


class ScheduledCommandTests(TestCase):
    def test_is_due_no_run(self):
        """If the command has yet to be run, is_due should return True."""
        command = ScheduledCommandFactory(last_run=None)
        assert_true(command.is_due)

    def test_is_due_interval_not_passed(self):
        """
        If the interval hasn't passed between the current time and last run time, is_due should
        return False.
        """
        command = ScheduledCommandFactory(last_run=datetime(2013, 2, 1, 5, 0, 0),
                                          interval_minutes=15)
        with patch('captain.projects.models.timezone') as timezone:
            timezone.now.return_value = datetime(2013, 2, 1, 5, 14, 0)
            assert_false(command.is_due)

    def test_is_due_interval_passed(self):
        """
        If the interval has passed between the current time and last run time, is_due should
        return True.
        """
        command = ScheduledCommandFactory(last_run=datetime(2013, 2, 1, 5, 0, 0),
                                          interval_minutes=15)
        with patch('captain.projects.models.timezone') as timezone:
            timezone.now.return_value = datetime(2013, 2, 1, 5, 16, 0)
            assert_true(command.is_due)

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
