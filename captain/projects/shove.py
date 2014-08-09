import json
import logging
from contextlib import closing

from django.conf import settings

import pika


log = logging.getLogger(__name__)


def create_connection():
    """Setup a connection to RabbitMQ."""
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=pika.credentials.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASS
        )
    )
    return pika.BlockingConnection(parameters)


def send_command(queue, project_name, command, log_key):
    """
    Send a command to an instance of shove.

    :param queue:
        Name of the queue to send the command to. Each instance of shove listens on its own queue.

    :param project_name:
        Key that identifies the project for which this command applies. Shove maintains a mapping
        between this key and the directory containing the project so it can find the command
        whitelist and scripts to execute.

    :param command:
        Name of the command to run. Projects define these names in a procfile contained in their
        repository. Invalid command names will be ignored.

    :param log_key:
        Key to identify the log that this command's output should be stored in. This is almost
        always the primary key of a CommandLog instance.
    """
    with closing(create_connection()) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=queue)

        body = json.dumps({
            'version': '1.0',  # Version of the command format.
            'project': project_name,
            'command': command,
            'log_key': log_key,
            'log_queue': settings.LOGGING_QUEUE
        })
        channel.basic_publish(exchange='', routing_key=queue, body=body)


def consume(queue_name, callback):
    """
    Connect to the specified queue and consume any incoming data.

    This will block until a KeyboardInterrupt is thrown.

    :param callback:
        Callback to run when a log event is received. Expects a callable
        ``callback(data)`` where data is a dict of the JSON data
        received.
    """
    def consume(channel, method, properties, body):
        try:
            data = json.loads(body)
        except ValueError:
            log.warning('Could not parse incoming data as JSON: `{0}`.'.format(body))
            return
        callback(data)

    with closing(create_connection()) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_consume(consume, queue=queue_name, no_ack=True)
        log.info('Listening for data on queue `{0}`.'.format(queue_name))

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            log.info('Halting monitoring for queue `{0}`.'.format(queue_name))

