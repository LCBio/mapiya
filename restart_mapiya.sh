#! /bin/bash

killall gunicorn

source /home/mapserver/miniconda3/bin/activate venv
export TMPDIR=/home/mapserver/tmp
gunicorn -c lcbio/gunicorn.py
