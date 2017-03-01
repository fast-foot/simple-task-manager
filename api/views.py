from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserSerializer, TaskSerializer, ProjectSerializer
from .config.api_config import api_config
from .models import Task, Project

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def list(self, request):
        users = User.objects.all()
        serializer = TaskSerializer(users, many=True)
        return Response(serializer.data)


class TaskList(APIView):
    def get(self, request, format=None):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

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

    def delete(self, request, pk, format=None):
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectList(APIView):
    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

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

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        if not project:
            data = {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Project is not found'
            }
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)

        tasks = project.task_set.all()
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)