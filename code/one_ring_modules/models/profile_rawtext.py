#!/usr/bin/env python3


class ProfileRawtext(dict):
    """
    |  Easy de/serialization because we're inheriting from dictionary. Works nicely with Python's json module
    |  Example:
    |  serialized_profile = json.dumps(ProfileRawtext('a', 'b'))
    |  deserialized_profile = ProfileRawtext(**(json.loads(serialized_profile))
    """
    def __init__(self, platform, user_id, name, image_links):
        dict.__init__(self, platform=platform)
        dict.__init__(self, user_id=user_id)
        dict.__init__(self, name=name)
        dict.__init__(self, image_links=image_links)

    def __repr__(self):
        return '<ProfileRawtext: {0} ({1}) @ {2}. len(image_links)={3}>'.format(self['name'] if self['name'] else self['user_id'],
                                                                                self['user_id'],
                                                                                self['platform'],
                                                                                len(self['image_links']))
