#!/usr/bin/env bash


echo "Performing environment setup..."
ORIGINAL_DIRECTORY="`pwd`"
LOCAL_DIRECTORY="`dirname ${0}`"
cd ${LOCAL_DIRECTORY}
LOG_FILE=./fanControllerLog.log
if [[ ! -f "$LOG_FILE" ]]; then
    touch ${LOG_FILE}
fi
chmod -R 757 ${LOG_FILE}
VENV_DIR=venv
if [[ ! -d "$VENV_DIR" ]]; then
    echo "$VENV_DIR directory not detected. Creating virtual environment..."
    virtualenv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate
pip3 install -r requirements.txt


echo "Launching Pi Fan Controller..."
python3 main.py >> ${LOG_FILE}


echo "Performing environment teardown..."
deactivate
cd ${ORIGINAL_DIRECTORY}
echo "Pi Fan Controller terminated."