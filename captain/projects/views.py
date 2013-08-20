from django.views.generic import ListView

from guardian.shortcuts import get_objects_for_user

from captain.projects.models import Project


class AllProjects(ListView):
    """List of all projects registered with Captain."""
    model = Project
    template_name = 'projects/projects.html'


class MyProjects(ListView):
    """List of projects that the current user has permission to run commands on."""
    template_name = 'projects/my_projects.html'

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'can_run_commands', Project)
