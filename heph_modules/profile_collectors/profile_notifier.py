import logging
import json
import socket
import sys
import time

from heph_modules.profile_collectors.okc.okc_profile_collector import OkcProfileCollector

# Logging
LOG_NAME = 'heph_modules/profile_collectors/profile_collection.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class ProfileNotifier:
    def __init__(self, destination_hostname, destination_port, notification_frequency):
        self.destination_hostname = destination_hostname
        self.destination_port = destination_port
        self.notification_frequency = notification_frequency

    def notify(self):
        profile_rawtext = OkcProfileCollector.collect_profile()  # TODO remove OKC and generify this line via an attachment pattern
        logging.info('[Notifier] Profile Collected! {0}'.format(profile_rawtext))
        destination = socket.socket()
        destination.connect((self.destination_hostname, int(self.destination_port)))
        destination.send(json.dumps(profile_rawtext).encode())


def initialize_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(LOG_FORMAT)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler(LOG_NAME)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)

    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)

    logging.info('[Notifier] Loggers successfully initialized.')


if __name__ == '__main__':
    destination_hostname, destination_port, notification_frequency = sys.argv[1], sys.argv[2], int(sys.argv[3])

    initialize_logger()

    logging.info('\n'
                 '\n----------------------------'
                 '\nProfile Notifier is running!'
                 '\n----------------------------'
                 '\n')
    try:
        while True:
            profile_notifier = ProfileNotifier(destination_hostname, destination_port, notification_frequency)
            profile_notifier.notify()
            time.sleep(notification_frequency)
    except KeyboardInterrupt:
        logging.info('[Notifier] Shutting down notifier...')
        logging.info('[Notifier] Done!\n')