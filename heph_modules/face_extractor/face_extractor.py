#!/usr/bin/env python3

import cv2
import logging
import os

# Parameters
CASCADE_PATH = os.path.abspath("heph_modules/face_extractor/haarcascade_frontalface_default.xml")
FACE_SIZE = (100, 100)
RESIZE_TOP_PIXELS = 300

# Logging
LOG_NAME = 'face_extractor.log'
LOG_FORMAT = '[FACE_EXTRACTOR_SERVER] %(asctime)s - %(name)s - %(levelname)s - %(message)s'


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
