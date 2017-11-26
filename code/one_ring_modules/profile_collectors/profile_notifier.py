import logging
import json
import random
import socket
import sys
import time

from one_ring_modules.profile_collectors.okc.okc_profile_collector import OkcProfileCollector
from one_ring_modules.profile_collectors.tinder.tinder_profile_collector import TinderProfileCollector

# Logging
LOG_NAME = 'phase_0_collector.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s : %(message)s'


class ProfileNotifier:
    def __init__(self, destination_hostname, destination_port, notification_frequency, blacklist_folder_path, test_filepath=None):
        self.destination_hostname = destination_hostname
        self.destination_port = destination_port
        self.notification_frequency = notification_frequency

        # Collector implementations
        # TODO do this in a more elegant way - Profile collectors should always have a good session as a param
        self.profile_collectors = [
            OkcProfileCollector(blacklist_folder_path + '/phase_0_collector_okc.blacklist', test_filepath),
            TinderProfileCollector(blacklist_folder_path + '/phase_0_collector_tinder.blacklist'),
        ]

        logging.info('\n'
                     '\n============================================'
                     '\nProfile Notifier is running!'
                     '\n{0}'
                     '\n============================================'
                     '\n'.format('\n'.join([c.__repr__() + ' is online!' for c in self.profile_collectors])))

    def notify(self):
        profile_rawtext = random.choice(self.profile_collectors).collect_profile()
        logging.debug('[Notifier] Profile Collected! {0}'.format(profile_rawtext))
        try:
            destination = socket.socket()
            destination.connect((self.destination_hostname, int(self.destination_port)))
            destination.send(json.dumps(profile_rawtext).encode())
            destination.close()
        except ConnectionRefusedError:
            logging.error('[Notifier] Connection to {0}:{1} was refused!'.format(self.destination_hostname, self.destination_port))


def initialize_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(LOG_FORMAT)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler(LOG_NAME)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)

    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)

    logging.debug('[Notifier] Loggers successfully initialized.')


if __name__ == '__main__':

    dest_hostname = sys.argv[1]
    dest_port = sys.argv[2]
    notification_frequency = int(sys.argv[3])
    blacklist_folder_path = sys.argv[4]
    test_filepath = sys.argv[5] if len(sys.argv) > 5 else None

    initialize_logger()

    try:
        profile_notifier = ProfileNotifier(dest_hostname, dest_port, notification_frequency, blacklist_folder_path, test_filepath)
        while True:
            profile_notifier.notify()
            time.sleep(notification_frequency)
    except KeyboardInterrupt:
        logging.debug('[Notifier] Shutting down notifier...')
        logging.debug('[Notifier] Done!\n')
