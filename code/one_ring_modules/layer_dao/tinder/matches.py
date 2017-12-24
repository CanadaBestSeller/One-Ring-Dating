#!/usr/bin/env python3
# coding=utf-8

from one_ring_modules.layer_api.tinder_api import TinderApi


class Matches:

    @classmethod
    def from_api(cls, api):
        return cls(api)

    @classmethod
    def from_credentials(cls, email, password):
        api = TinderApi.log_in(email, password)
        return cls(api)

    def __init__(self, api):
        self.api = api

    # We are throttled @ 20 matches.
    # TODO: collect paginated matches to get ALL inbox matches OR systematically remove no-reply matches
    def get_all_in_inbox(self, count=20):
        rawtext_dict_matches = self.api.get_matches_batch(count)
        return [Match.from_dict(d) for d in rawtext_dict_matches]


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
        match_id = d['_id']
        name = d['person']['name']
        photo_links = [photo['url'] for photo in d['person']['photos']]
        is_empty_conversation = len(d['messages']) is 0
        return cls(match_id, name, photo_links, is_empty_conversation)

    @classmethod
    def from_name_and_id(cls, name, match_id, is_empty_conversation):
        return cls(match_id=match_id, name=name, photo_links=[], is_empty_conversation=is_empty_conversation)

    def __init__(self, match_id, name, photo_links, is_empty_conversation):
        self.match_id = match_id
        self.name = name
        self.photo_links = photo_links
        self.is_empty_conversation = is_empty_conversation

    def __repr__(self):
        return '<Match: {0} ({1}). Photos: {2}>'.format(self.name,
                                                        self.id,
                                                        len(self.photo_links))
