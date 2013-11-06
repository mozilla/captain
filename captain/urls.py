from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import jingo.monkey
from commonware.response.cookies.monkeypatch import patch_all as patch_cookies


admin.autodiscover()


urlpatterns = patterns('',
    url(r'', include('captain.projects.urls')),
    url(r'', include('captain.users.urls')),

    (r'^auth/', include('django_browserid.urls')),

    (r'^admin/', include(admin.site.urls)),
)


# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    ) + staticfiles_urlpatterns()


# Monkeypatches!
# Patch Django to support __html__ for rendering in Jinja.
jingo.monkey.patch()

# Patch HttpResponse to use secure, httponly cookies by default.
patch_cookies()
