import datetime

from simple_task_manager import celery_app
from .utils import fetch_users_with_assigned_tasks, notify_users

EMAIL_NOTIFICATION_PERIOD_HOURS = 24
EMAIL_SUBJECT = 'Task manager email'

celery_app.conf.timezone = 'UTC'


@celery_app.task
def send_email():
    users = fetch_users_with_assigned_tasks()
    return notify_users(users, EMAIL_SUBJECT)


celery_app.conf.update(
    CELERYBEAT_SCHEDULE={
        'daily-schedule': {
            'task': 'api.tasks.send_email',
            'schedule': datetime.timedelta(hours=EMAIL_NOTIFICATION_PERIOD_HOURS)
        }
    }
)
