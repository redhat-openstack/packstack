#!/bin/bash -ex
PACKSTACK_CONFIG_FILE="/tmp/packstack.txt"

if [ $(id -u) != 0 ]; then
    # preserve environment so we can have ZUUL_* params
    SUDO='sudo -E'
fi

echo -e "Generating packstack config for:
- keystone
- glance (swift backend)
- nova
- neutron (ovs+vxlan)
- heat
- swift
- sahara
- horizon
- trove
- tempest (regex: 'smoke dashboard')"
echo "tempest will run if packstack's installation completes successfully."
echo

packstack --allinone \
          --os-aodh-install=n \
          --os-ceilometer-install=n \
          --os-gnocchi-install=n \
          --os-cinder-install=n \
          --nagios-install=n \
          --glance-backend=swift \
          --os-sahara-install=y \
          --os-heat-install=y \
          --os-trove-install=y \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke dashboard" \
          --gen-answer-file=${PACKSTACK_CONFIG_FILE}
sed -i -re "s,(.*_PASSWORD|.*_PW)=.*,\1=packstack," ${PACKSTACK_CONFIG_FILE}

$SUDO packstack --answer-file=${PACKSTACK_CONFIG_FILE} || export FAILURE="true"
