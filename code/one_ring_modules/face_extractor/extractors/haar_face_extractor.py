#!/usr/bin/env python3

import cv2
import logging
import os

from one_ring_modules.utils.file_utils import FileUtils

# Parameters
CASCADE_PATH = os.path.abspath('code/one_ring_modules/face_extractor/haarcascade_frontalface_default.xml')
FACE_SIZE = (100, 100)
RESIZE_TOP_PIXELS = 300
LOG_TAG = '[Haar Face Extractor] '


class HaarFaceExtractor:

    @staticmethod
    def extract_face(input_image_filepath, output_folder_path, output_prefix, output_filename):

        logging.debug(LOG_TAG + 'Processing image @ ' + input_image_filepath)
        logging.debug(LOG_TAG + 'Output folder @ ' + output_folder_path)

        # Create the Haar cascade
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

        # Read the image
        image = cv2.imread(input_image_filepath)
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
        logging.debug(LOG_TAG + 'Faces found: {0}.'.format(len(faces)))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        annotated_folder_path = output_folder_path + '/' + output_prefix + 'edges/'
        FileUtils.create_folder_if_not_exists(annotated_folder_path)
        annotated_filepath = annotated_folder_path + output_filename
        cv2.imwrite(annotated_filepath, image)
        logging.debug(LOG_TAG + 'Saving face-annotated image as {0}'.format(annotated_filepath))

        # Extract face if image contains only 1 face
        if len(faces) == 1:
            for (x, y, w, h) in faces:
                face_grayscale = gray[y:y+h, x:x+w]
                face_grayscale_resized = cv2.resize(face_grayscale, FACE_SIZE)
                face_folder_path = output_folder_path + '/' + output_prefix + 'faces/'
                FileUtils.create_folder_if_not_exists(face_folder_path)
                face_filepath = face_folder_path + output_filename
                cv2.imwrite(face_filepath, face_grayscale_resized)
                logging.info(LOG_TAG + 'FOUND 1 FACE! Saving extracted grayscale face as {0}'.format(face_filepath))
        elif len(faces) == 0:
            logging.debug(LOG_TAG + 'Found no faces. Not extracting any faces')
        else:
            logging.debug(LOG_TAG + 'Found multiple faces. Not extracting any faces')

        logging.debug(LOG_TAG + 'Face extraction finished.\n')

