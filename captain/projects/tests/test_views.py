from django.core.urlresolvers import reverse

from django_nose.tools import assert_equal
from guardian.shortcuts import assign_perm
from mock import Mock, patch

from captain.base.tests import TestCase
from captain.projects import views
from captain.projects.tests import ProjectFactory
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
        self.url = reverse('projects.run_command', args=(self.project.pk,))

    def _run_command(self, **kwargs):
        return self.client.post(self.url, kwargs)

    def _login_user(self, with_permission):
        user = UserFactory.create()
        self.client_login_user(user)
        if with_permission:
            assign_perm('can_run_commands', user, self.project)
        return user

    def test_not_logged_in(self):
        """If the user is not authenticated, return a 403 Forbidden."""
        response = self._run_command(command='blah')
        assert_equal(response.status_code, 403)

    def test_permission_required(self):
        """
        If the current user doesn't have permission to run commands on this project, return a 403
        Forbidden.
        """
        self._login_user(False)
        response = self._run_command(command='blah')
        assert_equal(response.status_code, 403)

    def test_invalid_method(self):
        """If the request is not a POST, return a 405 Method Not Allowed."""
        self._login_user(True)
        response = self.client.get(self.url)
        assert_equal(response.status_code, 405)

    def test_empty_command(self):
        """
        If the command string is empty, redirect back to the project.
        """
        self._login_user(True)
        response = self._run_command(command='')
        self.assertRedirects(response, self.project.get_absolute_url())

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
