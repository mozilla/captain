from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
from guardian.shortcuts import get_objects_for_user

from captain.projects.forms import RunCommandForm
from captain.projects.models import Project


class AllProjects(ListView):
    """List of all projects registered with Captain."""
    model = Project
    template_name = 'projects/projects.html'


class MyProjects(LoginRequiredMixin, ListView):
    """List of projects that the current user has permission to run commands on."""
    template_name = 'projects/my_projects.html'

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'can_run_commands', Project)


class ProjectDetails(DetailView):
    model = Project
    template_name = 'projects/project_details.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetails, self).get_context_data(**kwargs)
        project = context['project']

        context['form'] = RunCommandForm()
        context['commands'] = project.commandlog_set.order_by('-sent')
        return context


class RunCommand(PermissionRequiredMixin, SingleObjectMixin, View):
    model = Project
    permission_required = 'projects.can_run_commands'
    return_403 = True

    def post(self, *args, **kwargs):
        project = self.get_object()

        form = RunCommandForm(self.request.POST)
        if not form.is_valid():
            messages.error(self.request,
                           'There was a problem sending your command. Please try again.')
            return redirect(project)

        project.send_command(self.request.user, form.cleaned_data['command'])
        messages.success(self.request, 'Command sent successfully!')
        return redirect(project)
