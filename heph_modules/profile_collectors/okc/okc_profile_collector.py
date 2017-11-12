#!/usr/bin/env python3

import logging

from heph_modules.models.profile_rawtext import ProfileRawtext


class OkcProfileCollector:
    """
    TODO - Create more strict contract for collect_profile(blacklist=None) implementation
    """
    @staticmethod
    def collect_profile(blacklist=None):
        image_links = [
            'https://i.pinimg.com/736x/8a/0d/a8/8a0da86c832393adfbcf9537cf328549--brown-hair-colors-dark-brown-color.jpg',
            'http://zntent.com/wp-content/uploads/2014/11/alison-brie-04.jpg',
            'https://surgeryvip.com/wp-content/uploads/2015/05/Alison-Brie.jpg',
            'http://static1.refinery29.com/bin/entry/2dc/x,80/1147896/alison-brie-community2.jpg',
            'https://friskyforks.com/wp-content/uploads/2017/02/brie-cheese.jpg'
        ]
        profile = ProfileRawtext('okc', 'alison-brie', image_links)
        logging.info('[OKC Profile Collector] Collected profile via QuickMatch')
        return profile
    #
    # @staticmethod
    # def quickmatch():
