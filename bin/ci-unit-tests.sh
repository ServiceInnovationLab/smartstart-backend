#!/bin/bash

ROOTDIR=$(dirname $(dirname $0))
export PYTHONPATH=$ROOTDIR:$PYTHONPATH

$ROOTDIR/bin/bootstrap.sh

virtualenv -p python3 venv
. $ROOTDIR/venv/bin/activate
$ROOTDIR/venv/bin/pip install -U -r requirements.txt

# Run the damned tests already
$ROOTDIR/venv/bin/python manage.py test
