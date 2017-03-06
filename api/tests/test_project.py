from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from api.config.tests_config import BaseTest
from api.models import Project
from api.views import ProjectList, ProjectDetail, UserProjects

User = get_user_model()


class ProjectTest(BaseTest):
    def test_create_project(self):
        data = {
            'title': 'TestProject',
            'description': 'Test'
        }

        factory = APIRequestFactory()
        view = ProjectList.as_view()

        request = factory.post('/api/projects/', data=data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['title'], response.data.get('title'))
        self.assertEqual(data['description'], response.data.get('description'))
        self.assertEqual(1, response.data.get('id'))

    def test_create_project_fail_by_user_with_read_scope_only(self):
        data = {
            'title': 'TestProject',
            'description': 'Test'
        }

        factory = APIRequestFactory()
        view = ProjectList.as_view()

        request = factory.post('/api/projects/', data=data)
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_projects(self):
        projects = [Project.objects.create(title='TestProject' + str(i),
                                           description='T' + str(i)) for i in range(3)]
        factory = APIRequestFactory()
        view = ProjectList.as_view()

        request = factory.get('/api/projects')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for i in range(3):
            # Reverse comparison because projects are ordered by created date.
            self.assertEqual(projects[i].title, response.data[2 - i]['title'])
            self.assertEqual(projects[i].description, response.data[2 - i]['description'])

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for i in range(3):
            self.assertEqual(projects[i].title, response.data[2 - i]['title'])
            self.assertEqual(projects[i].description, response.data[2 - i]['description'])

    def test_get_project_detail(self):
        factory = APIRequestFactory()
        view = ProjectDetail.as_view()

        project = Project.objects.create(title='TestProject 1', description='abcd', id=1)

        request = factory.get('/api/projects/1')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(project.title, response.data['title'])
        self.assertEqual(project.description, response.data['description'])

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(project.title, response.data['title'])
        self.assertEqual(project.description, response.data['description'])

    def test_update_project(self):
        factory = APIRequestFactory()
        view = ProjectDetail.as_view()

        project = Project.objects.create(id=1, title='TestProject 1')
        data = {
            'id': project.id,
            'title': 'NewProject',
            'description': 'one'
        }

        request = factory.put('/api/projects/1', data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['description'], data['description'])

    def test_update_project_fail_by_user_with_read_scope_only(self):
        factory = APIRequestFactory()
        view = ProjectDetail.as_view()

        project = Project.objects.create(id=1, title='TestProject 1')
        data = {
            'id': project.id,
            'title': 'NewProject',
            'description': 'one'
        }

        request = factory.put('/api/projects/1', data)
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project(self):
        factory = APIRequestFactory()
        view = ProjectDetail.as_view()

        projects = Project.objects.bulk_create([
            Project(id=1, title='Test1', description='d1'),
            Project(id=2, title='Test2', description='d2'),
            Project(id=3, title='Test3', description='d3')
        ])
        project = projects[0]

        request = factory.delete('/api/projects/1')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Project.objects.all()), 2)
        self.assertNotIn(project, Project.objects.all())

    def test_delete_project_fail_by_user_with_read_scope_only(self):
        factory = APIRequestFactory()
        view = ProjectDetail.as_view()

        Project.objects.bulk_create([
           Project(id=1, title='Test1', description='d1'),
            Project(id=2, title='Test2', description='d2'),
            Project(id=3, title='Test3', description='d3')
        ])

        request = factory.delete('/api/projects/1')
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_not_found(self):
        factory = APIRequestFactory()
        view = ProjectDetail.as_view()

        request = factory.put('/api/projects/10')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='10')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        request = factory.delete('/api/projects/10')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='10')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_project_fail_because_of_existense(self):
        Project.objects.create(id=1, title='TestProject')
        data = {
            'title': 'TestProject',
            'description': 'Test'
        }

        factory = APIRequestFactory()
        view = ProjectList.as_view()

        request = factory.post('/api/projects/', data=data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_projects_of_user(self):
        factory = APIRequestFactory()
        view = UserProjects.as_view()

        with transaction.atomic():
            projects = [Project.objects.create(id=i, title='T' + str(i), description='d' + str(i))
                        for i in range(1, 6)]

            user = User.objects.create(id=1, username='alex_test', password='123')
            user.projects.set(projects)
            user.save()

        request = factory.get('/api/users/1/projects')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_user_without_projects(self):
        factory = APIRequestFactory()
        view = UserProjects.as_view()

        User.objects.create(id=1, username='alex_test', password='123')

        request = factory.get('/api/users/1/projects')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])