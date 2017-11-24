#!/usr/bin/env python3

import logging
import random
import os
import time

import requests

from one_ring_modules.api.okc.profile import Profile

# Credentials (username & password)
USERNAME = os.environ.get('ONE_RING_OKC_USERNAME')
PASSWORD = os.environ.get('ONE_RING_OKC_PASSWORD')


class Session(object):
    """
    A `requests.Session` with convenience methods for interacting with
    okcupid.com
    """

    default_login_headers = {
        'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/37.0.2062.94 '
                       'Safari/537.36')
    }

    @classmethod
    def login(cls, requests_session=None, rate_limit=None):
        requests_session = requests_session or requests.Session()
        session = cls(requests_session, rate_limit)
        # settings.USERNAME and settings.PASSWORD should not be made
        # the defaults to their respective arguments because doing so
        # would prevent this function from picking up any changes made
        # to those values after import time.
        session.do_login(USERNAME, PASSWORD)
        return session

    def __init__(self, requests_session, rate_limit=None):
        self._requests_session = requests_session
        self.log_in_name = None
        if isinstance(rate_limit, RateLimiter):
            self.rate_limiter = rate_limit
        else:
            self.rate_limiter = RateLimiter(rate_limit)

    def __getattr__(self, name):
        return getattr(self._requests_session, name)

    def do_login(self, username, password):
        credentials = {
            'username': username,
            'password': password,
            'okc_api': 1
        }
        login_response = self.okc_post('login',
                                       data=credentials,
                                       headers=self.default_login_headers,
                                       secure=True)
        login_json = login_response.json()
        log_in_name = login_json['screenname']
        if log_in_name is None:
            raise AuthenticationError(u'Could not log in as {0}'.format(username))
        if log_in_name.lower() != username.lower():
            logging.warning(u'Expected to log in as {0} but got {1}'.format(username, log_in_name))
        logging.debug(login_response.content.decode('utf8'))

        self.access_token = login_json.get("oauth_accesstoken")
        self.log_in_name = log_in_name
        self.headers.update(self.default_login_headers)

    def build_path(self, path, secure=None):
        if secure is None:
            secure = ('secure_login' in self.cookies and
                      int(self.cookies['secure_login']) != 0)
        return u'{0}://{1}/{2}'.format('https' if secure else 'http', "www.okcupid.com", path)

    def get_profile(self, username):
        """Get the profile associated with the supplied username
        :param username: The username of the profile to retrieve."""
        return Profile(self, username)

    def get_current_user_profile(self):
        """Get the `okcupyd.profile.Profile` associated with the supplied
        username.

        :param username: The username of the profile to retrieve.
        """
        return self.get_profile(self.log_in_name)

    def quickmatch(self):
        """Return a :class:`~okcupyd.profile.Profile` obtained by visiting the
        quickmatch page.
        """
        response = self.okc_get('quickmatch', params={'okc_api': 1})
        return Profile(self, response.json()['sn'])


class RateLimiter(object):
    def __init__(self, rate_limit, wait_std_dev=None):
        self.rate_limit = rate_limit
        if rate_limit is not None and wait_std_dev is None:
            wait_std_dev = float(rate_limit) / 5
        self.wait_std_dev = wait_std_dev
        self.last_request = None

    def wait(self):
        if self.rate_limit is None: return
        if self.last_request is not None:
            wait_time = random.gauss(self.rate_limit, self.wait_std_dev)
            elapsed = time.time() - self.last_request
            if elapsed < wait_time:
                time.sleep(wait_time - elapsed)
        self.last_request = time.time()


def build_okc_method(method_name):
    def okc_method(self, path, secure=None, **kwargs):
        base_method = getattr(self, method_name)
        self.rate_limiter.wait()
        response = base_method(self.build_path(path, secure), **kwargs)
        response.raise_for_status()
        return response
    return okc_method


# This code constructs the methods okc_get(), okc_put(), okc_post(), and okc_delete()
for method_name in ('get', 'put', 'post', 'delete'):
    setattr(Session, 'okc_{0}'.format(method_name), build_okc_method(method_name))


class AuthenticationError(Exception):
    pass
