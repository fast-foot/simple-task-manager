from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Project, UserRole

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('project', 'id', 'title', 'description', 'created_date', 'due_date')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'created_date')


class UserSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'role', 'project')


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('user_role',)
