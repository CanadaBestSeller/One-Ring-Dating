#!/usr/bin/env python3

import json
import logging
import os
import socketserver
import sys

from urllib.request import urlretrieve

from heph_modules.face_extractor.face_extractor import FaceExtractor
from heph_modules.models.profile_rawtext import ProfileRawtext

# Configs
RESULT_FOLDER = "phase_1_pool/"
ESSENTIAL_FOLDERS = [RESULT_FOLDER + NAME for NAME in ['ids/', 'faces/', 'edges/', 'originals/']]
RESULT_EXTENSION = ".jpg"

# Logging
LOG_NAME = 'phase_1_face_extraction.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class FaceExtractorServer(socketserver.BaseRequestHandler):
    """
    Handles requests from inbound port.
    Request input must be a JSON of type ProfileRawtext (see import above)

    *** This server does several things ***
    1. Handles a request, given the platform, handle, and list of image links
    2. Retrieves every image, marks the faces, and also saves the faces separately for analysis
    3. Naming scheme of the processed pictures is the concatenation of the platform and handle

    *** Debugging Steps ***
    See debug_face_extractor_snippets.txt
    """

    # Contract
    def handle(self):
        self.data = self.request.recv(1024).strip()
        json_data = json.loads(self.data.decode())
        logging.info('[Server] Received request from {}:\n{}'.format(self.client_address[0], json.dumps(json_data, indent=4)))
        profile_rawtext = ProfileRawtext(**json_data)
        FaceExtractorServer.process_extraction_request(profile_rawtext)

    def setup(self): pass  # Contract

    def finish(self): pass  # Contract

    def close(self): pass  # Contract

    @staticmethod
    def process_extraction_request(profile_rawtext):

        logging.info('[Server] Processing request...\n')

        FaceExtractorServer.ensure_face_folders_exist()
        platform = profile_rawtext['platform']
        handle = profile_rawtext['handle']
        image_links = profile_rawtext['image_links']

        for index, image_link in enumerate(image_links):
            image_folder_path, image_filename = FaceExtractorServer.save_image(platform, handle, image_link, index)
            FaceExtractor.extract_face(image_folder_path, image_filename)

        logging.info('[Server] Request complete!\n\n')

    @staticmethod
    def save_image(platform, handle, image_link, index):
        open(RESULT_FOLDER + 'ids/' + platform + '-' + handle + '.id', 'a').close()
        image_filename = platform + '-' + handle + '-' + str(index+1) + RESULT_EXTENSION
        image_folder_path = RESULT_FOLDER + 'originals/'
        urlretrieve(image_link, image_folder_path + image_filename)
        logging.info('[Server] Image has been successfully downloaded and saved as {0}'.format(image_folder_path))
        return image_folder_path, image_filename

    @staticmethod
    def ensure_face_folders_exist():
        for folder_path in ESSENTIAL_FOLDERS:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)


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

    logging.info('[Server] Loggers successfully initialized.')


if __name__ == '__main__':
    serving_host, serving_port = sys.argv[1], int(sys.argv[2])
    initialize_logger()

    logging.info('\n'
                 '\n-----------------------------------'
                 '\nFace Extraction Server online!'
                 '\nServing requests @ {}:{}'
                 '\n-----------------------------------'
                 '\n'.format(serving_host, serving_port))

    server = socketserver.TCPServer((serving_host, serving_port), FaceExtractorServer)
    server.request_queue_size = 5
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('[Server] Shutting down server...')
        server.shutdown()
        logging.info('[Server] Done!\n')
