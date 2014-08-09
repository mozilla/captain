import logging
from datetime import timedelta
from threading import Event, Thread

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from captain.projects import shove
from captain.projects.models import Project, ShoveInstance


log = logging.getLogger(__name__)


def handle_heartbeat_event(data):
    """
    Update the ShoveInstance table when a heartbeat event is received.
    """
    try:
        routing_key = data['routing_key']
        hostname = data['hostname']
        project_names = data['project_names'].split(',')
    except (KeyError, AttributeError):
        log.warning('Could not parse incoming heartbeat event: `{0}`.'.format(data))
        return

    shove_instance, created = ShoveInstance.objects.get_or_create(routing_key=routing_key)

    log.info('Updating shove instance for routing key `{0}`.'.format(routing_key))
    shove_instance.hostname = hostname
    shove_instance.last_heartbeat = timezone.now()
    shove_instance.active = True

    # Add new projects.
    projects = shove_instance.projects.all()
    for project_name in project_names:
        try:
            project = Project.objects.get(project_name=project_name)
            if project not in projects:
                shove_instance.projects.add(project)
        except Project.DoesNotExist:
            log.error('Could not find project with project_name = `{0}`'.format(project_name))

    # Remove old projects.
    for project in projects:
        if project.project_name not in project_names:
            shove_instance.projects.remove(project)

    shove_instance.save()


class MarkInactiveShoveInstancesThread(Thread):
    """
    Thread that marks ShoveInstances that have not sent in a heartbeat
    within a certain period as inactive.
    """
    daemon = True

    def __init__(self, *args, **kwargs):
        super(MarkInactiveShoveInstancesThread, self).__init__(*args, **kwargs)
        self.close_event = Event()

    def run(self):
        self.mark_inactive_shoves()
        while not self.close_event.wait(settings.HEARTBEAT_INACTIVE_DELAY):
            self.mark_inactive_shoves()

    def mark_inactive_shoves(self):
        old_time = timezone.now() - timedelta(seconds=settings.HEARTBEAT_INACTIVE_DELAY)
        out_of_date_shoves = ShoveInstance.objects.filter(last_heartbeat__lte=old_time,
                                                          active=True)
        out_of_date_shoves.update(active=False)

    def stop(self):
        """Inform the thread that it's time to die."""
        self.close_event.set()


class Command(BaseCommand):
    help = ('Listen for heartbeat events from shove and update the ShoveInstance table with the '
            'current status of shove instances.')

    def handle(self, *args, **kwargs):
        # Log INFO events to make the commandline output a little more
        # useful.
        fmt = '[%(threadName)10s] %(asctime)s - %(levelname)s: %(message)s'
        logging.basicConfig(format=fmt, level=logging.INFO)

        # While we're updating instances, let's look out for inactive
        # ones too.
        marking_thread = MarkInactiveShoveInstancesThread(name='marking')
        marking_thread.start()

        try:
            shove.consume(settings.HEARTBEAT_QUEUE, handle_heartbeat_event)
        except Exception as error:
            log.error('Error during monitoring: ' + unicode(error))

        marking_thread.stop()
        marking_thread.join()
