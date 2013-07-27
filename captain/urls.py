from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import jingo.monkey


urlpatterns = patterns('',
    url(r'', include('captain.base.urls')),
)


# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    ) + staticfiles_urlpatterns()


# Monkeypatches!
jingo.monkey.patch()
