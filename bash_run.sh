#!/usr/bin/env bash

# Creative Controls
ONE_RING_MESSENGER_FIRST_LINE="Hello!"

# Application Controls. Best leave alone.
ONE_RING_GLOBAL_SERVING_HOST=localhost

ONE_RING_PHASE_0_PROFILE_NOTIFIER_POLLING_INTERVAL=10
ONE_RING_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT=7000

ONE_RING_PHASE_0_FACE_EXTRACTOR_SERVER_PORT=$ONE_RING_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT
ONE_RING_PHASE_0_FACE_EXTRACTOR_OUTPUT_LOCATION="${PWD}/phase_1_faces"

ONE_RING_PHASE_1_FACE_SELECTOR_INPUT_LOCATION=$ONE_RING_PHASE_1_FACE_EXTRACTOR_OUTPUT_LOCATION
ONE_RING_PHASE_1_FACE_SELECTOR_POLLING_INTERVAL=5
ONE_RING_PHASE_1_FACE_SELECTOR_OUTPUT_LOCATION="${PWD}/phase_2_candidates"

ONE_RING_PHASE_2_POST_PROCESSOR_INPUT_LOCATION=$ONE_RING_PHASE_1_FACE_SELECTOR_OUTPUT_LOCATION
ONE_RING_PHASE_2_POST_PROCESSOR_EXECUTION_INTERVAL=5
ONE_RING_PHASE_2_POST_PROCESSOR_OUTPUT_LOCATION="${PWD}/phase_3_matches"

ONE_RING_PHASE_3_MESSENGER_INPUT_LOCATION=$ONE_RING_PHASE_2_POST_PROCESSOR_OUTPUT_LOCATION
ONE_RING_PHASE_3_MESSENGER_EXECUTION_INTERVAL=5

if [ -z ${ONE_RING_OKC_USERNAME+x} ]; 
    then echo "Please enter your OkCupid username/email:"; 
    read ONE_RING_OKC_USERNAME; export ONE_RING_OKC_USERNAME; 
else echo "OKC username is set."; fi

if [ -z ${ONE_RING_OKC_PASSWORD+x} ]; 
    then echo "Please enter your OkCupid password:"; 
    read -s ONE_RING_OKC_PASSWORD; export ONE_RING_OKC_PASSWORD; 
else echo "OKC password is set."; fi

if [ -z ${ONE_RING_FB_EMAIL+x} ]; 
    then echo "Please enter your Facebook email:"; 
    read ONE_RING_FB_EMAIL; export ONE_RING_FB_EMAIL; 
else echo "FB email is set."; fi

if [ -z ${ONE_RING_FB_PASSWORD+x} ]; 
    then echo "Please enter your Facebook password:"; 
    read -s ONE_RING_FB_PASSWORD; export ONE_RING_FB_PASSWORD; 
else echo "FB password is set."; fi

clear

if [ ! -d "${PWD}/code/one_ring_virtual_env" ]; then
echo "Creating virtual environment..."
python3 -m venv ./code/one_ring_virtual_env
echo "Done!"; echo ""
fi

echo "Activating virtual environment..."
source ./code/one_ring_virtual_env/bin/activate
echo "Done!"

clear

if [ ! -d "${PWD}/code/one_ring_modules.egg-info" ]; then
echo "Installing necessary external dependencies in virtual environment..."
pip install -r code/one_ring_modules/requirements.txt
echo "Done!"
fi

clear

if [ ! -d "${PWD}/code/one_ring_modules.egg-info" ]; then
echo "Creating global module symlinks in virtual env to enable absolute imports..."
pip install -e ./code
echo "Done!"
fi

clear

# We are starting the applications in a descending order to avoid connection refusal.
python3 code/one_ring_modules/face_extractor/face_extractor_server.py \
    ${ONE_RING_GLOBAL_SERVING_HOST} \
    ${ONE_RING_PHASE_0_FACE_EXTRACTOR_SERVER_PORT} \
    &
ONE_RING_PHASE_0_FACE_EXTRACTOR_SERVER_PID=$!

# We can optionally enter a file name as the last argument, to read from a pre-fetched list of usernames, instead of OKC's quickmatch
# This is useful for load testing, 404 testing, and procuring training data for face selection models
python3 code/one_ring_modules/profile_collectors/profile_notifier.py \
    ${ONE_RING_GLOBAL_SERVING_HOST} \
    ${ONE_RING_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT} \
    ${ONE_RING_PHASE_0_PROFILE_NOTIFIER_POLLING_INTERVAL} \
    ${PWD} \
    okc.test \
    &
ONE_RING_PHASE_0_PROFILE_NOTIFIER_PID=$!

control_c() {
    echo ""
    echo ""
    echo "Ending program..."

    kill ${ONE_RING_PHASE_0_FACE_EXTRACTOR_SERVER_PID}
    echo "Terminated Face Extractor Server."

    kill ${ONE_RING_PHASE_0_PROFILE_NOTIFIER_PID}
    echo "Terminated OKC Profile Collector."

    deactivate
    echo "Virtual environment deactivated."

    echo "One Ring Dating exited successfully."
    exit
}

trap control_c SIGINT

while true ; do
   :
done
