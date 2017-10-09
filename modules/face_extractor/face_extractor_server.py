#!/usr/bin/env python3

import json
import logging
import os
import socketserver
import sys
from urllib.request import urlretrieve

import cv2


# Configs
RESULT_FOLDER = "phase_1_selection/"
CASCADE_PATH = os.path.abspath("modules/face_extractor/haarcascade_frontalface_default.xml")
RESULT_EXTENSION = ".jpg"
FACE_SIZE = (100, 100)
RESIZE_TOP_PIXELS = 300

# Logging
LOG_NAME = 'face_extractor.log'
LOG_FORMAT = '[FACE_EXTRACTOR_SERVER] %(asctime)s - %(name)s - %(levelname)s - %(message)s'


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
            image_filepath = FaceExtractorServer.save_image(platform, handle, image_link, index)
            FaceExtractor.extract_face(image_filepath)

    @staticmethod
    def save_image(platform, handle, image_link, index):
        extension = os.path.splitext(image_link)[1]
        open(RESULT_FOLDER + platform + '-' + handle + '.id', 'a').close()
        image_filename = str(index+1) + '---' + platform + '-' + handle + extension
        image_filepath = RESULT_FOLDER + 'original-' + image_filename
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


class FaceExtractor:
    @staticmethod
    def extract_face(image_filepath):
        logging.info("Processing {0}".format(image_filepath))

        # Create the Haar cascade
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

        # Read the image
        image = cv2.imread(image_filepath)
        resize_ratio = RESIZE_TOP_PIXELS/image.shape[1]
        image = cv2.resize(image, (0, 0,), fx=resize_ratio, fy=resize_ratio)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=20,
            minSize=(30, 30),
        )
        logging.info("Processing {0}. Faces found: {1}.".format(image_filepath, len(faces)))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        annotated_filename = os.path.dirname(image_filepath) + '/edge-' + os.path.basename(image_filepath)
        cv2.imwrite(annotated_filename, image)
        logging.info("Saving face-annotated image as {0}".format(annotated_filename))

        # Extract face if image contains only 1 face
        if len(faces) == 1:
            for (x, y, w, h) in faces:
                face_grayscale = gray[y:y+h, x:x+w]
                face_grayscale_resized = cv2.resize(face_grayscale, FACE_SIZE)
                face_filename = os.path.dirname(image_filepath) + '/face-' + os.path.basename(image_filepath)
                cv2.imwrite(face_filename, face_grayscale_resized)
                logging.info("Saving extracted grayscale face as {0}".format(face_filename))
        elif len(faces) == 0:
            logging.info("Found no faces. Not extracting any faces")
        else:
            logging.info("Found multiple faces. Not extracting any faces")


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
