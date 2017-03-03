from typing import List, Dict, Optional, Union
from django.utils.timezone import datetime
from django.core.mail import send_mail
from smtplib import SMTPException

from .models import Task, User

FROM_EMAIL = 'alex.chudovsky@gmail.com'


def fetch_users_with_assigned_tasks() -> List[User]:
    assigned_tasks = Task.objects.exclude(user_id__isnull=True)\
                                 .filter(assigned_date__date=datetime.today(),
                                         user__email__isnull=False)

    users_ids = [task.user_id for task in assigned_tasks]
    users = User.objects.in_bulk(users_ids)

    return users.values()


def notify_users(users: List[User], subject: Optional[str]) -> List[Dict[str, Union[str, int]]]:
    notified_users = []

    try:
        for user in users:
            message = 'Dear, {username}! Task [{title}] has been assigned to you at {time}.'.format(
                username=user.username,
                title=user.task.title,
                time=user.task.created_date.strftime('%I:%M %p on %B %d, %Y')
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

            notified_users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'notified': True
            })

    except SMTPException as e:
        print(str(e))

    return notified_users
