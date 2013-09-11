from django.contrib.auth.models import User

from django_nose.tools import assert_equal

from captain.base.tests import TestCase
from captain.users.helpers import gravatar_url


class TestGravatars(TestCase):
    def setUp(self):
        super(TestGravatars, self).setUp()

        # Gravatar hash for this email is 55502f40dc8b7c769880b10874abc9d0
        self.user = User.objects.create_user('asdf', 'test@example.com')

    def test_basic(self):
        """Passing an email returns the gravatar url for that email."""
        url = gravatar_url('test@example.com')
        assert_equal(
            url, 'https://secure.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?s=80&d=mm')

    def test_user(self):
        """Passing a user returns the gravatar url for that user's email."""
        url = gravatar_url(self.user)
        assert_equal(
            url, 'https://secure.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?s=80&d=mm')
