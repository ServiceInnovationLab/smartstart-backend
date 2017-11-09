#!/bin/bash

ROOTDIR=$(dirname $0)/..
cd $ROOTDIR

$ROOTDIR/bin/bootstrap.sh

virtualenv -p python3 $ROOTDIR/venv
. $ROOTDIR/venv/bin/activate
$ROOTDIR/venv/bin/pip install -U -r requirements.txt

# Run the damned tests already
$ROOTDIR/venv/bin/python manage.py test
