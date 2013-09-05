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
    name = models.CharField(max_length=256)
    slug = models.SlugField()
    homepage = models.URLField()

    queue = models.CharField(max_length=256)
    project_name = models.CharField(max_length=256)

    class Meta:
        permissions = (
            ('can_run_commands', 'Can run commands'),
        )

    def send_command(self, user, command):
        """
        Send a command to be executed by shove for this project.

        :param user:
            User that is running the command. This can be None if the command is being run
            automatically as a scheduled command.

        :param command:
            Name of the command to execute.

        :raises:
            PermissionDenied: If a user is given and that user does not have permission to run a
            command on this project.
        """
        if user and not user.has_perm('projects.can_run_commands', self):
            raise PermissionDenied('User `{0}` does not have permission to run command `{1}` on '
                                   'project `{2}`.'.format(user.email, command, self.name))

        log = CommandLog.objects.create(project=self, user=user, command=command)
        shove.send_command(self.queue, self.project_name, command, log.pk)
        return log

    def get_absolute_url(self):
        return reverse('projects.details.history', args=(self.pk,))

    def __unicode__(self):
        return u'<Project {0}>'.format(self.name)


class ScheduledCommand(models.Model):
    """Command that runs automatically at a certain interval."""
    project = models.ForeignKey(Project)
    command = models.CharField(max_length=256)
    user = models.ForeignKey(User)

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
        if not self.last_run:
            return True
        else:
            return (timezone.now() - self.last_run) > timedelta(minutes=self.interval_minutes)


class CommandLog(models.Model):
    """Log of information about a single run of a command."""
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User, null=True)
    command = models.CharField(max_length=256)
    sent = models.DateTimeField(auto_now_add=True)

    def _logfile_filename(self, filename):
        return 'logs/{project_slug}/{command}.{sent}.log'.format(
            project_slug=self.project.slug,
            command=slugify(self.command),
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

    def __unicode__(self):
        username = self.user.username if self.user else 'The Captain'
        return u'<CommandLog {0}:{1}:{2}>'.format(self.project.name, username, self.command)
