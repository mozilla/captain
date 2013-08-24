from django.conf.urls import patterns, url

from captain.projects import views


urlpatterns = patterns('',
    url(r'^$', views.AllProjects.as_view(), name='projects.all'),
    url(r'^my_projects/$', views.MyProjects.as_view(), name='projects.mine'),
    url(r'^projects/$', views.AllProjects.as_view(), name='projects.list'),
    url(r'^projects/(?P<pk>\d+)/$', views.ProjectDetails.as_view(), name='projects.details'),

    url(r'^projects/(?P<pk>\d+)/run_command$', views.RunCommand.as_view(),
        name='projects.run_command'),
)
