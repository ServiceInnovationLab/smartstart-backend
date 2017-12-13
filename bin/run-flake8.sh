#!/bin/bash

cd $(dirname $0)/..
flaketmp=$HOME/.flaketmp

find $(git ls-files $*) -iname '*.py' \
    | grep -v migration \
    | xargs flake8 --ignore=E501,W503,E402 \
    | grep -vP "settings/.*F403" \
> $flaketmp 2>&1

if [ -s $flaketmp ]; then
    cat $flaketmp
    rm $flaketmp
    exit 1
else
    rm $flaketmp
    exit 0
fi
