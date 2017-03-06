from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from api.config.tests_config import BaseTest
from api.models import Project
from api.views import UserList, UserDetail, ProjectUsers, ProjectDetail


User = get_user_model()


class ProjectTest(BaseTest):
    def test_assign_users_to_project(self):
        factory = APIRequestFactory()
        view = ProjectDetail.as_view()

        with transaction.atomic():
            users = User.objects.bulk_create([
                User(id=2, username='Test2', password='1', email='test2@mail.com'),
                User(id=4, username='Test4', password='123', email='test4@mail.com')
            ])
            users_ids = [user.id for user in users]
            project = Project.objects.create(id=1, title='TestProject')

        project_data = {
            'id': project.id,
            'title': 'NewProject',
            'users_ids': users_ids
        }

        request = factory.put('/api/projects/1', project_data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 2)
        self.assertTrue(all(user['id'] in users_ids for user in response.data['users']))

    def test_create_user(self):
        factory = APIRequestFactory()
        view = UserList.as_view()

        data = {
            'username': 'test',
            'password': '123q',
            'email': 'test@mail.com'
        }

        request = factory.post('/api/users/', data=data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['username'], response.data.get('username'))
        self.assertEqual(data['email'], response.data.get('email'))

    def test_create_user_fail_by_user_with_read_scope_only(self):
        factory = APIRequestFactory()
        view = UserList.as_view()

        data = {
            'username': 'test',
            'password': '123q'
        }

        request = factory.post('/api/users', data=data)
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_users(self):
        factory = APIRequestFactory()
        view = UserList.as_view()

        users = User.objects.bulk_create([
            User(id=2, username='Test2', password='1', email='test2@mail.com'),
            User(id=3, username='Test3', password='12', email='test3@mail.com'),
            User(id=4, username='Test4', password='123', email='test4@mail.com'),
        ])

        request = factory.get('/api/users')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 4 Because in setUp() one user instantiated.
        self.assertEqual(len(response.data), 4)

        users_names = [user['username'] for user in response.data]
        users_emails = [user['email'] for user in response.data]
        for user in users:
            self.assertIn(user.username, users_names)
            self.assertIn(user.email, users_emails)

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        users_names = [user['username'] for user in response.data]
        users_emails = [user['email'] for user in response.data]
        for user in users:
            self.assertIn(user.username, users_names)
            self.assertIn(user.email, users_emails)

    def test_get_user_detail(self):
        factory = APIRequestFactory()
        view = UserDetail.as_view()

        user = User.objects.create(id=2, username='Test2', password='2', email='test2@mail.com')

        request = factory.get('/api/users/2')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='2')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, response.data['username'])
        self.assertEqual(user.email, response.data['email'])

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='2')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, response.data['username'])
        self.assertEqual(user.email, response.data['email'])

    def test_update_user(self):
        factory = APIRequestFactory()
        view = UserDetail.as_view()

        user = User.objects.create(id=2, username='Test2', password='2', email='test2@mail.com')
        data = {
            'id': user.id,
            'username': 'Test2',
            'email': 'test2@mail.com'
        }

        request = factory.put('/api/users/2', data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='2')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, response.data['username'])
        self.assertEqual(user.email, response.data['email'])

    def test_update_user_fail_by_user_with_read_scope_only(self):
        factory = APIRequestFactory()
        view = UserDetail.as_view()

        user = User.objects.create(id=2, username='Test2', password='2', email='test2@mail.com')
        data = {
            'id': user.id,
            'username': 'Test2',
            'email': 'test2@mail.com'
        }

        request = factory.put('/api/users/2', data)
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='2')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user(self):
        factory = APIRequestFactory()
        view = UserDetail.as_view()

        users = User.objects.bulk_create([
            User(id=2, username='Test2', password='1', email='test2@mail.com'),
            User(id=3, username='Test3', password='12', email='test3@mail.com'),
            User(id=4, username='Test4', password='123', email='test4@mail.com'),
        ])
        user = users[0]

        request = factory.delete('/api/users/2')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='2')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(User.objects.all()), 3)
        self.assertNotIn(user, User.objects.all())

    def test_delete_user_fail_by_user_with_read_scope_only(self):
        factory = APIRequestFactory()
        view = UserDetail.as_view()

        User.objects.bulk_create([
            User(id=2, username='Test2', password='1', email='test2@mail.com'),
            User(id=3, username='Test3', password='12', email='test3@mail.com'),
            User(id=4, username='Test4', password='123', email='test4@mail.com')
        ])

        request = factory.delete('/api/users/2')
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='2')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_found(self):
        factory = APIRequestFactory()
        view = UserDetail.as_view()

        request = factory.put('/api/users/10')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='10')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        request = factory.delete('/api/users/10')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='10')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user_fail_because_of_existense(self):
        user = User.objects.create(id=2, username='Test2', password='2', email='test2@mail.com')
        data = {
            'id': user.id,
            'username': 'Test2',
            'email': 'test2@mail.com'
        }

        factory = APIRequestFactory()
        view = UserList.as_view()

        request = factory.post('/api/users/', data=data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_users_of_project(self):
        factory = APIRequestFactory()
        view = ProjectUsers.as_view()

        with transaction.atomic():
            users = [User.objects.create(id=i, username='U' + str(i), password=str(i))
                     for i in range(1, 4)]
            project = Project.objects.create(id=1, title='TestProject')
            project.users.set(users)
            project.save()

        request = factory.get('/api/projects/1/users')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_project_without_users(self):
        factory = APIRequestFactory()
        view = ProjectUsers.as_view()

        Project.objects.create(id=1, title='TestProject')

        request = factory.get('/api/projects/1/users')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])