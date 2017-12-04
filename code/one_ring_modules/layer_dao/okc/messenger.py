#!/usr/bin/env python3

import logging

from one_ring_modules.layer_api.okc_api import OkcApi

LOG_TAG = '[OKC Messenger] '


class Messenger(object):  # TODO Generify into platform-agnostic Messenger in commons

    @classmethod
    def from_api(cls, api, log_only=True):
        return cls(api, log_only)

    @classmethod
    def from_credentials(cls, email, password, log_only=True):
        api = OkcApi.log_in(email, password)
        return cls(api, log_only)

    def __init__(self, api, log_only):
        self.api = api
        self.log_only = log_only

    def send_opener(self, match, message):
        """
        | This will only send a message if there is NO HISTORY at all between you and the match.
        | This is done to avoid sound like a robot / spamming your matches
        | :param id: Tinder ID of the match to receive the message
        | :return: boolean success
        |
        """
        # TODO check if there is a relationship between self and this tinder_id
        if self.api.is_conversation_is_empty(match.id):
            logging.debug(LOG_TAG + 'Messaged {0} ({1}) with the message: "{2}"'.format(match.name,
                                                                                        match.id,
                                                                                        message))
            return True
        else:
            return False
