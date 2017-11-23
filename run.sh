#!/usr/bin/env bash

# Creative Controls
HEPH_MESSENGER_FIRST_LINE="Hello!"

# Application Controls. Best leave alone.
HEPH_GLOBAL_SERVING_HOST=localhost

HEPH_PHASE_0_PROFILE_NOTIFIER_POLLING_INTERVAL=5
HEPH_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT=7001

HEPH_PHASE_0_FACE_EXTRACTOR_SERVER_PORT=$HEPH_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT
HEPH_PHASE_0_FACE_EXTRACTOR_OUTPUT_LOCATION="${PWD}/phase_1_pool"

HEPH_PHASE_1_FACE_SELECTOR_INPUT_LOCATION=$HEPH_PHASE_1_FACE_EXTRACTOR_OUTPUT_LOCATION
HEPH_PHASE_1_FACE_SELECTOR_POLLING_INTERVAL=5
HEPH_PHASE_1_FACE_SELECTOR_OUTPUT_LOCATION="${PWD}/phase_2_candidates"

HEPH_PHASE_2_POST_PROCESSOR_INPUT_LOCATION=$HEPH_PHASE_1_FACE_SELECTOR_OUTPUT_LOCATION
HEPH_PHASE_2_POST_PROCESSOR_EXECUTION_INTERVAL=5
HEPH_PHASE_2_POST_PROCESSOR_OUTPUT_LOCATION="${PWD}/phase_3_matches"

HEPH_PHASE_3_MESSENGER_INPUT_LOCATION=$HEPH_PHASE_2_POST_PROCESSOR_OUTPUT_LOCATION
HEPH_PHASE_3_MESSENGER_EXECUTION_INTERVAL=5

# Prompt OKC username if not already set
if [ -z ${OKC_USERNAME+x} ]; then echo "Please enter your OkCupid username/email:"; read OKC_USERNAME; export OKC_USERNAME; else echo "OKC username is set."; fi

# Prompt OKC password if not already set
if [ -z ${OKC_PASSWORD+x} ]; then echo "Please enter your OkCupid password:"; read -s OKC_PASSWORD; export OKC_PASSWORD; else echo "OKC password is set."; fi

# This is needed to install the compiled binaries at the root code folder
cd code
python3 setup.py install
cd ..

# Enable global absolute-path imports
export PYTHONPATH=$PYTHONPATH:$PWD/code/heph_modules

# We are starting the applications in a descending order to avoid connection refusal.
python3 code/heph_modules/face_extractor/face_extractor_server.py \
    ${HEPH_GLOBAL_SERVING_HOST} \
    ${HEPH_PHASE_0_FACE_EXTRACTOR_SERVER_PORT} \
    &
HEPH_PHASE_0_FACE_EXTRACTOR_SERVER_PID=$!

# We can optionally enter a file name as the last argument, to read from a pre-fetched list of usernames, instead of OKC's quickmatch
# This is useful for load testing, 404 testing, and procuring training data for face selection models
python3 code/heph_modules/profile_collectors/profile_notifier.py \
    ${HEPH_GLOBAL_SERVING_HOST} \
    ${HEPH_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT} \
    ${HEPH_PHASE_0_PROFILE_NOTIFIER_POLLING_INTERVAL} \
    ${PWD} \
    okc.test \
    &
HEPH_PHASE_0_PROFILE_NOTIFIER_PID=$!

control_c() {
    echo ""
    echo ""
    echo "Ending program..."

    kill ${HEPH_PHASE_0_FACE_EXTRACTOR_SERVER_PID}
    echo "Terminated Face Extractor Server."

    kill ${HEPH_PHASE_0_PROFILE_NOTIFIER_PID}
    echo "Terminated OKC Profile Collector."

    echo "Program exited."
    exit
}

trap control_c SIGINT

while true ; do
   :
done
