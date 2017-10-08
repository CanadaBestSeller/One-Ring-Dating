#!/usr/bin/env python3

import json
import logging
import os
import sys
import socketserver

from urllib.request import urlretrieve
from modules.face_extractor.face_extractor import FaceExtractor

# Face extraction
RESULT_FOLDER = "phase_1_selection/"

# Logging
LOG_NAME = 'face_extractor.log'
LOG_FORMAT = '[FACE_EXTRACTOR] %(asctime)s - %(name)s - %(levelname)s - %(message)s'


class FaceExtractorServer(socketserver.BaseRequestHandler):
    """
    Handles requests from inbound port.
    Request must be a JSON of type FaceExtractionRequest (see below this class)

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
        logging.info('Received request from {}:\n{}'.format(self.client_address[0], json.dumps(json_data, indent=4)))
        face_extraction_request = FaceExtractionRequest(**json_data)
        FaceExtractorServer.process(face_extraction_request)

    def setup(self): pass  # Contract

    def finish(self): pass  # Contract

    def close(self): pass  # Contract

    @staticmethod
    def process(face_extraction_request):
        platform = face_extraction_request['platform']
        handle = face_extraction_request['handle']
        image_links = face_extraction_request['image_links']

        for index, image_link in enumerate(image_links):
            image_filepath = FaceExtractorServer.save_image(platform, handle, image_link, index, RESULT_FOLDER)
            FaceExtractor.extract_face(image_filepath)

    @staticmethod
    def save_image(platform, handle, image_link, index, destination):
        extension = os.path.splitext(image_link)[1]
        image_filename = platform + '-' + handle + '-' + str(index+1) + extension
        image_filepath = RESULT_FOLDER + image_filename
        urlretrieve(image_link, image_filepath)
        logging.info("Image has been successfully downloaded and saved as {0}".format(image_filepath))
        return image_filepath


class FaceExtractionRequest(dict):
    """
    Easy de/serialization because we're inheriting from dictionary. Works nicely with Python's json module:
    serialized_request = json.dumps(FaceExtractionRequest('a', 'b'))
    deserialized_request = FaceExtractionRequest(**(json.loads(serialized_request))
    """
    def __init__(self, platform, handle, image_links):
        dict.__init__(self, platform=platform)
        dict.__init__(self, handle=handle)
        dict.__init__(self, image_links=image_links)


def main():
    print("LOL")


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

    logging.info("Loggers successfully initialized.")


if __name__ == '__main__':
    serving_host, serving_port = sys.argv[1], int(sys.argv[2])
    initialize_logger()

    logging.info("Serving requests @ {}:{}".format(serving_host, serving_port))
    while True:
        server = socketserver.TCPServer((serving_host, serving_port), FaceExtractorServer)
        server.request_queue_size = 5
        server.serve_forever()
