#!/usr/bin/env python3
# coding=utf-8

import copy
import json
import os
import re

import requests
import robobrowser

TINDER_HOST_URL = 'https://api.gotinder.com'
MOBILE_USER_AGENT = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"
FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F" \
          "&display=touch" \
          "&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_" \
          "auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22" \
          "com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D" \
          "&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2C" \
          "user_friends%2Cuser_work_history%2Cuser_likes" \
          "&response_type=token%2Csigned_request" \
          "&default_audience=friends" \
          "&return_scopes=true" \
          "&auth_type=rerequest" \
          "&client_id=464891386855067" \
          "&ret=login" \
          "&sdk=ios" \
          "&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1" \
          "&ext=1470840777" \
          "&hash=AeZqkIcf-NEW6vBd"

HEADERS_TEMPLATE = {
    'app_version': '6.9.4',
    'platform': 'ios',
    "content-type": "application/json",
    "User-agent": "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)",
}

# Credentials (username & password)
FB_EMAIL = os.environ.get('ONE_RING_FB_EMAIL')
FB_PASSWORD = os.environ.get('ONE_RING_FB_PASSWORD')


class TinderSession:  # TODO Use a factory pattern and limit output to only self.header
    """
    | DEBUG AS FOLLOWS:
    |
    | cd C:\Users\PC147-GamingComp2\PycharmProjects\One-Ring-Dating
    | code\one_ring_virtual_env\Scripts\activate.bat
    | cd code\one_ring_modules\auth\tinder
    | python
    | from tinder_session import TinderSession
    | t = TinderSession("<username>", "<password>")
    | t.get_recommendations()
    | quit()
    cls
    """

    @classmethod
    def log_in(cls):
        return cls(FB_EMAIL, FB_PASSWORD)

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.fb_access_token = self.get_fb_access_token()  # If this fails, check email/password
        self.fb_id = self.get_fb_id()
        self.fb_auth_token = self.get_auth_token()
        self.headers = copy.deepcopy(HEADERS_TEMPLATE)
        self.headers.update({"X-Auth-Token": self.fb_auth_token})

    def get_fb_access_token(self):
        s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
        s.open(FB_AUTH)
        f = s.get_form()
        f["pass"] = self.password
        f["email"] = self.email
        s.submit_form(f)
        f = s.get_form()
        s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
        access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
        return access_token

    def get_fb_id(self):
        """
        :returns FB ID from access token
        """
        response = requests.get('https://graph.facebook.com/me?access_token=' + self.fb_access_token)
        return response.json()["id"]

    def get_auth_token(self):
        url = TINDER_HOST_URL + '/auth'
        response = requests.post(url,
                                 headers=HEADERS_TEMPLATE,
                                 data=json.dumps(
                                {'facebook_token': self.fb_access_token, 'facebook_id': self.fb_id})
                                 )
        return response.json()["token"]

    def get_recommendations(self):
        """
        :return: list of users that you can swipe on
        """
        try:
            r = requests.get('https://api.gotinder.com/user/recs', headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong with getting recomendations:", e)

    def get_recs_v2(self):
        try:
            url = TINDER_HOST_URL + '/v2/recs/core?locale=en-US'
            r = requests.get(url, headers=self.headers)
            return r.json()
        except Exception as e:
            print('excepted')


class AuthenticationError:
    pass
