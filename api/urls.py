from django.conf.urls import url
from api import views

app_name = 'api'

urlpatterns = [
    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^tasks/$', views.TaskList.as_view(), name='task-list'),
    url(r'^projects/$', views.ProjectList.as_view(), name='project-list'),
    url(r'^tasks/(?P<pk>[0-9]+)$', views.TaskDetail.as_view(), name='task-detail'),
    url(r'^projects/(?P<pk>[0-9]+)$', views.ProjectDetail.as_view(), name='project-detail'),
    url(r'^users/(?P<pk>[0-9]+)$', views.UserDetail.as_view(), name='user-detail'),
    url(r'^users/(?P<pk>[0-9]+)/projects', views.UserProjects.as_view(), name='user-projects'),
    url(r'^projects/(?P<pk>[0-9]+)/users', views.ProjectUsers.as_view(), name='project-users'),
    url(r'^projects/(?P<pk>[0-9]+)/tasks', views.ProjectTasks.as_view(), name='project-tasks')
]