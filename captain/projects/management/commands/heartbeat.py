import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from captain.projects import shove
from captain.projects.models import Project


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ('Send a small heartbeat message to shove and logging processes to make sure they\'re '
            'still listening.')

    def handle(self, *args, **kwargs):
        # Send heartbeat to project queues and the logging queue.
        print 'Sending heartbeat to project and logging queues...'
        queues = list(Project.objects.values_list('queue', flat=True).distinct())
        queues.append(settings.LOGGING_QUEUE)
        shove.send_heartbeat(queues)
        print 'Done!'
