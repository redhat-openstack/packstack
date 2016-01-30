#!/bin/bash
if [ $(id -u) != 0 ]; then
    SUDO='sudo'
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

$SUDO packstack --allinone \
          --debug \
          --default-password="packstack" \
          --os-swift-install=n \
          --os-horizon-install=n \
          --os-manila-install=y \
          --glance-backend=swift \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke TelemetryAlarming" || export FAILURE=true
