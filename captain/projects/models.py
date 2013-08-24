from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import models

from captain.projects import shove


class Project(models.Model):
    name = models.CharField(max_length=256)
    homepage = models.URLField()

    queue = models.CharField(max_length=256)
    project_name = models.CharField(max_length=256)

    class Meta:
        permissions = (
            ('can_run_commands', 'Can run commands'),
        )

    def send_command(self, user, command):
        """Send a command to be executed by shove for this project."""
        if not user.has_perm('projects.can_run_commands', self):
            raise PermissionDenied('User `{0}` does not have permission to run command `{1}` on '
                                   'project `{2}`.'.format(user.email, command, self.name))

        shove.send_command(self.queue, self.project_name, command)
        CommandLog.objects.create(project=self, user=user, command=command)  # Log it!

    def get_absolute_url(self):
        return reverse('projects.details', args=(self.pk,))

    def __unicode__(self):
        return u'<Project {0}>'.format(self.name)


class CommandLog(models.Model):
    """Log of information about a single run of a command."""
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    command = models.CharField(max_length=256)
    sent = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'<CommandLog {0}:{1}:{2}>'.format(self.project.name, self.user.username,
                                                  self.command)
