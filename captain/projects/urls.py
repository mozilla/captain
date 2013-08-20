from django.conf.urls import patterns, url

from captain.projects import views


urlpatterns = patterns('',
    url(r'^$', views.AllProjects.as_view(), name='projects.all'),
    url(r'^my_projects/$', views.MyProjects.as_view(), name='projects.mine'),
)
