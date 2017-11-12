import logging
import sys
import time

# Logging
LOG_NAME = 'profile_collection.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class ProfileNotifier:
    @staticmethod
    def notify():
        logging.info('[Notifier] This is a MOCK NOTIFICATION!')


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
    initialize_logger()

    logging.info('\n'
                 '\n----------------------------'
                 '\nProfile Notifier is running!'
                 '\n----------------------------'
                 '\n')
    try:
        while True:
            ProfileNotifier.notify()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('[Notifier] Shutting down notifier...')
        logging.info('[Notifier] Done!\n')