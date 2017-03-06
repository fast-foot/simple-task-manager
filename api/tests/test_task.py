from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from api.config.tests_config import BaseTest
from api.models import Task, Project, User
from api.views import TaskList, TaskDetail, ProjectTasks


class TaskTest(BaseTest):
    def test_create_task(self):
        project = Project.objects.create(id=1, title='TestProject')
        data = {
            'title': 'TestTask',
            'description': 'Test',
            'project_id': project.id
        }

        factory = APIRequestFactory()
        view = TaskList.as_view()

        request = factory.post('/api/tasks/', data=data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['title'], response.data.get('title'))
        self.assertEqual(data['description'], response.data.get('description'))

    def test_create_task_fail_by_user_with_read_scope_only(self):
        project = Project.objects.create(id=1, title='TestProject')
        data = {
            'title': 'TestTask',
            'description': 'Test',
            'project_id': project.id
        }

        factory = APIRequestFactory()
        view = TaskList.as_view()

        request = factory.post('/api/tasks/', data=data)
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_tasks(self):
        factory = APIRequestFactory()
        view = TaskList.as_view()

        project = Project.objects.create(title='TestProject 1')
        tasks = Task.objects.bulk_create([
            (Task(id=1, title='Test1', project=project)),
            (Task(id=2, title='Test2', project=project)),
            (Task(id=3, title='Test3', project=project))
        ])

        request = factory.get('/api/tasks')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for i in range(3):
            # Reverse comparison because tasks are ordered by created date.
            self.assertEqual(tasks[i].title, response.data[2 - i]['title'])
            self.assertEqual(tasks[i].description, response.data[2 - i]['description'])
            self.assertEqual(tasks[i].project.id, response.data[2 - i]['project']['id'])
            self.assertEqual(tasks[i].project.title, response.data[2 - i]['project']['title'])
            self.assertEqual(tasks[i].project.description,
                             response.data[2 - i]['project']['description'])

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for i in range(3):
            self.assertEqual(tasks[i].title, response.data[2 - i]['title'])
            self.assertEqual(tasks[i].description, response.data[2 - i]['description'])
            self.assertEqual(tasks[i].project.id, response.data[2 - i]['project']['id'])
            self.assertEqual(tasks[i].project.title, response.data[2 - i]['project']['title'])
            self.assertEqual(tasks[i].project.description,
                             response.data[2 - i]['project']['description'])

    def test_get_task_detail(self):
        factory = APIRequestFactory()
        view = TaskDetail.as_view()

        project = Project.objects.create(title='TestProject 1', id=1)
        task = Task.objects.create(id=1, title='Test', description='test', project_id=project.id)

        request = factory.get('/api/tasks/1')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(task.title, response.data['title'])
        self.assertEqual(task.description, response.data['description'])

        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(task.title, response.data['title'])
        self.assertEqual(task.description, response.data['description'])

    def test_update_task(self):
        factory = APIRequestFactory()
        view = TaskDetail.as_view()

        project = Project.objects.create(id=1, title='TestProject 1')
        Task.objects.create(title='TestTask', description='test', project_id=project.id, id=1)
        task_data = {
            'title': 'NewTask',
            'description': 'new one',
            'project_id': project.id
        }

        request = factory.put('/api/tasks/1', task_data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], task_data['title'])
        self.assertEqual(response.data['description'], task_data['description'])

    def test_update_task_fail_by_user_with_read_scope_only(self):
        factory = APIRequestFactory()
        view = TaskDetail.as_view()

        project = Project.objects.create(id=1, title='TestProject 1')
        Task.objects.create(title='TestTask', description='test', project_id=project.id, id=1)
        task_data = {
            'title': 'NewTask',
            'description': 'new one',
            'project_id': project.id
        }

        request = factory.put('/api/tasks/1', task_data)
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_task_to_user_after_task_updating(self):
        factory = APIRequestFactory()
        view = TaskDetail.as_view()

        project = Project.objects.create(id=1, title='TestProject 1')
        task = Task.objects.create(title='TestTask', project_id=project.id, id=1)
        user = User.objects.create(username='test', password='123')

        task_data = {
            'title': task.title,
            'description': task.description,
            'project_id': project.id,
            'user_id': user.id
        }

        request = factory.put('/api/tasks/1', task_data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], user.id)

    def test_assign_task_to_user_after_task_creation(self):
        factory = APIRequestFactory()
        view = TaskList.as_view()

        project = Project.objects.create(id=1, title='TestProject 1')
        user = User.objects.create(id=1, username='test', password='123')

        task_data = {
            'title': 'Task 5',
            'description': 'test',
            'project_id': project.id,
            'user_id': user.id
        }

        request = factory.post('/api/tasks/', task_data)
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(response.data['project']['id'], project.id)

    def test_delete_task(self):
        factory = APIRequestFactory()
        view = TaskDetail.as_view()

        project = Project.objects.create(title='TestProject')
        tasks = Task.objects.bulk_create([
            (Task(id=1, title='Test1', description='d1', project=project)),
            (Task(id=2, title='Test2', description='d2', project=project)),
            (Task(id=3, title='Test3', description='d3', project=project))
        ])
        task = tasks[0]

        request = factory.delete('/api/tasks/1')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Task.objects.all()), 2)
        self.assertNotIn(task, Task.objects.all())

    def test_delete_task_fail_by_user_with_read_scope_only(self):
        factory = APIRequestFactory()
        view = TaskDetail.as_view()

        project = Project.objects.create(title='TestProject')

        Task.objects.bulk_create([
            (Task(id=1, title='Test1', project=project)),
            (Task(id=2, title='Test2', project=project)),
            (Task(id=3, title='Test3', project=project))
        ])

        request = factory.delete('/api/tasks/1')
        force_authenticate(request, user=self.test_user, token=self.read_access_token)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_task_not_found(self):
        factory = APIRequestFactory()
        view = TaskDetail.as_view()

        request = factory.put('/api/tasks/10')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='10')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        request = factory.delete('/api/tasks/10')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='10')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_tasks_of_project(self):
        factory = APIRequestFactory()
        view = ProjectTasks.as_view()

        project = Project.objects.create(id=1, title='TestProject')
        Task.objects.bulk_create([
            (Task(id=1, title='Test1', project=project)),
            (Task(id=2, title='Test2', project=project)),
            (Task(id=3, title='Test3', project=project))
        ])

        request = factory.get('/api/projects/1/tasks')
        force_authenticate(request, user=self.test_user, token=self.full_access_token)
        response = view(request, pk='1')

        self.assertEqual(len(response.data), 3)