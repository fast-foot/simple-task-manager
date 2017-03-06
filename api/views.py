from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.ext.rest_framework import TokenHasScope, TokenHasReadWriteScope

from api.models import Task, Project, UserRole
from api.utils.exceptions import ResourceNotFoundException
from api.serializers import UserSerializer, UserRoleSerializer, TaskSerializer, \
                            ProjectSerializer, ProjectTasksSerializer

User = get_user_model()


def get_object(_model, pk):
    try:
        return _model.objects.get(pk=pk)
    except _model.DoesNotExist:
        raise ResourceNotFoundException


class UserList(APIView):
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request, format=None):
        users = User.objects.order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetail(APIView):
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request, pk, format=None):
        try:
            user = get_object(User, pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)

    def put(self, request, pk, format=None):
        try:
            user = get_object(User, pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)

    def delete(self, request, pk, format=None):
        user = get_object(User, pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleList(APIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']

    def get(self, request, format=None):
        user_roles = UserRole.objects.all()
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)


class TaskList(APIView):
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request, format=None):
        tasks = Task.objects.order_by('-created_date')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetail(APIView):
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = TaskSerializer

    def get(self, request, pk, format=None):
        try:
            task = get_object(Task, pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)

    def put(self, request, pk, format=None):
        try:
            task = get_object(Task, pk)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)

    def delete(self, request, pk, format=None):
        task = get_object(Task, pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectList(APIView):
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request, format=None):
        projects = Project.objects.order_by('-created_date')
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectDetail(APIView):
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request, pk, format=None):
        try:
            project = get_object(Project, pk)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)

    def put(self, request, pk, format=None):
        try:
            project = get_object(Project, pk)
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)

    def delete(self, request, pk, format=None):
        project = get_object(Project, pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectTasks(APIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']

    def get(self, request, pk, format=None):
        try:
            project = get_object(Project, pk)
            tasks = project.tasks.order_by('-created_date')
            serializer = ProjectTasksSerializer(tasks, many=True)
            return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)


class UserProjects(APIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']

    def get(self, request, pk, format=None):
        try:
            user = get_object(User, pk)
            projects = user.projects.order_by('-created_date')
            serializer = ProjectSerializer(projects, many=True)
            return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)


class ProjectUsers(APIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']

    def get(self, request, pk, format=None):
        try:
            project = get_object(Project, pk)
            users = project.users.order_by('-date_joined')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except ResourceNotFoundException as exc:
            return Response(data=exc.data, status=exc.status_code)