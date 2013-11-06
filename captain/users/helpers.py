import urllib
from hashlib import md5

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.html import escape

from jingo import register
from jinja2 import Markup


GRAVATAR_URL = getattr(settings, 'GRAVATAR_URL', 'https://secure.gravatar.com')


@register.function
def gravatar_url(arg, size=80):
    if isinstance(arg, User):
        email = arg.email
    else:  # Treat as email
        email = arg

    return '{url}/avatar/{email_hash}?{options}'.format(
        url=GRAVATAR_URL,
        email_hash=md5(email.lower()).hexdigest(),
        options=urllib.urlencode({'s': unicode(size), 'd': 'mm'})
    )


@register.function
def gravatar_img(arg, size=80, img_class=None):
    return Markup('<img class="{img_class}" src="{src}" width="{width}">'.format(
        img_class=img_class,
        src=gravatar_url(arg, size=size),
        width=size
    ))


@register.function
def user_display(user, gravatar_size=24):
    """Return HTML for displaying a user on the site, including their gravatar and name."""
    return Markup(' '.join((
        gravatar_img(user, size=gravatar_size),
        escape(user.display_name)
    )))
