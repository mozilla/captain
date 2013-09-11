from django.test import TestCase as DjangoTestCase

from django_browserid.tests import mock_browserid


class TestCase(DjangoTestCase):
    def client_login_user(self, user):
        with mock_browserid(user.email):
            self.client.login()
