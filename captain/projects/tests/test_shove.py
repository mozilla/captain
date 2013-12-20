import json

from django.test.utils import override_settings

from django_nose.tools import assert_equal, assert_raises, assert_true
from mock import ANY, Mock, patch

from captain.base.tests import TestCase
from captain.projects import shove


class MockConnectTestCase(TestCase):
    """TestCase that mocks the create_connection function in captain.projects.shove."""
    def setUp(self):
        super(MockConnectTestCase, self).setUp()
        self.create_connection_patch = patch('captain.projects.shove.create_connection')

        create_connection = self.create_connection_patch.start()
        self.connection = Mock()
        self.channel = self.connection.channel.return_value
        create_connection.return_value = self.connection

    def tearDown(self):
        super(MockConnectTestCase, self).tearDown()
        self.create_connection_patch.stop()


@override_settings(LOGGING_QUEUE='test_log_queue')
class SendCommandTests(MockConnectTestCase):
    def test_basic_publish(self):
        shove.send_command('my_queue', 'my_project', 'asdf', 75)

        self.channel.queue_declare.assert_called_once_with(queue='my_queue', durable=True)
        self.channel.basic_publish.assert_called_once_with(exchange='', routing_key='my_queue',
                                                           body=ANY)
        assert_true(self.connection.close.called)

        body = self.channel.basic_publish.call_args[1]['body']
        assert_equal(json.loads(body), {
            'version': '1.0',
            'project': 'my_project',
            'command': 'asdf',
            'log_key': 75,
            'log_queue': 'test_log_queue',
        })

    def test_always_close(self):
        """Ensure that the connection is closed even if an exception is thrown."""
        self.channel.queue_declare.side_effect = IOError

        with assert_raises(IOError):
            shove.send_command('my_queue', 'my_project', 'asdf', 75)
        assert_true(self.connection.close.called)


@override_settings(LOGGING_QUEUE='test_log_queue')
class SendHeartbeatTests(MockConnectTestCase):
    def test_basic_heartbeat(self):
        heartbeat_json = '{"heartbeat": true}'

        shove.send_heartbeat(['foo', 'bar'])

        self.channel.queue_declare.assert_any_call(queue='foo', durable=True)
        self.channel.basic_publish.assert_any_call(exchange='', routing_key='foo',
                                                   body=heartbeat_json)
        self.channel.queue_declare.assert_any_call(queue='bar', durable=True)
        self.channel.basic_publish.assert_any_call(exchange='', routing_key='bar',
                                                   body=heartbeat_json)
        assert_true(self.connection.close.called)

    def test_always_close(self):
        """Ensure that the connection is closed even if an exception is thrown."""
        self.channel.queue_declare.side_effect = IOError

        with assert_raises(IOError):
            shove.send_heartbeat(['foo', 'bar'])
        assert_true(self.connection.close.called)


@override_settings(LOGGING_QUEUE='test_log_queue')
class ConsumeLogsTests(MockConnectTestCase):
    def _get_consume(self, callback):
        shove.consume_logs(callback)
        return self.channel.basic_consume.call_args[0][0]

    def test_stats_consuming(self):
        """Ensure that calling consume_logs will set up a consumer on the logging queue."""
        callback = Mock()
        shove.consume_logs(callback)

        self.channel.queue_declare.assert_called_once_with(queue='test_log_queue', durable=True)
        self.channel.basic_consume.assert_called_once_with(ANY, queue='test_log_queue',
                                                           no_ack=True)
        assert_true(self.channel.start_consuming.called)
        assert_true(self.connection.close.called)

    def test_consumer_arguments(self):
        """
        The consumer should parse incoming logging events as JSON and pass the log_key and output
        arguments to the callback.
        """
        callback = Mock()
        consume = self._get_consume(callback)

        consume(self.channel, Mock(), Mock(),
                '{"log_key": 75, "output": "test output", "version": "1.0", "return_code": 0}')
        callback.assert_called_once_with(75, 0, 'test output')

    @patch('captain.projects.shove.log')
    def test_consumer_invalid_json(self, log):
        """If the consumer receives invalid JSON, it should log it and return."""
        callback = Mock()
        consume = self._get_consume(callback)

        consume(self.channel, Mock(), Mock(), 'asdfas__EWtwet')
        assert_true(log.warning.called)
        assert_true(not callback.called)

    @patch('captain.projects.shove.log')
    def test_consumer_incorrect_response(self, log):
        """If the consumer receives an incorrect response, it should log it and return."""
        callback = Mock()
        consume = self._get_consume(callback)

        consume(self.channel, Mock(), Mock(), '{"blah": "foo", "BAR": 3}')
        assert_true(log.warning.called)
        assert_true(not callback.called)

    @patch('captain.projects.shove.log')
    def test_consumer_heartbeat(self, log):
        """
        If the consumer receives a heartbeat command, it should return.
        """
        callback = Mock()
        consume = self._get_consume(callback)

        consume(self.channel, Mock(), Mock(), '{"heartbeat": true}')
        assert_true(not log.warning.called)
        assert_true(not callback.called)
