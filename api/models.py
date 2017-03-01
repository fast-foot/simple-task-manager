from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_task_manager import settings


class UserRole(models.Model):
    MANAGER = 'Manager'
    DEVELOPER = 'Developer'
    ROLES = (
        (MANAGER, MANAGER),
        (DEVELOPER, DEVELOPER)
    )
    role_name = models.CharField(max_length=30, choices=ROLES, default=DEVELOPER)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    role = models.ForeignKey(UserRole, null=True)


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

