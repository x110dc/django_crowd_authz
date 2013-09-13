import json
import logging
import requests
from django.contrib.auth.models import User
from django.test import TestCase
from mock import patch
from auth.backends import CrowdBackend
from testfixtures import LogCapture


class TestCrowdBackend(TestCase):
    """
    Testing operation for normal case.
    """

    def setUp(self):
        self.config = CrowdBackend.config

        # a sample 'good' response from Crowd
        # though it is missing a 'last-name' field
        self.good = {'active': True,
                     'attributes': {'attributes': [],
                     'link': {'href': 'snipple', 'rel': 'self'}},
                     'display-name': 'Kraken McKraken',
                     'email': 'kraken.mckraken@example.com',
                     'expand': 'attributes',
                     'first-name': 'Kraken',
                     'link': {'href': 'nozzle', 'rel': 'self'},
                     'name': 'kraken.mckraken',
                     'password': {'link': {'href': 'gobble', 'rel': 't'}}}

    def test_config(self):

        self.assertEqual('foo', self.config.AppName)
        self.assertEqual('bar', self.config.AppPassword)
        self.assertEqual('baz', self.config.URL)

        with self.assertRaises(AttributeError):
            self.config.FOO

    def test_authenticate(self):
        with patch.object(requests, 'post') as mock_method:
            mock_method.return_value.content = json.dumps(self.good)
            mock_method.return_value.status_code = 200
            with LogCapture(level=logging.INFO) as log_test:
                user = CrowdBackend().authenticate('kraken.mckraken', 'quux')
                self.assertIn('<kraken.mckraken> authenticated via Crowd', str(
                    log_test))

            self.assertEqual('kraken.mckraken', user.username)
            self.assertIsInstance(user, User)
            self.assertEqual('kraken.mckraken@example.com', user.email)


class TestCrowdErrors(TestCase):
    """
    Check error conditions: settings is misconfigured, authentication fails,
    an unparseable response is received from Crowd.  Also check that logs
    are generated.
    """

    def setUp(self):
        # sample error response
        self.bad = {'message': 'zizzle'}
        # non-parseable response (not JSON)
        self.really_bad = 'fibnozzle'

    def test_crowd_user(self):
        """
        Misconfigured settings.
        """

        with patch.dict('settings.CROWD_AUTH', {'AppName': 'fubar'},
                        clear=True):
            with LogCapture(level=logging.ERROR) as log_test:
                return_value = CrowdBackend().crowd_user()
                self.assertIn(
                    '\'AppPassword\' not found in settings.CROWD_AUTH',
                    str(log_test))
            self.assertIsNone(return_value)

    def test_bad_crowd_response(self):
        """
        Authentication fails.
        """
        with patch.object(requests, 'post') as mock_method:
            mock_method.return_value.content = json.dumps(self.bad)
            mock_method.return_value.status_code = 400
            with LogCapture(level=logging.INFO) as log_test:
                user = CrowdBackend().authenticate('kraken.mckraken', 'quux')
                self.assertIn(
                    'Crowd authentication for <kraken.mckraken> failed',
                    str(log_test))

            self.assertIsNone(user)

    def test_unparseable_response(self):
        """
        Non-JSON received from Crowd.
        """
        with patch.object(requests, 'post') as mock_method:
            mock_method.return_value.content = self.really_bad
            mock_method.return_value.status_code = 400
            with LogCapture(level=logging.INFO) as log_test:
                user = CrowdBackend().authenticate('kraken.mckraken', 'quux')
                self.assertIn('Error parsing server response', str(log_test))

            self.assertIsNone(user)

    def test_dumb_thing_just_to_get_100_percent_coverage(self):
        """
        'get_user' is boilerplate Django authentication backend code, but I
        wanted 100% coverage.  ;-)
        """
        self.assertIsNone(CrowdBackend().get_user(42))
