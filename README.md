django_crowd_authz
==================

Crowd authentication backend for Django

tested with python 2.7.5 and Django 1.5.3

Requirements:

    requests

Add something like this to your Django settings:

    CROWD_AUTH = {
        'AppName': 'foo',
        'AppPassword': 'bar',
        'URL': 'https://crowd.example.com/rest/usermanagement/1/authentication',
    }

How to test:

    python manage.py test


