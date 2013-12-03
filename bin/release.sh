#!/usr/bin/env bash
#

git reset --hard
git submodule sync
git submodule update --init
git status -s | grep "." && ( echo "Contains unknown files" ; exit 1 )

if [ "$1" = "release" ] ; then
    sed -i -e 's/FINAL=False/FINAL=True/g' packstack/version.py
    SNAPTAG=""
else
    SNAPTAG=$(git log --oneline | wc -l)
fi

python setup.py setopt -o tag_build -s "$SNAPTAG" -c egg_info
python setup.py sdist
git checkout packstack/version.py
