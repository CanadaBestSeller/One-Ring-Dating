#!/usr/bin/env python3

import logging
import random
import time

import requests

from one_ring_modules.auth.tinder.tinder_session import TinderSession
from one_ring_modules.auth.tinder.tinder_session import AuthenticationError
from one_ring_modules.models.profile_rawtext import ProfileRawtext
from one_ring_modules.utils.file_utils import FileUtils

from requests.exceptions import HTTPError

LOG_TAG = '[Tinder Profile Collector] '


class TinderProfileCollector:

    def __init__(self, blacklist_filepath, test_filepath=None):
        logging.warning(LOG_TAG + 'Logging in now. This should happen very rarely.')
        self.blacklist_filepath = blacklist_filepath
        self.recommendations_list = []  # TODO User a generator to make this cache list logic thread-safe

    def collect_profile(self, blacklist_folder_path):
        time.sleep(1)

        try:
            match_handle = self.collect_handle() if self.test_filepath is None else self.mock_collect_handle()
            logging.info(LOG_TAG + 'Quickmatch found! Handle = {0}'.format(match_handle))
        except AuthenticationError:
            logging.warning(LOG_TAG + 'Encountered authentication error. Attempting to re-log')
            self.session = TinderSession.login()
            return self.collect_profile(blacklist_folder_path)

        if match_handle in FileUtils.parse_lines(self.blacklist_filepath):
            logging.warning(LOG_TAG + 'Quickmatch is in blacklist! Skipping user "{0}"'.format(match_handle))
            return self.collect_profile(blacklist_folder_path)

        try:
            image_links = self.get_okc_image_links(match_handle)
        except HTTPError:
            logging.warning(
                LOG_TAG + 'Encountered HTTP error while collecting user ID {0}. Re-trying.'.format(match_handle))
            return self.collect_profile(blacklist_folder_path)

        FileUtils.add_line_to_file(self.blacklist_filepath, match_handle)

        # TODO extract platform tag, so that it is specified by the server (caller) as input to __init__()
        return ProfileRawtext('tinder', match_handle, image_links)

    def collect_handle(self):
        if len(self.recommendations_list) is 0:
            recs = self.get_recommendations()
            self.recommendations_list = recs
            logging.info(LOG_TAG + 'Got {0} recommendations from Tinder!\n{1}'.format(len(recs), recs))
        return self.recommendations_list.pop()

    def mock_collect_handle(self):
        handle = random.choice(FileUtils.parse_lines(self.test_filepath))
        logging.info(LOG_TAG + 'MOCKING recommendation. Recommendation user ID: {0}'.format(handle))
        return handle

