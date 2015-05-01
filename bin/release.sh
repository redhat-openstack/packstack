#!/usr/bin/env bash

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR=`dirname $SCRIPT_PATH`
cd $SCRIPT_DIR/..

if [ -n "$1" ] ; then
  # tagged release
  BRANCH=`git rev-parse --abbrev-ref HEAD`
  git fetch gerrit
  git tag -m $1 -s $1 gerrit/$BRANCH
  git push gerrit tag $1
else
  # development release
  VERSION=`python setup.py --version`
  sed -i -e "s/RESERVE_STR = None/RESERVE_STR = '$VERSION'/g" packstack/version.py
  python setup.py sdist
  git checkout packstack/version.py
fi
