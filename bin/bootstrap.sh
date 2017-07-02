#!/bin/bash
set -x  # echo on

# run this script with sudo
# didn't prepend `sudo` before each line
# since while in docker, sudo is not installed by default

sudo apt-get update -y
sudo apt-get install -y vim libxml2-dev libxslt1-dev zlib1g-dev libxmlsec1-dev xmlsec1 pkg-config python3-dev python-pip

pip install -U pip
pip install -U virtualenv virtualenvwrapper
