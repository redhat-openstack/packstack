#!/usr/bin/env bash

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR=`dirname $SCRIPT_PATH`
cd $SCRIPT_DIR/..

git reset --hard

if [ -n "$1" ] ; then
    git tag -a -m $1 $1
fi

VERSION=`python setup.py --version`

sed -i -e "s/RESERVE_STR = None/RESERVE_STR = '$VERSION'/g" packstack/version.py
python setup.py sdist

if [ -n "$1" ] ; then
    echo "Packstack was released with tag '$1'. Please don't forget to push tag upstream (git push --tags)."
fi

git checkout packstack/version.py
