#!/bin/bash
if [ $(id -u) != 0 ]; then
    SUDO='sudo'
fi

$SUDO packstack ${ADDITIONAL_ARGS} \
          --allinone \
          --debug \
          --default-password="packstack" || export FAILURE=true
