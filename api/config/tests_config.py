import datetime
import base64

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from oauth2_provider.models import get_application_model, AccessToken

REDIRECT_URI = 'http://example.it'

UserModel = get_user_model()
Application = get_application_model()


def get_basic_auth_header(user, password):
    user_pass = '{0}:{1}'.format(user, password)
    auth_string = base64.b64encode(user_pass.encode('utf-8'))
    auth_headers = {
        'HTTP_AUTHORIZATION': 'Basic ' + auth_string.decode('utf-8'),
    }

    return auth_headers


class BaseTest(TestCase):
    def setUp(self):
        self.test_user = UserModel.objects.create_user("alex", "alex@mail.com", "12345")
        self.application = Application(
            name='Test Application',
            redirect_uris=REDIRECT_URI,
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

        self.application.save()

        self.full_access_token = AccessToken.objects.create(
            user=self.test_user,
            token='1234567890',
            scope='read write',
            application=self.application,
            expires=timezone.now() + datetime.timedelta(days=1)
        )
        self.read_access_token = AccessToken.objects.create(
            user=self.test_user,
            token='1234567895',
            scope='read',
            application=self.application,
            expires=timezone.now() + datetime.timedelta(days=1)
        )

    def tearDown(self):
        self.application.delete()
        self.test_user.delete()
        self.full_access_token.delete()
        self.read_access_token.delete()