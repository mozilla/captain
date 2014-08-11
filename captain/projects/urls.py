from django.conf.urls import patterns, url

from captain.projects import views


urlpatterns = patterns('',
    url(r'^$', views.AllProjects.as_view(), name='projects.all'),
    url(r'^my_projects/$', views.MyProjects.as_view(), name='projects.mine'),
    url(r'^projects/$', views.AllProjects.as_view(), name='projects.list'),

    url(r'^projects/(?P<project_id>\d+)/$', views.ProjectHistory.as_view(),
        name='projects.details.history'),
    url(r'^projects/(?P<pk>\d+)/run_command$', views.RunCommand.as_view(),
        name='projects.details.run_command'),
    url(r'^projects/(?P<project_id>\d+)/schedule$', views.Schedule.as_view(),
        name='projects.details.schedule'),
    url(r'^projects/(?P<project_id>\d+)/sent_command/(?P<pk>\d+)$',
        views.SentCommandDetails.as_view(), name='projects.details.sent_command'),
)
