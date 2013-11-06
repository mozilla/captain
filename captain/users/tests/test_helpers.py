from django.contrib.auth.models import User

from django_nose.tools import assert_equal, assert_true

from captain.base.tests import TestCase
from captain.users.helpers import gravatar_url, user_display
from captain.users.tests import UserFactory


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


class TestUserDisplay(TestCase):
    def test_html_in_name(self):
        """If a user's display name has HTML in it it must be escaped."""
        user = UserFactory.create()
        user.profile.display_name = 'foo<span>bar</span>'
        output = user_display(user)
        assert_true(output.endswith('foo&lt;span&gt;bar&lt;/span&gt;'))
