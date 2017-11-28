#!/usr/bin/env python3

import logging
import os
import sys
import time

from one_ring_modules.api.tinder.session import Session as TinderSession
from one_ring_modules.api.tinder.matches import Matches as TinderMatches
from one_ring_modules.commons.message_bot import MessageBot

# Logging
LOG_NAME = 'phase_3_message_bot.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s : %(message)s'
LOG_TAG = '[Message Bot] '

# Credentials (username & password)
FB_EMAIL = os.environ.get('ONE_RING_FB_EMAIL')
FB_PASSWORD = os.environ.get('ONE_RING_FB_PASSWORD')


class MessageBotFacade:
    """
    | Phase 3 in the One-Ring-Dating Pipeline
    |
    | Stand-alone aggregation of message bots.
    """

    # TODO move session initialization to command_line.py, so that this class starts with good/None sessions
    def __init__(self):

        self.message_bots = []

        # Tinder Message Bot
        # TODO wrap this session generation logic in application/main.py
        tinder_session = TinderSession.log_in(FB_EMAIL, FB_PASSWORD)
        if tinder_session is not None:
            tinder_matches_id_provider = TinderMatches.from_session(tinder_session)
            tinder_messenger = TinderMessenger.from_session(tinder_session, log_only=true)
            tinder_picture_retriever = TinderPictureRetriever.from_session(tinder_session)
            tinder_message_bot = MessageBot('Tinder',
                                            tinder_matches_id_provider,
                                            tinder_messenger,
                                            tinder_picture_retriever)
            self.message_bots += tinder_message_bot

        logging.info('\n'
                     '\n============================================'
                     '\nPhase 3 Message Bot is running!'
                     '\n{0}'
                     '\n============================================'
                     '\n'.format('\n'.join([b.name() + ' is online!' for b in self.message_bots])))

    def check_and_send_opener(self, opener):
        for message_bot in self.message_bots:
            message_bot.send_opener_to_all_matches(opener)


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
        message_bot_facade = MessageBotFacade(check_and_send_opener_rate_in_seconds,
                                              status_update_rate_in_seconds)
        while True:
            message_bot_facade.check_and_message()
            logging.debug(LOG_TAG + 'Checking again in {0} seconds'.format(check_and_send_opener_rate_in_seconds))
            time.sleep(check_and_send_opener_rate_in_seconds)
    except KeyboardInterrupt:
        logging.debug(LOG_TAG + 'Shutting down message bot...')
        logging.debug(LOG_TAG + 'Done!\n')
