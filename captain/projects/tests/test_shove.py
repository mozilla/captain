import json

from django.test.utils import override_settings

from django_nose.tools import assert_equal, assert_false, assert_raises, assert_true
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


class ConsumeTests(MockConnectTestCase):
    def test_stats_consuming(self):
        """
        Ensure that calling consume will set up a consumer on the
        requested queue.
        """
        callback = Mock()
        shove.consume('myqueue', callback)

        self.channel.queue_declare.assert_called_once_with(queue='myqueue', durable=True)
        self.channel.basic_consume.assert_called_once_with(ANY, queue='myqueue', no_ack=True)
        assert_true(self.channel.start_consuming.called)
        assert_true(self.connection.close.called)

    def test_consumer_json(self):
        """
        The consumer listening to RabbitMQ should parse incoming data as
        JSON and then pass it to the callback.
        """
        callback = Mock()
        shove.consume('myqueue', callback)

        consumer = self.channel.basic_consume.call_args[0][0]
        consumer(None, None, None, '{"foo": "bar", "baz": 1}')
        callback.assert_called_with({'foo': 'bar', 'baz': 1})

    def test_consumer_json_invalid(self):
        """
        If the incoming data is invalid JSON, log a warning and do not
        call the callback.
        """
        callback = Mock()
        shove.consume('myqueue', callback)
        consumer = self.channel.basic_consume.call_args[0][0]

        with patch('captain.projects.shove.log') as log:
            consumer(None, None, None, 'invalid{json}')
            assert_false(callback.called)
            assert_true(log.warning.called)
