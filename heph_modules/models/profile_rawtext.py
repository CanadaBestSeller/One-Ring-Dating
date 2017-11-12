#!/usr/bin/env python3


class ProfileRawtext(dict):
    """
    Easy de/serialization because we're inheriting from dictionary. Works nicely with Python's json module:
    serialized_profile = json.dumps(ProfileRawtext('a', 'b'))
    deserialized_profile = ProfileRawtext(**(json.loads(serialized_profile))
    """
    def __init__(self, platform, handle, image_links):
        dict.__init__(self, platform=platform)
        dict.__init__(self, handle=handle)
        dict.__init__(self, image_links=image_links)

    def __repr__(self):
        return '<ProfileRawtext: {0} @ {1}. len(image_links)={2}>'.format(self['handle'], self['platform'], len(self['image_links']))
