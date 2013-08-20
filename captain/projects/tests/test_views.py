from django.core.urlresolvers import reverse
from django.test import TestCase

from django_browserid.tests import mock_browserid
from django_nose.tools import assert_equal
from guardian.shortcuts import assign_perm

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

        with mock_browserid(user.email):
            self.client.login()

        response = self.client.get(reverse('projects.mine'))
        assert_equal(set(response.context['object_list']), set([project1, project2]))
