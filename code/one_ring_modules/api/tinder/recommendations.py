#!/usr/bin/env python3
# coding=utf-8

import logging

from one_ring_modules.api.tinder.session import Session

LOG_TAG = '[Tinder Profile Collector] '


class Recommendations:

    @classmethod
    def from_session(cls, session):
        return cls(session)

    @classmethod
    def from_credentials(cls, email, password):
        session = Session.log_in()
        return cls(session)

    def __init__(self, session):
        self.session = session
        self.recommendations = []

    def refresh_recommendations(self):
        logging.debug(LOG_TAG + 'Caching Tinder recommendations...')
        rawtext_dict_recommendations = self.session.get_recommendations()
        self.recommendations = [Recommendation.from_dict(d) for d in rawtext_dict_recommendations]
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
    | d['_id']
    | d['bio']
    | d['birth_date_info']
    | d['birth_date']
    | d['common_friend_count']
    | d['common_friends']
    | d['common_like_count']
    | d['common_likes']
    | d['connection_count']
    | d['content_hash']
    | d['distance_mi']
    | d['gender']
    | d['group_matched']
    | d['instagram']
    | d['jobs']
    | d['name']
    | d['photos']
    | d['ping_time']
    | d['s_number']
    | d['schools']
    | d['spotify_theme_track']
    | d['spotify_top_artists']
    | d['teaser']
    | d['teasers']
    |
    | """

    @classmethod
    def from_dict(cls, rawtext_json_dict):
        return cls(rawtext_json_dict)

    def __init__(self, d):
        self.id = d['_id']
        self.name = d['name']
        self.photo_links = [photo['url'] for photo in d['photos']]
        self.distance_in_miles = d['distance_mi']
        self.bio = d['bio']

    def __repr__(self):
        return '<{0} ({1}). {2} miles away. Photos: {3}>'.format(self.name,
                                                                 self.id,
                                                                 self.distance_in_miles,
                                                                 len(self.photo_links))
