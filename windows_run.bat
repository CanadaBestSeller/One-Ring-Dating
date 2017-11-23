REM TO-DO
REM 1. Get PID from START commands
REM 3. CTRL+C logic to kill aforementioned PIDs
REM 4. If condition for inputting OKC if user does not have OKC
REM 5. Update windows_readme.txt

REM Creative Controls
SET ONE_RING_MESSENGER_FIRST_LINE="Hello!"

REM Application Controls. Best leave alone.
SET ONE_RING_GLOBAL_SERVING_HOST=localhost

SET ONE_RING_PHASE_0_PROFILE_NOTIFIER_POLLING_INTERVAL=10
SET ONE_RING_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT=7000

SET ONE_RING_PHASE_0_FACE_EXTRACTOR_SERVER_PORT=%ONE_RING_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT%
SET ONE_RING_PHASE_0_FACE_EXTRACTOR_OUTPUT_LOCATION=%cd%\phase_1_pool

SET ONE_RING_PHASE_1_FACE_SELECTOR_INPUT_LOCATION=%ONE_RING_PHASE_1_FACE_EXTRACTOR_OUTPUT_LOCATION%
SET ONE_RING_PHASE_1_FACE_SELECTOR_POLLING_INTERVAL=5
SET ONE_RING_PHASE_1_FACE_SELECTOR_OUTPUT_LOCATION=%cd%\phase_2_candidates

SET ONE_RING_PHASE_2_POST_PROCESSOR_INPUT_LOCATION=%ONE_RING_PHASE_1_FACE_SELECTOR_OUTPUT_LOCATION%
SET ONE_RING_PHASE_2_POST_PROCESSOR_EXECUTION_INTERVAL=5
SET ONE_RING_PHASE_2_POST_PROCESSOR_OUTPUT_LOCATION=%cd%\phase_3_matches

SET ONE_RING_PHASE_3_MESSENGER_INPUT_LOCATION=%ONE_RING_PHASE_2_POST_PROCESSOR_OUTPUT_LOCATION%
SET ONE_RING_PHASE_3_MESSENGER_EXECUTION_INTERVAL=5

cls
@echo off

SET /p OKC_USERNAME="Enter your OkCupid username/email: "
CALL:getPassword OKC_PASSWORD "Enter your OkCupid password (hidden): "

REM This is needed to install the compiled binaries at the root code folder
python -m venv code\one_ring_virtual_env

REM Activate virtual environment
code\one_ring_virtual_env\Scripts\activate.bat

REM Install dependencies
pip install -r code\one_ring_modules\requirements.txt

REM Install one_ring_modules for global absolute imports
pip install %cd%\code

REM We are starting the applications in a descending order to avoid connection refusal.

REM Start the Face Extractor Server in the background
START /b cmd /c ^
    python code/one_ring_modules/face_extractor/face_extractor_server.py ^
    %ONE_RING_GLOBAL_SERVING_HOST% ^
    %ONE_RING_PHASE_0_FACE_EXTRACTOR_SERVER_PORT%
REM SET ONE_RING_PHASE_0_FACE_EXTRACTOR_SERVER_PID=$!

REM Start the Profile Collector/Notifier in the background
REM We can optionally enter a file name as the last argument, to read from a pre-fetched list of usernames, instead of OKC's quickmatch
REM This is useful for load testing, 404 testing, and procuring training data for face selection models START /b cmd /c ^
    python code\one_ring_modules\profile_collectors\profile_notifier.py ^
    %ONE_RING_GLOBAL_SERVING_HOST% ^
    %ONE_RING_PHASE_0_PROFILE_NOTIFIER_DESTINATION_PORT% ^
    %ONE_RING_PHASE_0_PROFILE_NOTIFIER_POLLING_INTERVAL% ^
    %cd%
REM SET ONE_RING_PHASE_0_PROFILE_NOTIFIER_PID=$!



REM------------------------------------------------------------------------------
REM Masks user input and returns the input as a variable.
REM Password-masking code based on http://www.dostips.com/forum/viewtopic.php?p=33538REMp33538
REM
REM Arguments: %1 - the variable to store the password in
REM            %2 - the prompt to display when receiving input
REM------------------------------------------------------------------------------
:getPassword
set "_password="

REM We need a backspace to handle character removal
for /f %%a in ('"prompt;$H&for %%b in (0) do rem"') do set "BS=%%a"

REM Prompt the user 
set /p "=%~2" <nul 

:keyLoop
REM Retrieve a keypress
set "key="
for /f "delims=" %%a in ('xcopy /l /w "%~f0" "%~f0" 2^>nul') do if not defined key set "key=%%a"
set "key=%key:~-1%"

REM If No keypress (enter), then exit
REM If backspace, remove character from password and console
REM Otherwise, add a character to password and go ask for next one
if defined key (
    if "%key%"=="%BS%" (
        if defined _password (
            set "_password=%_password:~0,-1%"
            set /p "=!BS! !BS!"<nul
        )
    ) else (
        set "_password=%_password%%key%"
        set /p "="<nul
    )
    goto :keyLoop
)
echo/

REM Return password to caller
set "%~1=%_password%"
goto :eof
