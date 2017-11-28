#!/usr/bin/env python3

import logging


class MessageBot:

    def __init__(self, tag, id_provider, messenger, pic_retriever):
        self.tag = tag
        self.id_provider = id_provider
        self.messenger = messenger
        self.pic_retriever = pic_retriever

    def send_opener_to_all_matches(self, opener):
        messageable_ids = self.id_provider.get()
        logging.info('[{0} Message bot] {1} IDs are ready to be messaged'.format(self.tag, len(messageable_ids)))
        for index, id in enumerate(messageable_ids):
            logging.debug('[{0} Message Bot] Messaging ID {1} of {2} @ {3}...'.format(self.tag,
                                                                                      index,
                                                                                      len(messageable_ids),
                                                                                      id))
            message_success = self.messenger.send_opener(id, opener)
            if message_success:
                self.pic_retriever.save(id)

    def name(self):
        return self.tag + ' Message Bot'
