import json
from contextlib import closing

from django.conf import settings

import pika


def send_command(queue, project_name, command):
    """Send a command to an instance of shove."""
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=pika.credentials.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASS
        )
    )

    with closing(pika.BlockingConnection(parameters)) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)

        body = json.dumps({'project': project_name, 'command': command})
        channel.basic_publish(exchange='', routing_key=queue, body=body)
        connection.close()
