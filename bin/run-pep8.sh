#!/bin/bash


## Runs pep8 over the Python files in PaCT.
##
## you can add arguments for pep8. like --repeat
## if you want to see all the complaints for each file.

DIRECTORY=$(dirname $0)/../pact

find ${DIRECTORY} -path '*/migrations' -prune  \
  -o -name '*.py' -print0 | xargs --null pep8 --ignore=E501,W503,E402 $@
