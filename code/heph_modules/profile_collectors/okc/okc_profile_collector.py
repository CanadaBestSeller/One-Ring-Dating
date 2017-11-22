#!/usr/bin/env python3

import logging
import re
import time

from heph_modules.models.profile_rawtext import ProfileRawtext
from heph_modules.auth.okc.session import Session as OkcSession
from heph_modules.auth.okc.session import AuthenticationError

from heph_modules.utils.xpath import xpb
from heph_modules.utils.file_utils import FileUtils as Blacklist

from lxml import html


class OkcProfileCollector:

    def __init__(self):
        self.session = OkcSession.login()

    def collect_profile(self, blacklist_folder_path):
        time.sleep(1)
        blacklist_filepath = blacklist_folder_path + '/phase_1_collector_okc.blacklist'
        try:
            match_handle = self.quickmatch()
            logging.info('[OKC Profile Collector] Quickmatch found! Handle = {0}'.format(match_handle))

            if match_handle in Blacklist.parse_lines(blacklist_filepath):
                logging.warn('[OKC Profile Collector] Quickmatch is in blacklist! Skipping user "{0}"'.format(match_handle))
                return self.collect_profile(blacklist_folder_path)

            image_links = self.get_okc_image_links(match_handle)
            Blacklist.add_line_to_file(blacklist_filepath, match_handle)
            return ProfileRawtext('okc', match_handle, image_links)  # TODO extract platform tag
        except AuthenticationError:
            self.session = OkcSession.login()
            return self.collect_profile(blacklist_folder_path)

    def quickmatch(self):
        match = self.session.quickmatch()
        return match.username

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
