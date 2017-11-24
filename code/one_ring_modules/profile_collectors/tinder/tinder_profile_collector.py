#!/usr/bin/env python3

import logging

from one_ring_modules.api.tinder.recommendations import Recommendations
from one_ring_modules.models.profile_rawtext import ProfileRawtext
from one_ring_modules.utils.file_utils import FileUtils

LOG_TAG = '[Tinder Profile Collector] '


class TinderProfileCollector:

    def __init__(self, blacklist_filepath):
        self.blacklist_filepath = blacklist_filepath
        self.recommendations = Recommendations.from_session()

    def collect_profile(self):
        recommendation = self.recommendations.get()

        if recommendation.id in FileUtils.parse_lines(self.blacklist_filepath):
            logging.warning(LOG_TAG + 'User is already processed! Skipping {0} ({1})'.format(recommendation.name, recommendation.id))
            return self.collect_profile()

        FileUtils.add_line_to_file(self.blacklist_filepath, recommendation.id)

        # TODO extract platform tag, so that it is specified by the server (caller) as input to __init__()
        return ProfileRawtext(platform='tinder',
                              user_id=recommendation.id,
                              name=recommendation.name,
                              image_links=recommendation.photo_links)

    def __repr__(self):
        return 'Tinder Profile Collector'
