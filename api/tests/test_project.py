from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Project, User
from ..config.tests_config import mocked_datetime, PROJECT_LIST_VIEW_NAME, PROJECT_DETAIL_VIEW_NAME


class ProjectTest(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('alex', 'alex@mail.com', 'pass')
        self.client.login(username='alex', password='pass')

    def test_create_project(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = mocked_datetime
            data = {
                'title': 'TestProject',
                'description': 'Test ...',
                'created_date': mocked_datetime
            }

            response = self.client.post(reverse(PROJECT_LIST_VIEW_NAME), data)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            data['id'] = 1
            self.assertEqual(dict(response.data), data)

    def test_get_projects(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = mocked_datetime
            projects = [Project.objects.create(title='TestProject' + str(i),
                                               description='T' + str(i)) for i in range(3)]

            response = self.client.get(reverse(PROJECT_LIST_VIEW_NAME))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 3)

            for project, resp_project in zip(projects, response.data):
                self.assertEqual(project.title, resp_project['title'])
                self.assertEqual(project.description, resp_project['description'])
                #self.assertEqual(project.created_date, resp_project['created_date'])

    def test_get_project_detail(self):
        project = Project.objects.create(title='TestProject 1', description='abcd')

        response = self.client.get(reverse(PROJECT_DETAIL_VIEW_NAME, args=[project.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(project.title, response.data['title'])
        self.assertEqual(project.description, response.data['description'])

    def test_update_project(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = mocked_datetime
            project = Project.objects.create(title='TestProject 1')
            data = {
                'id': project.id,
                'title': 'NewProject',
                'description': ''
            }

            response = self.client.put(reverse(PROJECT_DETAIL_VIEW_NAME, args=[project.id]), data=data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['title'], data['title'])
            self.assertEqual(response.data['description'], data['description'])

    def test_delete_project(self):
        projects = [Project.objects.create(title='TestProject' + str(i),
                                           description='T' + str(i)) for i in range(3)]
        project = projects[2]

        response = self.client.delete(reverse(PROJECT_DETAIL_VIEW_NAME, args=[project.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Project.objects.all()), 2)
        self.assertNotIn(project, Project.objects.all())

    def test_project_not_found(self):
        response = self.client.get(reverse(PROJECT_LIST_VIEW_NAME, args=[12]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)