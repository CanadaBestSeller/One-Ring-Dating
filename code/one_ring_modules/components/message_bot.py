#!/usr/bin/env python3

import logging


class MessageBot:

    def __init__(self, tag, inbox_match_provider, messenger):
        self.tag = tag
        self.inbox_match_provider = inbox_match_provider
        self.messenger = messenger

    def send_opener_to_all_inbox_matches(self, opener):
        all_inbox_matches = self.inbox_match_provider.get_all_matches_in_inbox()
        logging.info('[{0} Message bot] {1} IDs are ready to be messaged'.format(self.tag, len(all_inbox_matches)))
        for index, match in enumerate(all_inbox_matches):
            logging.debug('[{0} Message Bot] Messaging ID {1} of {2} @ {3}...'.format(self.tag,
                                                                                      index,
                                                                                      len(all_inbox_matches),
                                                                                      match.id))
            message_success = self.messenger.send_opener(id, opener)
            if message_success:
                logging.debug('[{0} Message Bot] Message successful!')
            else:
                logging.debug('[{0} Message Bot] Message failed!')

    def name(self):
        return self.tag + ' Message Bot'
