#!/usr/bin/env python3

import json
import logging
import socketserver
import sys
from urllib.request import urlretrieve

from one_ring_modules.face_extractor.extractors.haar_face_extractor import HaarFaceExtractor
from one_ring_modules.face_extractor.extractors.landmark_face_extractor import LandmarkFaceExtractor
from one_ring_modules.models.profile_rawtext import ProfileRawtext
from one_ring_modules.utils.file_utils import FileUtils

# Configs
ROOT_IMAGE_FOLDER = "phase_1_pool/"
RESULT_EXTENSION = ".jpg"

# Logging
LOG_NAME = 'phase_0_face_extractor.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_TAG = '[Face Extractor Server] '


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
        logging.debug(LOG_TAG + 'Received request from {}:\n{}'.format(self.client_address[0], json.dumps(json_data, indent=4)))
        profile_rawtext = ProfileRawtext(**json_data)
        FaceExtractorServer.process_extraction_request(profile_rawtext)

    def setup(self): pass  # Contract

    def finish(self): pass  # Contract

    def close(self): pass  # Contract

    @staticmethod
    def process_extraction_request(profile_rawtext):
        logging.debug(LOG_TAG + 'Processing request...\n')
        platform = profile_rawtext['platform']
        handle = profile_rawtext['handle']
        image_links = profile_rawtext['image_links']
        FileUtils.create_folder_if_not_exists(ROOT_IMAGE_FOLDER)

        for index, image_link in enumerate(image_links):
            image_filepath, image_filename = FaceExtractorServer.save_image(platform, handle, image_link, index)
            HaarFaceExtractor.extract_face(image_filepath, ROOT_IMAGE_FOLDER, "haar_", image_filename)
            # LandmarkFaceExtractor.extract_face(image_filepath, ROOT_IMAGE_FOLDER, "landmark_", image_filename)

        logging.debug('[Face Extractor Server] Request complete!\n\n')

    @staticmethod
    def save_image(platform, handle, image_link, index):
        id_folder = ROOT_IMAGE_FOLDER + 'ids/'
        FileUtils.create_folder_if_not_exists(id_folder)
        open(id_folder + platform + '-' + handle + '.id', 'a').close()

        image_filename = platform + '-' + handle + '-' + str(index+1) + RESULT_EXTENSION

        originals_folder = ROOT_IMAGE_FOLDER + 'originals/'
        FileUtils.create_folder_if_not_exists(originals_folder)
        image_filepath = originals_folder + image_filename
        urlretrieve(image_link, image_filepath)
        logging.debug(LOG_TAG + 'Image has been successfully downloaded and saved as {0}'.format(image_filepath))
        return image_filepath, image_filename


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

    logging.debug(LOG_TAG + 'Loggers successfully initialized.')


if __name__ == '__main__':
    serving_host = sys.argv[1]
    serving_port = int(sys.argv[2])

    initialize_logger()

    logging.debug('\n'
                  '\n-----------------------------------'
                  '\nFace Extractor Server online!'
                  '\nServing requests @ {}:{}'
                  '\n-----------------------------------'
                  '\n'.format(serving_host, serving_port))

    server = socketserver.TCPServer((serving_host, serving_port), FaceExtractorServer)
    server.request_queue_size = 5
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.debug(LOG_TAG + 'Shutting down server...')
        server.shutdown()
        logging.debug(LOG_TAG + 'Done!\n')
