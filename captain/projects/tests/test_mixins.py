from django.http import HttpResponse
from django.test.client import RequestFactory

from django_nose.tools import assert_equal
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin
from mock import Mock, patch

from captain.base.tests import TestCase
from captain.projects.mixins import PermissionRequiredMixin


class MyView(PermissionRequiredMixin):
    def permission_denied(self):
        return 'permission_denied'


class PermissionRequiredMixinTests(TestCase):
    def setUp(self):
        super(PermissionRequiredMixinTests, self).setUp()
        self.factory = RequestFactory()

        self.user = Mock()
        self.request = Mock(user=self.user, wraps=self.factory.get('/'))
        self.response = HttpResponse()
        self.check_permissions_patch = patch.object(GuardianPermissionRequiredMixin,
                                                    'check_permissions')

    def test_check_permissions_forbidden_authenticated(self):
        """
        If the user doesn't have permission and is authenticated, return the result of the
        permission_denied method.
        """
        self.user.is_authenticated.return_value = True
        with self.check_permissions_patch as check_permissions:
            # check_permissions returns a response if the user fails the permission check.
            check_permissions.return_value = self.response

            obj = MyView()
            assert_equal(obj.check_permissions(self.request), 'permission_denied')

    def test_check_permissions_forbidden_no_auth(self):
        """
        If the user doesn't have permission and isn't authenticated, return the response from the
        parent's check_permissions method.
        """
        self.user.is_authenticated.return_value = False
        with self.check_permissions_patch as check_permissions:
            check_permissions.return_value = self.response

            obj = MyView()
            assert_equal(obj.check_permissions(self.request), self.response)

    def test_check_permissions_allowed(self):
        """
        If the user has permission, return the value from the parent's check_permissions method
        (None).
        """
        self.user.is_authenticated.return_value = False
        with self.check_permissions_patch as check_permissions:
            # None means the permission check passed.
            check_permissions.return_value = None

            obj = MyView()
            assert_equal(obj.check_permissions(self.request), None)

            # Even if they are authenticated, we should still return None.
            self.user.is_authenticated.return_value = True
            assert_equal(obj.check_permissions(self.request), None)
