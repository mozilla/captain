from django_nose.tools import assert_equal, assert_false, assert_true
from mock import Mock, patch, PropertyMock

from captain.base.tests import aware_datetime, TestCase
from captain.projects.management.commands import (monitor_shove_instances, monitor_shove_logs,
                                                  process_command_schedule)
from captain.projects.models import CommandLog, ShoveInstance
from captain.projects.tests import (CommandLogFactory, ProjectFactory, ScheduledCommandFactory,
                                    ShoveInstanceFactory)


class MonitorShoveLogsTests(TestCase):
    @patch('captain.projects.management.commands.monitor_shove_logs.log')
    def test_handle_log_key_invalid(self, log):
        """If the given log key isn't a valid pk, log a warning and return."""
        monitor_shove_logs.handle_log_event({
            'log_key': 'not.an.int',
            'return_code': 0,
            'output': 'asdf'
        })
        assert_true(log.warning.called)
        assert_equal(CommandLog.objects.count(), 0)

    @patch('captain.projects.management.commands.monitor_shove_logs.log')
    def test_handle_log_not_found(self, log):
        """If no log can be found with the given key, log a warning and return."""
        monitor_shove_logs.handle_log_event({
            'log_key': 99999999999,
            'return_code': 0,
            'output': 'asdf'
        })
        assert_true(log.warning.called)
        assert_equal(CommandLog.objects.count(), 0)

    @patch.object(CommandLog, 'log', new_callable=PropertyMock)
    def test_handle_log_found(self, mock_log):
        """If a command log is found, save the given output to the log."""
        command_log = CommandLogFactory.create()
        monitor_shove_logs.handle_log_event({
            'log_key': command_log.pk,
            'return_code': 6,
            'output': 'asdf'
        })

        mock_log.assert_called_with('asdf')
        command_log = CommandLog.objects.get(pk=command_log.pk)  # Refresh from DB
        assert_equal(command_log.return_code, 6)

    def test_handle_log_event_missing_key(self):
        """If the log event is missing a required key, log and return."""
        with patch('captain.projects.management.commands.monitor_shove_logs.log') as log:
            monitor_shove_logs.handle_log_event({
                'return_code': 6,
                'output': 'asdf'
            })

            assert_true(log.warning.called)
            assert_equal(CommandLog.objects.count(), 0)



class ProcessCommandScheduleTests(TestCase):
    def _mock_command(self, *args, **kwargs):
        """
        Create a mock command that wraps a real ScheduledCommand (to trigger AttributeErrors on
        invalid attributes) and which mocks out send_command.
        """
        mock_command = Mock(*args, wraps=ScheduledCommandFactory.create(), **kwargs)
        mock_command.project.send_command = Mock()
        return mock_command

    def test_basic_run(self):
        """
        When the command is run, any scheduled commands that are due to run should be sent to
        shove.
        """
        command1 = Mock(is_due=False)
        command2 = Mock(is_due=True)
        command3 = Mock(is_due=True)

        path = 'captain.projects.management.commands.process_command_schedule.ScheduledCommand'
        with patch(path) as MockScheduledCommand:
            MockScheduledCommand.objects.all.return_value = [command1, command2, command3]
            cmd = process_command_schedule.Command()
            cmd.handle()

        # Commands that aren't due shoudn't have been run.
        assert_false(command1.run.called)

        # Commands that are due should have been run.
        assert_true(command2.run.called)
        assert_true(command3.run.called)


class MonitorShoveInstancesTests(TestCase):
    def test_inactive_thread_mark_inactive_shoves(self):
        """
        mark_inactive_shoves should find any ShoveInstances with a
        last_heartbeat older than the HEARTBEAT_INACTIVE_DELAY setting
        and mark them as inactive.
        """
        up_to_date_instance = ShoveInstanceFactory.create(
            last_heartbeat=aware_datetime(2014, 1, 1, 10, 0, 0), active=True)
        out_of_date_instance = ShoveInstanceFactory.create(
            last_heartbeat=aware_datetime(2014, 1, 1, 9, 30, 0), active=True)

        thread = monitor_shove_instances.MarkInactiveShoveInstancesThread()
        with self.settings(HEARTBEAT_INACTIVE_DELAY=10*60):
            with patch.object(monitor_shove_instances, 'timezone') as mock_timezone:
                mock_timezone.now.return_value = aware_datetime(2014, 1, 1, 10, 5, 0)
                thread.mark_inactive_shoves()

        assert_equal(ShoveInstance.objects.get(pk=up_to_date_instance.pk).active, True)
        assert_equal(ShoveInstance.objects.get(pk=out_of_date_instance.pk).active, False)

    def test_handle_heartbeat_missing_key(self):
        """
        If the given data is missing a required key, log a warning and
        return.
        """
        with patch.object(monitor_shove_instances, 'log') as log:
            monitor_shove_instances.handle_heartbeat_event({'incorrect': 'keys'})
            assert_true(log.warning.called)
            assert_equal(ShoveInstance.objects.count(), 0)

    def test_handle_heartbeat_project_names_not_string(self):
        """
        If the project name isn't a string, log a warning and return.
        """
        with patch.object(monitor_shove_instances, 'log') as log:
            monitor_shove_instances.handle_heartbeat_event({
                'routing_key': 'asdf',
                'hostname': 'paranoia.local',
                'project_names': ['foo', 'bar']
            })
            assert_true(log.warning.called)
            assert_equal(ShoveInstance.objects.count(), 0)

    def test_handle_heartbeat_blank_keys(self):
        """
        If the routing key or hostname are blank, log a warning and
        return.
        """
        with patch.object(monitor_shove_instances, 'log') as log:
            monitor_shove_instances.handle_heartbeat_event({
                'routing_key': '',
                'hostname': 'paranoia.local',
                'project_names': 'foo,bar',
            })
            assert_true(log.warning.called)
            assert_equal(ShoveInstance.objects.count(), 0)

            log.warning.reset_mock()
            monitor_shove_instances.handle_heartbeat_event({
                'routing_key': 'asdf',
                'hostname': '',
                'project_names': 'foo,bar',
            })
            assert_true(log.warning.called)
            assert_equal(ShoveInstance.objects.count(), 0)

    def test_handle_hearbeat_new_shove_instance(self):
        """
        If there is no existing shove instance for the given routing
        key, create a new one.
        """
        assert_equal(ShoveInstance.objects.count(), 0)
        monitor_shove_instances.handle_heartbeat_event({
            'routing_key': 'asdf',
            'hostname': 'paranoia.local',
            'project_names': '',
        })

        instance = ShoveInstance.objects.get(routing_key='asdf')
        assert_equal(instance.hostname, 'paranoia.local')
        assert_equal(instance.projects.count(), 0)

    def test_handle_heartbeat_existing_shove_instance(self):
        """
        If a shove instance for the given routing key already exists,
        update it with the latest hostname and projects.
        """
        instance = ShoveInstanceFactory.create(routing_key='asdf', hostname='old.local')
        project1 = ProjectFactory.create(project_name='foo')

        monitor_shove_instances.handle_heartbeat_event({
            'routing_key': 'asdf',
            'hostname': 'paranoia.local',
            'project_names': 'foo',
        })
        instance = ShoveInstance.objects.get(pk=instance.pk)
        assert_equal(instance.hostname, 'paranoia.local')
        assert_equal(list(instance.projects.all()), [project1])

    def test_handle_heartbeat_add_new_projects(self):
        """
        Add any projects specified by the project_names value to the
        list of projects supported by the ShoveInstance.
        """
        project1 = ProjectFactory.create(project_name='foo')
        project2 = ProjectFactory.create(project_name='bar')

        with patch.object(monitor_shove_instances, 'log') as log:
            monitor_shove_instances.handle_heartbeat_event({
                'routing_key': 'asdf',
                'hostname': 'paranoia.local',
                'project_names': 'foo,bar,baz',
            })
            # Warn about missing project but do not abort.
            assert_true(log.warning.called)

        instance = ShoveInstance.objects.get(routing_key='asdf')
        assert_equal(set(instance.projects.all()), set([project1, project2]))

    def test_handle_heartbeat_remove_projects(self):
        """Remove any old projects not in the project_names list."""
        instance = ShoveInstanceFactory.create(routing_key='asdf')
        project1 = ProjectFactory.create(project_name='foo')
        project2 = ProjectFactory.create(project_name='bar')
        instance.projects.add(project1)

        monitor_shove_instances.handle_heartbeat_event({
            'routing_key': 'asdf',
            'hostname': 'paranoia.local',
            'project_names': 'bar,baz',
        })

        instance = ShoveInstance.objects.get(routing_key='asdf')
        assert_equal(list(instance.projects.all()), [project2])
