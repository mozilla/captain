from django_nose.tools import assert_equal, assert_true
from mock import patch

from captain.base.tests import TestCase
from captain.projects.management.commands import monitor_shove_logs
from captain.projects.models import CommandLog


class MonitorShoveLogsTests(TestCase):
    @patch('captain.projects.management.commands.monitor_shove_logs.log')
    def test_handle_log_key_invalid(self, log):
        """If the given log key isn't a valid pk, log a warning and return."""
        monitor_shove_logs.handle_log_event('not.an.int', 'asdf')
        assert_true(log.warning.called)
        assert_equal(CommandLog.objects.count(), 0)

    @patch('captain.projects.management.commands.monitor_shove_logs.log')
    def test_handle_log_not_found(self, log):
        """If no log can be found with the given key, log a warning and return."""
        monitor_shove_logs.handle_log_event(99999999999, 'asdf')
        assert_true(log.warning.called)
        assert_equal(CommandLog.objects.count(), 0)

    @patch('captain.projects.management.commands.monitor_shove_logs.CommandLog')
    def test_handle_log_found(self, MockCommandLog):
        """If a command log is found, save the given output to the log."""
        mock_log = MockCommandLog.objects.get.return_value
        monitor_shove_logs.handle_log_event(47, 'asdf')

        MockCommandLog.objects.get.assert_called_with(pk=47)
        mock_log.write_log.assert_called_with('asdf')
