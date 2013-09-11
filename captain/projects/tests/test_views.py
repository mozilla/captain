from datetime import datetime

from django.core.urlresolvers import reverse

from django_nose.tools import assert_equal, assert_true
from guardian.shortcuts import assign_perm
from mock import Mock, patch

from captain.base.tests import TestCase
from captain.projects import views
from captain.projects.models import ScheduledCommand
from captain.projects.tests import CommandLogFactory, ProjectFactory
from captain.users.tests import UserFactory


class MyProjectsTests(TestCase):
    def test_queryset(self):
        """
        get_queryset should return all projects that the current user has permission to run
        commands on.
        """
        project1, project2, project3 = ProjectFactory.create_batch(3)
        user = UserFactory.create()
        assign_perm('can_run_commands', user, project1)
        assign_perm('can_run_commands', user, project2)

        self.client_login_user(user)
        response = self.client.get(reverse('projects.mine'))
        assert_equal(set(response.context['object_list']), set([project1, project2]))


class RunCommandTests(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()
        self.url = reverse('projects.details.run_command', args=(self.project.pk,))

    def _run_command(self, **kwargs):
        return self.client.post(self.url, kwargs)

    def _login_user(self, with_permission):
        user = UserFactory.create()
        self.client_login_user(user)
        if with_permission:
            assign_perm('can_run_commands', user, self.project)
        return user

    def test_not_logged_in(self):
        """If the user is not authenticated, redirect them to the login page."""
        response = self._run_command(command='blah')
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('users.login'), self.url))

    def test_permission_required(self):
        """
        If the current user doesn't have permission to run commands on this project, redirect them
        to the history page.
        """
        self._login_user(False)
        response = self._run_command(command='blah')
        self.assertRedirects(response,
                             reverse('projects.details.history', args=(self.project.pk,)))

    @patch.object(views.RunCommand, 'get_object')
    def test_valid_command(self, get_object):
        """
        If the user submits a valid command, send it to shove and redirect back to the project.
        """
        # Mock send_command on the project returned by get_object to inject it into the view.
        self.project.send_command = Mock()
        get_object.return_value = self.project

        user = self._login_user(True)
        response = self._run_command(command='blah')
        self.assertRedirects(response, self.project.get_absolute_url())
        self.project.send_command.assert_called_once_with(user, 'blah')


class ProjectHistoryTests(TestCase):
    def test_no_project_404(self):
        """If a project cannot be found with the project ID from the url, return a 404."""
        response = self.client.get(reverse('projects.details.history', args=(99999999,)))
        assert_equal(response.status_code, 404)

    def test_get_queryset(self):
        """
        The queryset being displayed should be all the command logs for the project, sorted by the
        time they were sent in reverse.
        """
        project = ProjectFactory.create()
        log1 = CommandLogFactory.create(project=project, sent=datetime(2013, 4, 1))
        log2 = CommandLogFactory.create(project=project, sent=datetime(2013, 4, 2))
        log3 = CommandLogFactory.create(project=project, sent=datetime(2013, 4, 3))

        view = views.ProjectHistory(kwargs={'project_id': project.id})
        assert_equal(list(view.get_queryset()), [log3, log2, log1])


class ScheduleTests(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()
        self.url = reverse('projects.details.schedule', args=(self.project.pk,))

    def _schedule(self, **kwargs):
        return self.client.post(self.url, kwargs)

    def _login_user(self, with_permission):
        user = UserFactory.create()
        self.client_login_user(user)
        if with_permission:
            assign_perm('can_run_commands', user, self.project)
        return user

    def test_not_logged_in(self):
        """If the user is not authenticated, redirect them to the login page."""
        response = self._schedule(command='blah', interval_minutes=15)
        self.assertRedirects(response, '{0}?next={1}'.format(reverse('users.login'), self.url))

    def test_permission_required(self):
        """
        If the current user doesn't have permission to run commands on this project, redirect them
        to the history page.
        """
        self._login_user(False)
        response = self._schedule(command='blah', interval_minutes=15)
        self.assertRedirects(response,
                             reverse('projects.details.history', args=(self.project.pk,)))

    def test_no_project_404(self):
        """If no project is found with the id from the URL, return a 404."""
        response = self.client.get(reverse('projects.details.schedule', args=(9999999999,)))
        assert_equal(response.status_code, 404)

    def test_valid_form(self):
        """
        If the user submits a valid form, create the scheduled command and redirect them back to
        the schedule.
        """
        user = self._login_user(True)
        response = self._schedule(command='blah', interval_minutes=15)
        assert_true(ScheduledCommand.objects
                    .filter(project=self.project, user=user, command='blah', interval_minutes=15)
                    .exists())
        self.assertRedirects(response, self.url)
