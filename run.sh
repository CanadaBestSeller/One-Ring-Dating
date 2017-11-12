#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:$PWD/heph_modules

HEPH_SERVING_HOST=localhost
HEPH_FACE_EXTRACTOR_SERVER_PORT=7777

python3 module_face_filter/face_extractor_server.py ${HEPH_SERVING_HOST} ${HEPH_FACE_EXTRACTOR_SERVER_PORT} &
HEPH_FACE_EXTRACTOR_SERVER_PORT_PID=$!

control_c() {
    echo ""
    echo ""
    echo "Ending program..."

    kill ${HEPH_FACE_EXTRACTOR_SERVER_PORT_PID}
    echo "Terminated Face Extractor Server."

    echo "Program exited."
    exit
}

trap control_c SIGINT

while true ; do
   :
done
