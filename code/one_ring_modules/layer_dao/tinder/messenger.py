#!/usr/bin/env python3

import logging
import time

from one_ring_modules.layer_api.tinder_api import TinderApi
from one_ring_modules.layer_dao.tinder.matches import Matches

LOG_TAG = '[Tinder Messenger] '


class Messenger(object):

    @classmethod
    def from_api(cls, api, log_only=True):
        return cls(api, log_only)

    @classmethod
    def from_credentials(cls, email, password, log_only=True):
        api = TinderApi.log_in(email, password)
        return cls(api, log_only)

    def __init__(self, api, log_only):
        self.api = api
        self.matches = Matches.from_api(api)
        self.log_only = log_only

    def send_opener_to_all_inbox_matches(self, message):
        """
        | This will check all matches in your inbox (max 20) and send a message
        | IF there is NO HISTORY at all between you and the match.
        | This is done to avoid sounding like a robot / spamming your matches
        | :param id: Tinder ID of the match to receive the message
        | :return: int: number of matches where opener was successfully sent
        |
        """

        total_messaged_count = 0

        matches = self.matches.get_all_in_inbox()
        messageables_count = len(list(filter(lambda m: m.is_empty_conversation, matches)))
        logging.info(LOG_TAG + 'Got the last {0} matches from inbox: {1}. {2} match(es) are messageable'
                     .format(len(matches), [m.name for m in matches], messageables_count))

        for match in matches:
            if match.is_empty_conversation:
                logging.debug(LOG_TAG + 'Messaged {0} ({1}) with the message: "{2}"'.format(match.name,
                                                                                            match.match_id,
                                                                                            message))
                total_messaged_count += 1
                time.sleep(2)

        logging.info(LOG_TAG + 'Successfully messaged {0} match(es) from inbox}')
        return total_messaged_count
