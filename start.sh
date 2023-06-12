#!/usr/bin/env bash

cd /opt/fuzz-ai-subs-live
git fetch --all
git reset --hard origin/main
chmod +x start.sh

if test -f "venv/bin/activate"; then
  echo "venv already created"
else
  echo "Creating venv"
  rm -rf venv
  python3 -m venv venv
fi

. venv/bin/activate
pip3 install --upgrade pip
pip3 install --upgrade -r requirements.txt
python3 main.py
