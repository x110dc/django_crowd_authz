from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import check_password


class CrowdBackend(object):

    def authenticate(self, username=None, password=None):
        pass

    def get_user(self, user_id):
        pass
