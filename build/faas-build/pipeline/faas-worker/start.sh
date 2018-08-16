#!/bin/sh

cd /root/temp/cloudframe
python setup.py install --user
python /root/.local/bin/faas-master &
python /root/.local/bin/faas-worker