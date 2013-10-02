#!/usr/bin/env python

from distutils.core import setup

setup(name='django_crowd_authz',
      version='1.0',
      description='Crowd Authentication for Django',
      author='Daniel Craigmile',
      author_email='danielc@pobox.com',
      url='https://github.com/x110dc/django_crowd_authz',
      py_modules=['auth.backends'],
      install_requires=['requests == 1.2.3'],
      )
