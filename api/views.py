from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from functools import wraps

from .config.api_config import api_config
from .models import Task, Project
from api.serializers import UserSerializer, TaskSerializer, ProjectSerializer

User = get_user_model()


def is_manager_or_admin(func):
    @wraps(func)
    def decorator(self, *args, **kwargs):
        if isinstance(args[0], Request):
            if (args[0].user.role == 'Manager' or args[0].user.is_superuser) and args[0].user.is_active:
                return func(self, *args, **kwargs)
            return Response(data={
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'Permissions denied'
            })
    return decorator


class UserList(APIView):
    @is_manager_or_admin
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @is_manager_or_admin
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return

    @is_manager_or_admin
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        if not user:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'User is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)

        return Response(serializer.data)


class TaskList(APIView):
    @is_manager_or_admin
    def get(self, request, format=None):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @is_manager_or_admin
    def post(self, request, format=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetail(APIView):
    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return

    @is_manager_or_admin
    def get(self, request, pk, format=None):
        task = self.get_object(pk)
        if not task:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Task is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)

        return Response(serializer.data)

    @is_manager_or_admin
    def put(self, request, pk, format=None):
        task = self.get_object(pk)
        if not task:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Task is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(data=api_config.response_payload.BAD_REQUEST,
                            status=status.HTTP_400_BAD_REQUEST)
        except ParseError:
            return Response(data=api_config.response_payload.BAD_REQUEST,
                            status=status.HTTP_400_BAD_REQUEST)

    @is_manager_or_admin
    def delete(self, request, pk, format=None):
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectList(APIView):
    @is_manager_or_admin
    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    @is_manager_or_admin
    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetail(APIView):
    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return

    @is_manager_or_admin
    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        if not project:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Project is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectSerializer(project)

        return Response(serializer.data)

    @is_manager_or_admin
    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        if not project:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Project is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = ProjectSerializer(project, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(data=api_config.response_payload.BAD_REQUEST,
                            status=status.HTTP_400_BAD_REQUEST)
        except ParseError:
            return Response(data=api_config.response_payload.BAD_REQUEST,
                            status=status.HTTP_400_BAD_REQUEST)

    @is_manager_or_admin
    def delete(self, request, pk, format=None):
        project = self.get_object(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectTasks(APIView):
    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return

    @is_manager_or_admin
    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        if not project:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Project is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        tasks = project.tasks.all()
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)


class UserProjects(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return

    @is_manager_or_admin
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        if not user:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'User is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        projects = user.projects.all()
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data)


class ProjectUsers(APIView):
    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return

    @is_manager_or_admin
    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        if not project:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Project is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        users = project.users.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)