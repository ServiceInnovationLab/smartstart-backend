#!/bin/bash

DIRECTORY=$(dirname $0)/..

find ${DIRECTORY} -iname '*.py' \
    | grep -v migration \
    | xargs flake8 --ignore=E501,W503,E402 \
    | grep -vP "settings/.*F403"
