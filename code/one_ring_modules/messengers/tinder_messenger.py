#!/usr/bin/env python3


class TinderMessenger(object):

    @classmethod
    def from_session(cls, session):
        return cls(session)

    def __init__(self, session):
        self.session = session

    def send_message(self, message):
        pass  #TODO Return boolean indicating success/failure
