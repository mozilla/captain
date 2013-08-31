from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView
from django.views.generic.detail import SingleObjectMixin

from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user

from captain.projects.forms import RunCommandForm
from captain.projects.mixins import PermissionRequiredMixin
from captain.projects.models import Project


class AllProjects(ListView):
    """List all projects registered with Captain."""
    model = Project
    template_name = 'projects/projects.html'


class MyProjects(LoginRequiredMixin, ListView):
    """List projects that the current user has permission to run commands on."""
    template_name = 'projects/my_projects.html'

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'can_run_commands', Project)


class RunCommand(PermissionRequiredMixin, SingleObjectMixin, FormView):
    """Show a form for running commands on a project."""
    model = Project
    permission_required = 'projects.can_run_commands'
    form_class = RunCommandForm
    template_name = 'projects/details/run_command.html'
    context_object_name = 'project'

    def dispatch(self, *args, **kwargs):
        # Workaround for an issue in SingleObjectMixin where it relies on self.object being set
        # before it can run get_context_data.
        self.object = self.get_object()
        return super(RunCommand, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """Send the submitted command to shove and redirect to the log list."""
        project = self.get_object()
        project.send_command(self.request.user, form.cleaned_data['command'])
        messages.success(self.request, 'Command sent successfully!')
        return redirect(project)

    def form_invalid(self, form):
        """Notify the user of the issue and redisplay the command form."""
        messages.error(self.request, 'There was a problem sending your command. Please try again.')
        return super(RunCommand, self).form_invalid(form)

    def permission_denied(self):
        """
        Notify the user that they do not have permission to run commands and redirect to the log
        list.
        """
        messages.error(self.request, 'You do not have permission to run commands for {project}.'
                       .format(project=self.object.name))
        return redirect(reverse('projects.details.history', args=(self.object.pk,)))


class ProjectHistory(ListView):
    """Show a list of all the log entries for commands run on a project."""
    model = Project
    template_name = 'projects/details/history.html'
    context_object_name = 'commands'

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return self.project.commandlog_set.order_by('-sent')

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectHistory, self).get_context_data(*args, **kwargs)
        context['project'] = self.project
        return context
