import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from captain.projects.models import ScheduledCommand


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run any ScheduledCommands that are due to be run.'

    def handle(self, *args, **kwargs):
        # Log INFO events to make the commandline output a little more useful.
        logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
        log.info('Searching for scheduled commands...')

        for command in ScheduledCommand.objects.all():
            if command.is_due:
                log.info('Running `{0}` on project `{1}` for interval `{2}`'.format(
                         command.command, command.project.name,
                         command.get_interval_minutes_display()))
                command.project.send_command(None, command.command)
                command.last_run = timezone.now()
                command.save()

        log.info('Done!')
