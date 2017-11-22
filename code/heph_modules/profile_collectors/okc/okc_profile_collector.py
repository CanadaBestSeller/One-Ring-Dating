#!/usr/bin/env python3

import logging
import random
import re
import time

from heph_modules.models.profile_rawtext import ProfileRawtext
from heph_modules.auth.okc.session import Session as OkcSession
from heph_modules.auth.okc.session import AuthenticationError

from requests.exceptions import HTTPError

from heph_modules.utils.xpath import xpb
from heph_modules.utils.file_utils import FileUtils

from lxml import html


class OkcProfileCollector:

    def __init__(self, test_filepath=None):
        logging.warn('[OKC Profile Collector] Logging in now. This should happen very rarely.')
        self.session = OkcSession.login()
        self.test_filepath = test_filepath

    def collect_profile(self, blacklist_folder_path):
        time.sleep(1)
        blacklist_filepath = blacklist_folder_path + '/phase_0_collector_okc.blacklist'

        try:
            match_handle = self.collect_handle() if self.test_filepath is None else self.mock_collect_handle()
            logging.info('[OKC Profile Collector] Quickmatch found! Handle = {0}'.format(match_handle))
        except AuthenticationError:
            logging.warn('[OKC Profile Collector] Encountered authentication error. Attempting to re-log')
            self.session = OkcSession.login()
            return self.collect_profile(blacklist_folder_path)

        if match_handle in FileUtils.parse_lines(blacklist_filepath):
            logging.warn('[OKC Profile Collector] Quickmatch is in blacklist! Skipping user "{0}"'.format(match_handle))
            return self.collect_profile(blacklist_folder_path)

        try:
            image_links = self.get_okc_image_links(match_handle)
        except HTTPError:
            logging.warn('[OKC Profile Collector] Encountered HTTP error while collecting user ID {0}. Re-trying.'.format(match_handle))
            return self.collect_profile(blacklist_folder_path)

        FileUtils.add_line_to_file(blacklist_filepath, match_handle)
        return ProfileRawtext('okc', match_handle, image_links)  # TODO extract platform tag

    def collect_handle(self):
        match = self.session.quickmatch()
        return match.username

    def mock_collect_handle(self):
        handle = random.choice(FileUtils.parse_lines(self.test_filepath))
        logging.info('[OKC Profile Collector] MOCKING quickmatch. Mocked handle: {0}'.format(handle))
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
