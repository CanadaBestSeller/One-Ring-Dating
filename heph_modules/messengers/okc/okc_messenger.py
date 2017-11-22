#!/usr/bin/env python3

import re

from heph_modules import utils
from heph_modules.auth.okc.session import Session as OkcSession

class OkcMessenger(object):
    """
    Send Messages to an okcupid user.
    """
    def __init__(self):
        self.session = OkcSession.login()

    def send(self, username, message, authcode=None, thread_id=None):
        authcode = authcode or self._get_authcode(username)
        params = self.message_request_parameters(
            username, message, thread_id or 0, authcode
        )
        response = self.session.okc_get('mailbox', params=params)
        return response.json()

    def _get_authcode(self, username):
        response = self.session.okc_get('profile/{0}'.format(username))
        return get_authcode(response.content)

    def message_request_parameters(self, username, message,
                                   thread_id, authcode):
        return {
            'ajax': 1,
            'sendmsg': 1,
            'r1': username,
            'body': message,
            'threadid': thread_id,
            'authcode': authcode,
            'reply': 1 if thread_id else 0,
            'from_profile': 1
        }


@utils.curry
def get_js_variable(html_response_content, variable_name):
    return re.search('var {0} = "(.*?)";'.format(variable_name), html_response_content.decode('utf-8')).group(1)


get_authcode = get_js_variable(variable_name='AUTHCODE')
get_username = get_js_variable(variable_name='SCREENNAME')
get_id = get_js_variable(variable_name='CURRENTUSERID')
get_current_user_id = get_id
get_my_username = get_username
