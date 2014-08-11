from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import dateformat, timezone

from captain.projects import shove


class Project(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    homepage = models.URLField()

    queue = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255, unique=True)
    shove_instances = models.ManyToManyField('ShoveInstance', related_name='projects')

    class Meta:
        permissions = (
            ('can_run_commands', 'Can run commands'),
        )

    def send_command(self, user, command, shove_instances):
        """
        Send a command to be executed by shove for this project.

        :param user:
            User that is running the command. This can be None if the
            command is being run automatically as a scheduled command.

        :param command:
            Name of the command to execute.

        :param shove_instances:
            List or queryset of ShoveInstances that the command should
            be sent to.

        :raises:
            PermissionDenied: If a user is given and that user does not
            have permission to run a command on this project.
        """
        if user and not user.has_perm('projects.can_run_commands', self):
            raise PermissionDenied('User `{0}` does not have permission to run command `{1}` on '
                                   'project `{2}`.'.format(user.email, command, self.name))

        active_shove_instances = self.shove_instances.filter(active=True)
        if not frozenset(shove_instances).issubset(frozenset(active_shove_instances)):
            raise ValueError('Given shove instances are not in the set of active shove instances '
                             'for this project.')

        sent_command = SentCommand.objects.create(project=self, user=user, command=command)
        for shove_instance in shove_instances:
            shove_instance.send_command(self, command, sent_command)
        return sent_command

    def get_absolute_url(self):
        return reverse('projects.details.history', args=(self.pk,))

    def __unicode__(self):
        return u'<Project {0}>'.format(self.name)


class ShoveInstance(models.Model):
    """An instance of shove running on a remote server."""
    routing_key = models.CharField(max_length=255, unique=True, blank=False)
    hostname = models.CharField(max_length=255, blank=False)

    active = models.BooleanField(default=False)
    last_heartbeat = models.DateTimeField(default=None, null=True)

    def send_command(self, project, command, sent_command):
        """
        Send a command to be executed by this ShoveInstance.

        :param project:
            Project instance for the project to run the given command
            on.

        :param command:
            Name of the command to execute.

        :param sent_command:
            SentCommand instance to log the results of this command to.
        """
        log = CommandLog.objects.create(shove_instance=self, sent_command=sent_command)
        shove.send_command(self.routing_key, project.project_name, command, log.pk)
        return log

    def __unicode__(self):
        return self.hostname


class ScheduledCommand(models.Model):
    """Command that runs automatically at a certain interval."""
    project = models.ForeignKey(Project)
    command = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    hostnames = models.TextField(blank=True)

    INTERVAL_CHOICES = (
        (15, 'Every 15 Minutes'),
        (30, 'Every 30 Minutes'),
        (60, 'Once an hour'),
        (180, 'Once every 3 hours'),
        (360, 'Once every 6 hours'),
        (720, 'Once every 12 hours'),
        (1440, 'Once a day'),
    )
    interval_minutes = models.IntegerField('Interval', choices=INTERVAL_CHOICES, default=15)
    last_run = models.DateTimeField(null=True)

    @property
    def is_due(self):
        """
        True if it has been self.interval_minutes since the last run of
        this command, False otherwise.
        """
        if not self.last_run:
            return True
        else:
            return (timezone.now() - self.last_run) > timedelta(minutes=self.interval_minutes)

    @property
    def shove_instances(self):
        """
        Queryset of ShoveInstances with hostnames matching the ones
        specified for this command.
        """
        return ShoveInstance.objects.filter(active=True, hostname__in=self.hostnames.split(','))

    def run(self):
        """
        Send the command for this scheduled command and log the current
        time as the last run.
        """
        self.project.send_command(None, self.command, self.shove_instances)
        self.last_run = timezone.now()
        self.save()


class SentCommand(models.Model):
    """
    A command that has been sent to a set of Shove instances for a
    particular project.
    """
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User, null=True)
    command = models.CharField(max_length=255)
    sent = models.DateTimeField(auto_now_add=True)

    @property
    def success(self):
        """
        True if all shove instances executed this command successfully,
        None if there are instances that haven't reported back, and
        False if there were failures.
        """
        successes = [log.success for log in self.commandlog_set.all()]
        return None if None in successes else all(successes)


class CommandLog(models.Model):
    """Log of information about a single run of a command."""
    sent_command = models.ForeignKey(SentCommand, null=True)
    shove_instance = models.ForeignKey(ShoveInstance, null=True)
    sent = models.DateTimeField(auto_now_add=True)

    def _logfile_filename(self, filename):
        return 'logs/{project_slug}/{command}.{hostname}.{sent}.log'.format(
            project_slug=self.sent_command.project.slug,
            command=slugify(self.sent_command.command),
            hostname=slugify(self.shove_instance.hostname),
            sent=dateformat.format(self.sent, 'U')
        )
    logfile = models.FileField(blank=True, default='', upload_to=_logfile_filename)
    return_code = models.IntegerField(null=True, default=None)

    @property
    def success(self):
        return None if self.return_code is None else self.return_code == 0

    @property
    def log(self):
        with self.logfile as f:
            return f.read()

    @log.setter
    def log(self, content):
        self.logfile.save(None, ContentFile(content), save=False)
