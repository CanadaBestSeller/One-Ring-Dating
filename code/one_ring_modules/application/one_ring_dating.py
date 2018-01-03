#!/usr/bin/env python3

import logging, os, sys, time

import getpass
import threading
import socketserver

from one_ring_modules.layer_api.okc_api import InvalidCredentialsException
from one_ring_modules.layer_api.tinder_api import TinderApi
from one_ring_modules.layer_api.okc_api import OkcApi

from one_ring_modules.application.face_extractor_server import FaceExtractorServer

# Application
APPLICATION_PORT = 26673
APPLICATION_HOST = 'localhost'

# Logging
LOG_TAG = '[One Ring Dating] '
LOG_NAME = 'application.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s : %(message)s'


class OneRingDating:
    def __init__(self, tinder_api, okc_api):
        self.tinder_api = tinder_api
        self.okc_api = okc_api
        self.face_extractor_server = OneRingDating.initialize_face_extractor_server()

    def start_face_extractor_server_async(self):
        threading.Thread(target=self.face_extractor_server.serve_forever).start()

    def stop_face_extractor_server(self):
        logging.info(LOG_TAG + 'Shutting down server...')
        self.face_extractor_server.shutdown()
        logging.info(LOG_TAG + 'Done!\n')

    @staticmethod
    def initialize_face_extractor_server():
        logging.info('\n'
                     '\n-----------------------------------'
                     '\nFace Extractor Server online!'
                     '\nServing requests @ {}:{}'
                     '\n-----------------------------------'
                     '\n'.format(APPLICATION_HOST, APPLICATION_PORT))

        server = socketserver.TCPServer((APPLICATION_HOST, APPLICATION_PORT), FaceExtractorServer)
        server.request_queue_size = 5
        return server


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

    logging.debug(LOG_TAG + 'Application logger successfully initialized.')


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_tinder_api_from_input():
    fb_email_input = input('Please enter your FB email, leave blank and press enter to skip: ')
    if fb_email_input is '':
        return None
    else:
        fb_password_input = getpass.getpass('Please enter your FB password (input is hidden): ')
        try:
            tinder_api = TinderApi.log_in(fb_email_input, fb_password_input)
            return tinder_api
        except InvalidCredentialsException:
            print('Invalid credentials, please try again')
            get_tinder_api_from_input()


def get_okc_api_from_input():
    okc_email_input = input('Please enter your OKC username, leave blank and press enter to skip: ')
    if okc_email_input is '':
        return None
    else:
        okc_password_input = getpass.getpass('Please enter your OKC password (input is hidden): ')
        try:
            okc_api = OkcApi.log_in(okc_email_input, okc_password_input)
            return okc_api
        except InvalidCredentialsException:
            print('Invalid credentials, please try again')
            get_okc_api_from_input()


if __name__ == '__main__':

    initialize_logger()

    FB_EMAIL = os.environ.get('ONE_RING_FB_EMAIL')
    FB_PASSWORD = os.environ.get('ONE_RING_FB_PASSWORD')
    OKC_USERNAME = os.environ.get('ONE_RING_OKC_USERNAME')
    OKC_PASSWORD = os.environ.get('ONE_RING_OKC_PASSWORD')

    clear_screen()
    tinder_api = get_tinder_api_from_input() if FB_EMAIL is None else TinderApi.log_in(FB_EMAIL, FB_PASSWORD)

    clear_screen()
    okc_api = get_okc_api_from_input() if OKC_USERNAME is None else OkcApi.log_in(OKC_USERNAME, OKC_PASSWORD)

    application = OneRingDating(tinder_api=tinder_api, okc_api=okc_api)
    application.start_face_extractor_server_async()

    counter = 1
    try:
        while counter > 0:
            logging.info(LOG_TAG + 'INSIDE MAIN THREAD... @ ' + str(counter))
            time.sleep(1)
            counter += 1
    except KeyboardInterrupt:
        application.stop_face_extractor_server()
