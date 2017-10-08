#!/usr/bin/env python3

import logging
import os

import cv2

CASCADE_PATH = "haarcascade_frontalface_default.xml"
RESULT_EXTENSION = ".jpg"
FACE_SIZE = (100, 100)


class FaceExtractor:

    @staticmethod
    def extract_face(image_filepath):
        logging.info("Processing {0}...".format(image_filepath))

        # Create the Haar cascade
        face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

        # Read the image
        image = cv2.imread(image_filepath)
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
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        annotated_filename = os.path.splitext(image_filepath)[0] + "-annotated" + RESULT_EXTENSION
        cv2.imwrite(annotated_filename, image)
        logging.info("Saving face-annotated image as {0}".format(annotated_filename))

        # Extract face if image contains only 1 face
        if len(faces) == 1:
            for (x, y, w, h) in faces:
                face_grayscale = gray[y:h, x:w]
                # cv2.resize(face_grayscale, FACE_SIZE)
                face_filename = os.path.splitext(image_filepath)[0] + "-face" + RESULT_EXTENSION
                cv2.imwrite(face_filename, face_grayscale)
                logging.info("Saving extracted grayscale face as {0}".format(face_filename))
        else:
            logging.info("Found multiple faces. Not extracting any faces")
