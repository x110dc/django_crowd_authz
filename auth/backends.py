import json
import logging

import requests
from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class CrowdConfig(object):
    """
    Represents the Crowd server configuration as specified in
    Django's settings.
    """

    config = settings.CROWD_AUTH

    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]
        raise AttributeError('\'{}\' not found in settings.CROWD_AUTH'.format(
            name))


class CrowdBackend(object):

    config = CrowdConfig()

    def crowd_user(self):
        """
        Makes the actual call to Crowd to authenticate a user. If
        authentication is successful a dictionary representing user
        attributes is returned.  If unsuccessful 'None' is returned.
        """

        try:
            auth = (self.config.AppName, self.config.AppPassword)
            url = self.config.URL
        except Exception as e:
            logger.error(str(e))
            return None
        params = {'username': self.username}
        data = json.dumps({'value': self.password})
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
        }
        try:
            response = requests.post(url, auth=auth, params=params, data=data,
                                     timeout=5, headers=headers)
        except Exception as e:
            logger.critical('Error connecting to Crowd: {}'.format(e))
            return None
        if response.status_code == 200:
            logger.info('username <{}> authenticated via Crowd'.format(
                self.username))
            return json.loads(response.content)

        try:
            error = json.loads(response.content)['message']
        except Exception as e:
            error = 'Error parsing server response: {}'.format(e)

        logger.info('Crowd authentication for <{}> failed: {}'.format(
            self.username, error))
        return None

    def authenticate(self, username=None, password=None):
        """
        Standard Django authentication function. Makes call
        to Crowd to authenticate.  If user authenticates but doesn't exist
        in Django she is created.
        """

        self.username = username
        self.password = password

        crowd_user = self.crowd_user()

        if crowd_user:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                user.set_unusable_password()
                user.is_staff = False
                user.is_superuser = False
                try:
                    user.email = crowd_user['email']
                    user.first_name = crowd_user['first-name']
                    user.last_name = crowd_user['last-name']
                except KeyError:
                    pass
                user.save()
                logger.info('Django user created <{}> from Crowd user'.format(
                    user.username))
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
