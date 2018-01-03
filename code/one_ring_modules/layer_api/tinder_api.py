#!/usr/bin/env python3
# coding=utf-8

import copy
import json
import logging
import re

from one_ring_modules.layer_api.one_ring_modules_api import InvalidCredentialsException, RequestErrorException

import requests
import werkzeug
import robobrowser

TINDER_HOST_URL = 'https://api.gotinder.com'
TINDER_HOST_V2_URL = 'https://api.gotinder.com/v2'
MOBILE_USER_AGENT = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"
FB_AUTH_LINK = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F" \
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

LOG_TAG = '[Tinder API] '


class TinderApi:
    """
    All Tinder APIs rely on a header which serves as its only authentication
    The factory method log_in() will create a TinderSession object with an attribute "head
    """

    @classmethod
    def log_in(cls, email, password):
        """
        :raises: InvalidCredentialsException if credentials are incorrect
        """
        fb_id, fb_auth_token = get_id_and_auth_token(email, password)
        return cls(email, password, fb_id, fb_auth_token)

    def __init__(self, email, password, fb_id, fb_auth_token):
        self.email = email
        self.password = password
        self.fb_id = fb_id
        self.fb_auth_token = fb_auth_token
        self.headers = copy.deepcopy(HEADERS_TEMPLATE)
        self.headers.update({"X-Auth-Token": self.fb_auth_token})

    def log_in_again(self):
        fb_id, fb_auth_token = get_id_and_auth_token(self.email, self.password)
        self.fb_id = fb_id
        self.fb_auth_token = fb_auth_token
        self.headers = copy.deepcopy(HEADERS_TEMPLATE)
        self.headers.update({"X-Auth-Token": self.fb_auth_token})

    # TODO write a retry decorator wrapper
    def get_recommendations(self):
        """
        :return: list of users that you can swipe on
        """
        url = TINDER_HOST_URL + '/user/recs'
        r = requests.get(url, headers=self.headers)
        if r.ok:
            return r.json()['results']
        else:
            logging.debug(LOG_TAG + 'Session expired. Getting a new session.')
            self.log_in_again()
            return self.get_recommendations()

    def get_matches_batch(self, count):
        """
        :return: list of users IDs which you can message
        """
        url = TINDER_HOST_V2_URL + '/matches?count=' + str(count) + 'locale=en'
        r = requests.get(url, headers=self.headers)
        if r.ok:
            return r.json()['data']['matches']
        else:
            logging.debug(LOG_TAG + 'Session expired. Getting a new session.')
            self.log_in_again()
            return self.get_recommendations()

    def send_message(self, match_id, message):
        url = TINDER_HOST_URL + '/user/matches/' + match_id
        r = requests.post(url, headers=self.headers, data=json.dumps({"message": message}))
        if r.ok:
            return r.json()
        else:
            logging.debug(LOG_TAG + 'Session expired. Getting a new session.')
            self.log_in_again()
            return self.send_message(match_id, message)


def get_fb_access_token(email, password):
    s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
    s.open(FB_AUTH_LINK)
    f = s.get_form()
    f["email"] = email
    f["pass"] = password
    s.submit_form(f)
    f = s.get_form()
    s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
    access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    return access_token


def get_fb_id(fb_access_token):
    response = requests.get('https://graph.facebook.com/me?access_token=' + fb_access_token)
    return response.json()["id"]


def get_auth_token(fb_access_token, fb_id):
    url = TINDER_HOST_URL + '/auth'
    response = requests.post(url,
                             headers=HEADERS_TEMPLATE,
                             data=json.dumps(
                                 {'facebook_token': fb_access_token, 'facebook_id': fb_id})
                             )
    return response.json()["token"]


def get_id_and_auth_token(email, password):
    try:
        logging.warning(LOG_TAG + 'Logging in now. This should happen very rarely.')
        fb_access_token = get_fb_access_token(email, password)  # If this fails, check email/password
        fb_id = get_fb_id(fb_access_token)
        fb_auth_token = get_auth_token(fb_access_token, fb_id)
        logging.info(LOG_TAG + 'Log in success!')
        return fb_id, fb_auth_token
    except werkzeug.exceptions.BadRequestKeyError:
        raise InvalidCredentialsException
