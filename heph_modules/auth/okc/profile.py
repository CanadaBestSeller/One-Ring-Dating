#!/usr/bin/env python3

import logging
from utils import cached_property


class Profile(object):
    """Represent the profile of an okcupid user.

    Many of the attributes on this object are
    :class:`~okcupyd.util.cached_property` instances which lazily load their
    values, and cache them once they have been accessed. This makes it so
    that this object avoids making unnecessary HTTP requests to retrieve the
    same piece of information twice.

    Because of this caching behavior, care must
    be taken to invalidate cached attributes on the object if an up to date view
    of the profile is needed. It is recommended that you call :meth:`.refresh`
    to accomplish this, but it is also possible to use
    :meth:`~okcupyd.util.cached_property.bust_self` to bust individual
    properties if necessary.
    """

    def __init__(self, session, username, **kwargs):
        self._session = session
        self.username = username

        if kwargs:
            self._set_cached_properties(kwargs)

    def _set_cached_properties(self, values):
        property_names = set(name for name, _ in cached_property.get_cached_properties(self))
        for key, value in values.items():
            if key not in property_names:
                logging.warning("Unrecognized kwarg {0} with value {1} passed to Profile constructor.")
            self.__dict__[key] = value
