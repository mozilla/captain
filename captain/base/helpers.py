from django.contrib.staticfiles.storage import staticfiles_storage

from jingo import register


@register.function
def static(path):
    return staticfiles_storage.url(path)


register.function(max)
