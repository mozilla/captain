from django_nose.tools import assert_equal, assert_true
from mock import patch, PropertyMock

from captain.base.tests import TestCase
from captain.projects.management.commands import monitor_shove_logs
from captain.projects.models import CommandLog
from captain.projects.tests import CommandLogFactory


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
