from django.utils import timezone

from django_nose.tools import assert_equal, assert_false, assert_true
from mock import Mock, patch, PropertyMock

from captain.base.tests import TestCase
from captain.projects.management.commands import monitor_shove_logs, process_command_schedule
from captain.projects.models import CommandLog
from captain.projects.tests import CommandLogFactory, ScheduledCommandFactory


class MonitorShoveLogsTests(TestCase):
    @patch('captain.projects.management.commands.monitor_shove_logs.log')
    def test_handle_log_key_invalid(self, log):
        """If the given log key isn't a valid pk, log a warning and return."""
        monitor_shove_logs.handle_log_event('not.an.int', 0, 'asdf')
        assert_true(log.warning.called)
        assert_equal(CommandLog.objects.count(), 0)

    @patch('captain.projects.management.commands.monitor_shove_logs.log')
    def test_handle_log_not_found(self, log):
        """If no log can be found with the given key, log a warning and return."""
        monitor_shove_logs.handle_log_event(99999999999, 0, 'asdf')
        assert_true(log.warning.called)
        assert_equal(CommandLog.objects.count(), 0)

    @patch.object(CommandLog, 'log', new_callable=PropertyMock)
    def test_handle_log_found(self, mock_log):
        """If a command log is found, save the given output to the log."""
        command_log = CommandLogFactory.create()
        monitor_shove_logs.handle_log_event(command_log.pk, 6, 'asdf')

        mock_log.assert_called_with('asdf')
        command_log = CommandLog.objects.get(pk=command_log.pk)  # Refresh from DB
        assert_equal(command_log.return_code, 6)


class ProcessCommandScheduleTests(TestCase):
    def setUp(self):
        super(ProcessCommandScheduleTests, self).setUp()
        self.timezone_patch = patch('captain.projects.management.commands.process_command_schedule'
                                    '.timezone')
        self.now = timezone.now()
        mock_timezone = self.timezone_patch.start()
        mock_timezone.now.return_value = self.now

    def tearDown(self):
        super(ProcessCommandScheduleTests, self).tearDown()
        self.timezone_patch.stop()

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
        command1 = self._mock_command(is_due=False, command='foo')
        command2 = self._mock_command(is_due=True, command='bar')
        command3 = self._mock_command(is_due=True, command='baz')

        path = 'captain.projects.management.commands.process_command_schedule.ScheduledCommand'
        with patch(path) as MockScheduledCommand:
            MockScheduledCommand.objects.all.return_value = [command1, command2, command3]
            cmd = process_command_schedule.Command()
            cmd.handle()

        # Commands that aren't due shoudn't have been run.
        assert_false(command1.project.send_command.called)

        # Commands that are due should have been run, and should have been saved with an updated
        # last_run.
        command2.project.send_command.assert_called_with(None, 'bar')
        assert_equal(command2.last_run, self.now)
        command2.save.assert_called_with()

        command3.project.send_command.assert_called_with(None, 'baz')
        assert_equal(command3.last_run, self.now)
        command3.save.assert_called_with()
