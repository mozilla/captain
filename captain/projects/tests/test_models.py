import shutil
import tempfile

from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile

from django_nose.tools import assert_raises, assert_equal, assert_false, assert_true
from guardian.shortcuts import assign_perm
from mock import call, Mock, patch

from captain.base.tests import aware_datetime, CONTAINS, TestCase
from captain.projects.models import CommandLog, ShoveInstance
from captain.projects.tests import (CommandLogFactory, ProjectFactory, SentCommandFactory,
                                    ShoveInstanceFactory, ScheduledCommandFactory)
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
            project.send_command(user, 'asdf', [])

    def test_send_command_inactive_shoves(self):
        """
        If any of the shove instances given are not in the set of active
        shove instances for this project, raise a ValueError.
        """
        user = UserFactory.create()
        project = ProjectFactory.create()
        assign_perm('can_run_commands', user, project)

        instance1, instance2 = ShoveInstanceFactory.create_batch(2, active=True)
        project.shove_instances.add(instance1)
        with assert_raises(ValueError):
            project.send_command(user, 'asdf', [instance1, instance2])

        # Now try with an inactive instance that is part of the
        # project's instances.
        instance2.active = False
        instance2.save()
        project.shove_instances.add(instance2)
        with assert_raises(ValueError):
            project.send_command(user, 'asdf', [instance1, instance2])

    def test_send_command_has_permission(self):
        """
        If the user has permission to run a command for this project,
        send the command to shove and create a sent command for it.
        """
        user = UserFactory.create()
        project = ProjectFactory.create(project_name='blah')
        assign_perm('can_run_commands', user, project)

        instance1, instance2 = ShoveInstanceFactory.create_batch(2, active=True)
        project.shove_instances.add(instance1, instance2)

        with patch.object(ShoveInstance, 'send_command', autospec=True) as send_command:
            sent_command = project.send_command(user, 'asdf', [instance1, instance2])
            send_command.assert_has_calls([call(instance1, project, sent_command),
                                           call(instance2, project, sent_command)],
                                          any_order=True)

        assert_equal(sent_command.project, project)
        assert_equal(sent_command.user, user)
        assert_equal(sent_command.command, 'asdf')

    def test_send_command_no_user(self):
        """
        If None is passed in as the user, do not perform any permission checks and run the command.
        """
        project = ProjectFactory.create(project_name='blah')

        instance = ShoveInstanceFactory.create(active=True)
        project.shove_instances.add(instance)

        with patch.object(ShoveInstance, 'send_command', autospec=True) as send_command:
            sent_command = project.send_command(None, 'asdf', [instance])
            send_command.assert_called_with(instance, project, sent_command)

        assert_equal(sent_command.project, project)
        assert_equal(sent_command.user, None)
        assert_equal(sent_command.command, 'asdf')


class ShoveInstanceTests(TestCase):
    def test_send_command(self):
        project = ProjectFactory.create(project_name='myproject')
        instance = ShoveInstanceFactory.create(active=True, routing_key='route')
        project.shove_instances.add(instance)
        sent_command = SentCommandFactory.create(command='asdf')

        with patch('captain.projects.models.shove') as shove:
            log = instance.send_command(project, sent_command)
            shove.send_command.assert_called_with('route', 'myproject', 'asdf', log.pk)
            assert_equal(log.shove_instance, instance)
            assert_equal(log.sent_command, sent_command)


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
        command = ScheduledCommandFactory(last_run=aware_datetime(2013, 2, 1, 5, 0, 0),
                                          interval_minutes=15)
        with patch('captain.projects.models.timezone') as timezone:
            timezone.now.return_value = aware_datetime(2013, 2, 1, 5, 14, 0)
            assert_false(command.is_due)

    def test_is_due_interval_passed(self):
        """
        If the interval has passed between the current time and last run time, is_due should
        return True.
        """
        command = ScheduledCommandFactory(last_run=aware_datetime(2013, 2, 1, 5, 0, 0),
                                          interval_minutes=15)
        with patch('captain.projects.models.timezone') as timezone:
            timezone.now.return_value = aware_datetime(2013, 2, 1, 5, 16, 0)
            assert_true(command.is_due)

    def test_shove_instances(self):
        instance1 = ShoveInstanceFactory.create(hostname='foo', active=True)
        instance2 = ShoveInstanceFactory.create(hostname='bar', active=True)
        ShoveInstanceFactory.create(hostname='baz', active=False)

        command = ScheduledCommandFactory(hostnames='foo,bar,baz')
        assert_equal(set(command.shove_instances), set([instance1, instance2]))

    def test_run(self):
        instance1 = ShoveInstanceFactory.create(hostname='foo', active=True)
        instance2 = ShoveInstanceFactory.create(hostname='bar', active=True)
        command = ScheduledCommandFactory(command='asdf', hostnames='foo,bar')
        command.project.send_command = Mock()

        with patch('captain.projects.models.timezone') as mock_timezone:
            now =  aware_datetime(2014, 1, 1, 1, 1, 1)
            mock_timezone.now.return_value = now
            command.run()

        assert_equal(command.last_run, now)
        command.project.send_command.assert_called_with(None, 'asdf',
                                                        CONTAINS(instance1, instance2))


class SentCommandTests(TestCase):
    def test_success_true(self):
        """
        If all shove instances executed the command successfully,
        return True.
        """
        command = SentCommandFactory.create()
        CommandLogFactory.create_batch(2, sent_command=command, return_code=0)
        assert_true(command.success)

    def test_success_none(self):
        """
        If any shove instance hasn't received a return code yet, return
        None.
        """
        command = SentCommandFactory.create()
        CommandLogFactory.create(sent_command=command, return_code=0)
        CommandLogFactory.create(sent_command=command, return_code=None)
        assert_true(command.success is None)

    def test_success_false(self):
        """
        If any shove instance has a nonzero return code return False.
        """
        command = SentCommandFactory.create()
        CommandLogFactory.create(sent_command=command, return_code=0)
        CommandLogFactory.create(sent_command=command, return_code=1)
        assert_false(command.success)


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
