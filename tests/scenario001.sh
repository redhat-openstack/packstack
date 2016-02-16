#!/bin/bash -ex
PACKSTACK_CONFIG_FILE="/tmp/packstack.txt"

if [ $(id -u) != 0 ]; then
    # preserve environment so we can have ZUUL_* params
    SUDO='sudo -E'
fi

echo -e "Generating packstack config for:
- keystone
- glance (file backend)
- nova
- neutron (ovs+vxlan)
- cinder (lvm+iscsi)
- ceilometer
- aodh
- gnocchi
- trove
- manila
- nagios
- tempest (regex: 'smoke TelemetryAlarming')"
echo "tempest will run if packstack's installation completes successfully."
echo

packstack --allinone \
          --os-swift-install=n \
          --os-horizon-install=n \
          --os-manila-install=y \
          --glance-backend=swift \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke TelemetryAlarming" \
          --gen-answer-file=${PACKSTACK_CONFIG_FILE}
sed -i -re "s,(.*_PASSWORD|.*_PW)=.*,\1=packstack," ${PACKSTACK_CONFIG_FILE}

$SUDO packstack --answer-file=${PACKSTACK_CONFIG_FILE} || export FAILURE="true"
