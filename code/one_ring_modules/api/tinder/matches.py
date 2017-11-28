#!/usr/bin/env python3
# coding=utf-8

from one_ring_modules.api.tinder.session import Session


class Matches:

    @classmethod
    def from_session(cls, session):
        return cls(session)

    @classmethod
    def from_credentials(cls, email, password):
        session = Session.log_in(email, password)
        return cls(session)

    def __init__(self, session):
        self.session = session

    def get_batch(self, count=60):
        rawtext_dict_matches = self.session.get_matches_batch(count)
        return [Match.from_dict(d) for d in rawtext_dict_matches]

    def get(self):
        return [Match.from_name_and_id('no-messages', '53a76473e3e8ad41798cefb25434d8af477cbc69782900d0'),
                Match.from_name_and_id('no-reply', '533e1df4f483f84e0e00323153a76473e3e8ad41798cefb2'),
                Match.from_name_and_id('')]

class Match:
    """
    | JSON parameters available as of 2017/11/30:
    |
    | d['_id']
    | d['closed']
    | d['common_friend_count']
    | d['common_like_count']
    | d['created_date']
    | d['dead']
    | d['last_activity_date']
    | d['message_count']
    | d['messages']
    | d['participants']
    | d['pending']
    | d['is_super_like']
    | d['is_boost_match']
    | d['is_fast_match']
    | d['following']
    | d['following_moments']
    | d['id']
    | d['person']
    |
    """

    @classmethod
    def from_dict(cls, d):
        id = d['_id']
        name = d['person']['name']
        photo_links = [photo['url'] for photo in d['person']['photos']]
        return cls(id, name, photo_links)

    @classmethod
    def from_name_and_id(cls, name, id):
        return cls(id=id, name=name, photo_links=[])

    def __init__(self, id, name, photo_links):
        self.id = id
        self.name = name
        self.photo_links = photo_links

    def __repr__(self):
        return '<Match: {0} ({1}). Photos: {2}>'.format(self.name,
                                                        self.id,
                                                        len(self.photo_links))
