from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Project, UserRole

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'created_date')


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('id', 'role_name')
        depth = 1


class UserSerializer(serializers.HyperlinkedModelSerializer):
    role = UserRoleSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'date_joined')


class TaskSerializer(serializers.ModelSerializer):
    user = UserRoleSerializer()

    class Meta:
        model = Task
        fields = ('project', 'id', 'title', 'description', 'created_date', 'due_date', 'user')