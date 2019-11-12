#!/bin/bash
if [ $(id -u) != 0 ]; then
    SUDO='sudo'
fi

$SUDO packstack ${ADDITIONAL_ARGS} \
          --allinone \
          --debug \
          --os-debug-mode=y \
          --service-workers=2 \
          --default-password="packstack" || export FAILURE=true
