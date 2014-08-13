from datetime import datetime

from django.test import TestCase as DjangoTestCase
from django.utils import timezone

from django_browserid.tests import mock_browserid


class TestCase(DjangoTestCase):
    def client_login_user(self, user):
        with mock_browserid(user.email):
            self.client.login()


def aware_datetime(*args, **kwargs):
    return timezone.make_aware(datetime(*args, **kwargs), timezone.get_default_timezone())


class CONTAINS(object):
    """Helper object that is equal to any object that contains a specific value."""
    def __init__(self, *values):
        self.values = values

    def __eq__(self, other):
        return all(v in other for v in self.values)

    def __ne__(self, other):
        return not self.__eq__(other)
