#!/bin/bash
set -x  # echo on

sudo apt-get update
sudo apt-get install -y vim libxml2-dev libxslt1-dev zlib1g-dev libxmlsec1-dev xmlsec1 python3-dev python-pip
sudo apt-get autoremove -y
sudo apt-get clean

sudo pip install -U pip
sudo pip install -U virtualenv
