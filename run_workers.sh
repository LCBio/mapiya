#! /bin/bash

source /home/mapserver/miniconda3/bin/activate venv
logs=/home/mapserver/logs/workers
worker_count=$1
manage=/home/mapserver/mapserver/manage.py

for ((i=0; i<$worker_count; ++i)); do
  $manage rqworker >$logs/out$i.txt 2>$logs/log$i.txt &
done
