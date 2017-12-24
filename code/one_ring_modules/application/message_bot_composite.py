#!/usr/bin/env python3

import logging
import os
import sys
import time

from one_ring_modules.layer_api.tinder_api import TinderApi
from one_ring_modules.layer_api.okc_api import OkcApi

from one_ring_modules.components.message_bot import MessageBot

from one_ring_modules.layer_dao.commons.local_file_matches import LocalFileMatches
from one_ring_modules.layer_dao.tinder.messenger import Messenger as TinderMessenger
from one_ring_modules.layer_dao.okc.messenger import Messenger as OkcMessenger

# Logging
LOG_NAME = 'phase_3_message_bot.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s : %(message)s'
LOG_TAG = '[Message Bot] '

# Credentials (username & password)
FB_EMAIL = os.environ.get('ONE_RING_FB_EMAIL')
FB_PASSWORD = os.environ.get('ONE_RING_FB_PASSWORD')

OKC_USERNAME = os.environ.get('ONE_RING_OKC_USERNAME')
OKC_PASSWORD = os.environ.get('ONE_RING_OKC_PASSWORD')


class MessageBotComposite:
    """
    | Phase 3 in the One-Ring-Dating Pipeline
    |
    | Stand-alone aggregation of message bots.
    """

    # TODO move api initialization to command_line.py, so that this class starts with good/None API objects
    def __init__(self):

        self.message_bots = []

        # Tinder Bot - does NOT require a local file of match IDs. Scans the inbox instead
        tinder_api = TinderApi.log_in(FB_EMAIL, FB_PASSWORD)
        if tinder_api is not None:
            tinder_message_bot = TinderMessenger.from_api(tinder_api)
            self.message_bots.append(tinder_message_bot)

        # OKC Bot -requires a local file of match IDs
        # okc_api = OkcApi.log_in(OKC_USERNAME, OKC_PASSWORD)
        # if okc_api is not None:
        #     tinder_message_bot = MessageBot('OKC',
        #                                     LocalFileMatches.from_mock_data(),
        #                                     OkcMessenger.from_api(okc_api, log_only=True))
        #     self.message_bots.append(tinder_message_bot)

        logging.info('\n'
                     '\n============================================'
                     '\nPhase 3 Message Bot is running!'
                     '\n{0}'
                     '\n============================================'
                     '\n'.format('\n'.join([b.name() + ' is online!' for b in self.message_bots])))

    def check_and_send_opener(self, opener):
        for message_bot in self.message_bots:
            message_bot.send_opener_to_all_inbox_matches(opener)


def initialize_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(LOG_FORMAT)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler(LOG_NAME)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)

    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)

    logging.debug(LOG_TAG + 'Loggers successfully initialized.')


if __name__ == '__main__':

    check_and_send_opener_rate_in_seconds = int(sys.argv[1])
    status_update_rate_in_seconds = int(sys.argv[2])

    initialize_logger()

    try:
        message_bot_facade = MessageBotComposite()
        logging.debug(LOG_TAG + 'Checking again in {0} seconds'.format(check_and_send_opener_rate_in_seconds))
        while True:
            message_bot_facade.check_and_send_opener('sup hoe')
            time.sleep()
            for seconds_remaining in range(check_and_send_opener_rate_in_seconds, 0, -1):
                sys.stdout.write("\r\n")
                seconds_passed = check_and_send_opener_rate_in_seconds - seconds_remaining
                if seconds_passed % check_and_send_opener_rate_in_seconds is 0:
                    logging.debug(LOG_TAG + '{0} seconds left until the next blast...'.format(seconds_remaining))
                time.sleep(1)

    except KeyboardInterrupt:
        logging.debug(LOG_TAG + 'Shutting down message bot...')
        logging.debug(LOG_TAG + 'Done!\n')
