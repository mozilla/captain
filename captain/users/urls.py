from django.conf.urls import patterns, url

from captain.users import views


urlpatterns = patterns('',
    url(r'^my_profile/update/$', views.UpdateUserProfile.as_view(), name='users.update_profile'),
    url(r'^login/$', views.Login.as_view(), name='users.login'),
)
