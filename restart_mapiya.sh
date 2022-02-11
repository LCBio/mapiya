#! /bin/bash

killall gunicorn
ps ax | grep rqworker | grep -v grep | awk '{print $1}' | xargs kill

source /home/mapserver/miniconda3/bin/activate venv
export TMPDIR=/home/mapserver/tmp
gunicorn -c lcbio/gunicorn.py
/home/mapserver/mapserver/run_workers.sh 10
