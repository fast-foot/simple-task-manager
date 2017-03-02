from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Task, Project, User
from ..config.tests_config import mocked_datetime, TASK_LIST_VIEW_NAME, TASK_DETAIL_VIEW_NAME, \
                                  PROJECT_TASKS_VIEW_NAME


class TaskTest(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('alex', 'alex@mail.com', 'pass')
        self.client.login(username='alex', password='pass')

    def test_get_tasks(self):
        project = Project.objects.create(title='TestProject 1')
        tasks = [Task.objects.create(title='TestTask' + str(i),
                                     description='T' + str(i),
                                     project_id=project.id) for i in range(3)]

        response = self.client.get(reverse(TASK_LIST_VIEW_NAME))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for task, resp_task in zip(tasks, response.data):
            self.assertEqual(task.title, resp_task['title'])
            self.assertEqual(task.description, resp_task['description'])
            self.assertEqual(task.project_id, resp_task['project'])

    def test_get_task_detail(self):
        project = Project.objects.create(title='TestProject 1')
        tasks = [Task.objects.create(title='TestTask' + str(i),
                                     description='T' + str(i),
                                     project_id=project.id) for i in range(3)]
        task = tasks[0]

        response = self.client.get(reverse(TASK_DETAIL_VIEW_NAME, args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(task.title, response.data['title'])
        self.assertEqual(task.description, response.data['description'])

    def test_delete_project(self):
        project = Project.objects.create(title='TestProject 1')
        tasks = [Task.objects.create(title='TestTask' + str(i),
                                     description='T' + str(i),
                                     project_id=project.id) for i in range(3)]
        task = tasks[2]

        response = self.client.delete(reverse(TASK_DETAIL_VIEW_NAME, args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Task.objects.all()), 2)
        self.assertNotIn(task, Task.objects.all())

    def test_task_not_found(self):
        response = self.client.get(reverse(TASK_DETAIL_VIEW_NAME, args=[11]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_tasks_per_project(self):
        project = Project.objects.create(title='TestProject 1')
        tasks = [Task.objects.create(title='TestTask' + str(i),
                                     description='T' + str(i),
                                     project_id=project.id) for i in range(3)]

        response = self.client.get(reverse(PROJECT_TASKS_VIEW_NAME, args=[project.id]))
        self.assertEqual(len(response.data), 3)