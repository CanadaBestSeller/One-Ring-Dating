#!/usr/bin/env python3
# coding=utf-8

import logging
import time

from one_ring_modules.api.tinder.session import Session, AuthenticationError

LOG_TAG = '[Tinder Profile Collector] '


class Recommendations:

    @classmethod
    def from_session(cls):
        session = Session.log_in()
        return cls(session)

    def __init__(self, session):
        self.session = session
        self.recommendations = []

    def refresh_recommendations(self):
        logging.debug(LOG_TAG + 'Caching Tinder recommendations...')
        try:
            rawtext_dict_recommendations = self.session.get_recommendations()
            self.recommendations = [Recommendation.from_dict(d) for d in rawtext_dict_recommendations]
        except AuthenticationError:
            logging.debug(LOG_TAG + 'Session expired. Getting a new session.')
            time.sleep(1)
            self.session = Session.log_in()
            logging.debug(LOG_TAG + 'New Session retrieval success.')

        logging.info(LOG_TAG + 'Cached recommendations for {0} users.'.format(len(self.recommendations)))

    def get(self):
        if len(self.recommendations) is 0:
            self.refresh_recommendations()
        recommendation = self.recommendations.pop()
        logging.info(LOG_TAG + 'GET success! {0}'.format(recommendation.__repr__()))
        return recommendation


class Recommendation:
    """
    | JSON parameters available as of 2017/11/30:
    |
    | r['_id']
    | r['bio']
    | r['birth_date_info']
    | r['birth_date']
    | r['common_friend_count']
    | r['common_friends']
    | r['common_like_count']
    | r['common_likes']
    | r['connection_count']
    | r['content_hash']
    | r['distance_mi']
    | r['gender']
    | r['group_matched']
    | r['instagram']
    | r['jobs']
    | r['name']
    | r['photos']
    | r['ping_time']
    | r['s_number']
    | r['schools']
    | r['spotify_theme_track']
    | r['spotify_top_artists']
    | r['teaser']
    | r['teasers']
    | """

    @classmethod
    def from_dict(cls, rawtext_dict_json):
        return cls(rawtext_dict_json)

    def __init__(self, r):
        self.id = r['_id']
        self.name = r['name']
        self.photo_links = [photo['url'] for photo in r['photos']]
        self.distance_in_miles = r['distance_mi']
        self.bio = r['bio']

    def __repr__(self):
        return '<{0} ({1}). {2} miles away. Photos: {3}>'.format(self.name,
                                                                 self.id,
                                                                 self.distance_in_miles,
                                                                 len(self.photo_links))
