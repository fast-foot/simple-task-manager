from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

app_name = 'api'

urlpatterns = [
    url(r'^users/$', views.UserViewSet.as_view(actions={'get': 'list'})),
    url(r'^tasks/$', views.TaskList.as_view(), name='task-list'),
    url(r'^projects/$', views.ProjectList.as_view(), name='project-list'),
    url(r'^tasks/(?P<pk>[0-9]+)$', views.TaskDetail.as_view(), name='task-detail'),
    url(r'^projects/(?P<pk>[0-9]+)$', views.ProjectDetail.as_view(), name='project-detail'),
    url(r'^projects/(?P<pk>[0-9]+)/tasks', views.ProjectTasks.as_view(), name='project-tasks'),
]

urlpatterns = format_suffix_patterns(urlpatterns)