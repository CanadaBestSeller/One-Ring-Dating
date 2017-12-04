#!/usr/bin/env python3
# coding=utf-8

from one_ring_modules.utils.file_utils import FileUtils


class LocalFileMatches:

    @classmethod
    def from_local_file(cls, filepath):
        return cls([Match.from_name_and_id('undef', line.strip()) for line in FileUtils.parse_lines(filepath)])

    @classmethod
    def from_mock_data(cls):
        matches = [Match.from_name_and_id('no-messages', 'LiteraryChic7'),
                   Match.from_name_and_id('no-reply', 'Meadowanne19'),
                   Match.from_name_and_id('she-replied', 'AlwaysHasABook')]
        return cls(matches)

    def __init__(self, matches):
        self.matches = matches

    def get_all_matches_in_inbox(self):
        return self.matches


class Match:

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
