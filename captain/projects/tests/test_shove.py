import json

from django_nose.tools import assert_equal, assert_raises, assert_true
from mock import ANY, patch

from captain.base.tests import TestCase
from captain.projects import shove


@patch('captain.projects.shove.pika')
class SendCommandTests(TestCase):
    def test_basic_publish(self, pika):
        shove.send_command('my_queue', 'my_project', 'asdf')

        connection = pika.BlockingConnection.return_value
        channel = connection.channel.return_value

        channel.queue_declare.assert_called_once_with(queue='my_queue', durable=True)
        channel.basic_publish.assert_called_once_with(exchange='', routing_key='my_queue',
                                                      body=ANY)
        assert_true(connection.close.called)

        body = channel.basic_publish.call_args[1]['body']
        assert_equal(json.loads(body), {'project': 'my_project', 'command': 'asdf'})

    def test_always_close(self, pika):
        """Ensure that the connection is closed even if an exception is thrown."""
        connection = pika.BlockingConnection.return_value
        channel = connection.channel.return_value

        channel.queue_declare.side_effect = IOError

        with assert_raises(IOError):
            shove.send_command('my_queue', 'my_project', 'asdf')
        assert_true(connection.close.called)
