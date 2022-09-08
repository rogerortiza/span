#!/bin/sh
python -m venv ./span_env
source span_env/bin/activate

python -m pip install -r requirements.txt

python -m ranking init --db_path=./ranking.json