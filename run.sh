#!/usr/bin/env bash

export PYTHONPATH=$PYTHONPATH:$PWD/heph_modules

HEPH_SERVING_HOST=localhost
HEPH_FACE_EXTRACTOR_SERVER_PORT=7000
HEPH_OKC_POLLING_INTERVAL=5

python3 heph_modules/face_extractor/face_extractor_server.py ${HEPH_SERVING_HOST} ${HEPH_FACE_EXTRACTOR_SERVER_PORT} &
HEPH_FACE_EXTRACTOR_SERVER_PID=$!

python3 heph_modules/profile_collectors/profile_notifier.py ${HEPH_SERVING_HOST} ${HEPH_FACE_EXTRACTOR_SERVER_PORT} ${HEPH_OKC_POLLING_INTERVAL} &
HEPH_OKC_POLLER_PID=$!

control_c() {
    echo ""
    echo ""
    echo "Ending program..."

    kill ${HEPH_OKC_POLLER_PID}
    echo "Terminated OKC Profile Collector."

    kill ${HEPH_FACE_EXTRACTOR_SERVER_PID}
    echo "Terminated Face Extractor Server."

    echo "Program exited."
    exit
}

trap control_c SIGINT

while true ; do
   :
done
