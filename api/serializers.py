from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Task, Project, UserRole

User = get_user_model()


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('id', 'role_name')


class UserSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(),
        required=False,
        write_only=True,
        source='role'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_id')


class ProjectSerializer(serializers.ModelSerializer):
    users_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='users',
        many=True
    )
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'created_date', 'users_ids', 'users')

    def create(self, validated_data):
        users = validated_data.pop('users') if validated_data.get('users') else []
        project = Project.objects.create(**validated_data)
        if users:
            project.users.set(users)
        return project

    def update(self, instance, validated_data):
        users = validated_data.pop('users') if validated_data.get('users') else []
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.created_date = validated_data.get('created_date', instance.created_date)
        users_to_assign = []

        for user in users:
            if user not in instance.users.all():
                users_to_assign.append(user)
        for user in users_to_assign:
            instance.users.add(user)

        return instance


class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    assigned_date = serializers.DateTimeField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='user'
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True,
        source='project'
    )

    class Meta:
        model = Task
        fields = ('id', 'project_id', 'user_id', 'project', 'user', 'title',
                  'description', 'created_date', 'due_date', 'assigned_date')

    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        task.assigned_date = timezone.now() if validated_data.get('user') else None
        return task

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)

        if instance.user and validated_data.get('user') and \
           instance.user != validated_data.get('user'):
            instance.assigned_date = timezone.now()

        instance.user = validated_data.get('user')

        return instance


class ProjectTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'created_date', 'due_date', 'assigned_date')