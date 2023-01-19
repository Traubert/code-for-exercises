#!/bin/sh
set -x
wget https://korp.csc.fi/download/YLE/fi/2019-2021-s-vrt/ylenews-fi-2019-2021-s-vrt.zip
unzip ylenews-fi-2019-2021-s-vrt.zip
rm ylenews-fi-2019-2021-s-vrt.zip
module load tykky
python3.9 -m venv tmp-venv
source tmp-venv/bin/activate
mkdir tykky-env
pip-containerize new --prefix tykky-env requirements.txt
deactivate
export PATH="$(pwd)/tykky-env/bin:$PATH"
python3 topics.py
