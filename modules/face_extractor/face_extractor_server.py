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
ESSENTIAL_FOLDERS = [RESULT_FOLDER + NAME for NAME in ['ids/', 'faces/', 'edges/', 'originals/']]
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
        FaceExtractorServer.ensure_face_folders_exist()
        platform = face_extraction_request['platform']
        handle = face_extraction_request['handle']
        image_links = face_extraction_request['image_links']

        for index, image_link in enumerate(image_links):
            image_folder_path, image_filename = FaceExtractorServer.save_image(platform, handle, image_link, index)
            FaceExtractor.extract_face(image_folder_path, image_filename)

    @staticmethod
    def save_image(platform, handle, image_link, index):
        open(RESULT_FOLDER + 'ids/' + platform + '-' + handle + '.id', 'a').close()
        image_filename = platform + '-' + handle + '-' + str(index+1) + RESULT_EXTENSION
        image_folder_path = RESULT_FOLDER + 'originals/'
        urlretrieve(image_link, image_folder_path + image_filename)
        logging.info("Image has been successfully downloaded and saved as {0}".format(image_folder_path))
        return image_folder_path, image_filename

    @staticmethod
    def ensure_face_folders_exist():
        for folder_path in ESSENTIAL_FOLDERS:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)


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
    def extract_face(image_folder_path, image_filename):
        logging.info("Processing [{1}] @ {0}".format(image_folder_path, image_filename))

        # Create the Haar cascade
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

        # Read the image
        image = cv2.imread(image_folder_path + image_filename)
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
        logging.info("Faces found: {0}.".format(len(faces)))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        annotated_filename = image_folder_path + '../edges/' + image_filename
        cv2.imwrite(annotated_filename, image)
        logging.info("Saving face-annotated image as {0}".format(annotated_filename))

        # Extract face if image contains only 1 face
        if len(faces) == 1:
            for (x, y, w, h) in faces:
                face_grayscale = gray[y:y+h, x:x+w]
                face_grayscale_resized = cv2.resize(face_grayscale, FACE_SIZE)
                face_filename = image_folder_path + '../faces/' + image_filename
                cv2.imwrite(face_filename, face_grayscale_resized)
                logging.info("FOUND 1 FACE! Saving extracted grayscale face as {0}".format(face_filename))
        elif len(faces) == 0:
            logging.info("Found no faces. Not extracting any faces")
        else:
            logging.info("Found multiple faces. Not extracting any faces")

        logging.info("Face extraction finished.\n")


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

    logging.info("\n"
                 "\n-----------------------------------"
                 "\nFace Extraction Server online!"
                 "\nServing requests @ {}:{}"
                 "\n-----------------------------------"
                 "\n".format(serving_host, serving_port))

    server = socketserver.TCPServer((serving_host, serving_port), FaceExtractorServer)
    server.request_queue_size = 5
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Shutting down server...')
        server.shutdown()
        logging.info('Done!\n')
