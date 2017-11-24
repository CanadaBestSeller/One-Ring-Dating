#!/usr/bin/env python3

import logging
import random
import re
import time

from one_ring_modules.models.profile_rawtext import ProfileRawtext
from one_ring_modules.api.okc.session import Session as OkcSession
from one_ring_modules.api.okc.session import AuthenticationError

from requests.exceptions import HTTPError

from one_ring_modules.utils.xpath import xpb
from one_ring_modules.utils.file_utils import FileUtils

from lxml import html

LOG_TAG = '[OKC Profile Collector] '


class OkcProfileCollector:

    def __init__(self, blacklist_filepath, test_filepath=None):
        logging.warning(LOG_TAG + 'Logging in now. This should happen very rarely.')
        self.session = OkcSession.login()
        self.test_filepath = test_filepath
        self.blacklist_filepath = blacklist_filepath

    def collect_profile(self):
        time.sleep(1)

        try:
            match_handle = self.collect_handle() if self.test_filepath is None else self.mock_collect_handle()
            logging.info(LOG_TAG + 'Quickmatch found! Handle = {0}'.format(match_handle))
        except AuthenticationError:
            logging.warning(LOG_TAG + 'Encountered authentication error. Attempting to re-log')
            self.session = OkcSession.login()
            return self.collect_profile()

        if match_handle in FileUtils.parse_lines(self.blacklist_filepath):
            logging.warning(LOG_TAG + 'Quickmatch already processed! Skipping user "{0}"'.format(match_handle))
            return self.collect_profile()

        try:
            image_links = self.get_okc_image_links(match_handle)
        except HTTPError:
            logging.warning(LOG_TAG + 'Encountered HTTP error while collecting user ID {0}. Re-trying.'.format(match_handle))
            return self.collect_profile()

        FileUtils.add_line_to_file(self.blacklist_filepath, match_handle)

        # TODO extract platform tag, so that it is specified by the server (caller) as input to __init__()
        return ProfileRawtext(platform='okc',
                              user_id=match_handle,
                              name=None,
                              image_links=image_links)

    def collect_handle(self):
        match = self.session.quickmatch()
        return match.username

    def mock_collect_handle(self):
        mock_handles = FileUtils.parse_lines(self.test_filepath)
        if len(mock_handles) is 0:
            logging.error(LOG_TAG + 'Attempting to mock quickmatch but there is no mock input! Falling back to real collect')
            return self.collect_handle()
        else:
            handle = random.choice(mock_handles)
            logging.info(LOG_TAG + 'MOCKING quickmatch. Mocked handle: {0}'.format(handle))
            return handle

    def get_okc_image_links(self, handle):
        pics_request = self.session.okc_get(
            u'profile/{0}/album/0'.format(handle),
        )
        pics_tree = html.fromstring(u'{0}{1}{2}'.format(
            u'<div>', pics_request.json()['fulls'], u'</div>'
        ))
        photo_info_xpb = xpb.div.with_class('photo').img.select_attribute_('src')
        return [OkcProfileCollector.get_okc_image_link(uri) for uri in photo_info_xpb.apply_(pics_tree)]

    def __repr__(self):
        return 'OkCupid Profile Collector'

    @staticmethod
    def get_okc_image_link(uri):
        base_uri = "https://k0.okccdn.com/php/load_okc_image.php/images/"
        okc_uri_re = re.compile("http(?P<was_secure>s?)://.*okccdn.com.*images/"
                                "[0-9]*x[0-9]*/[0-9]*x[0-9]*/"
                                "(?P<tnl>[0-9]*?)x(?P<tnt>[0-9]*?)/"
                                "(?P<tnr>[0-9]*)x(?P<tnb>[0-9]*)/0/"
                                "(?P<id>[0-9]*).(:?webp|jpeg)\?v=\d+")
        match = okc_uri_re.match(uri)
        return base_uri + match.group('id') + '.png'
