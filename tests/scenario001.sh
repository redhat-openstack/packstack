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
- manila
- nagios
- tempest (regex: 'smoke')"
echo "tempest will run if packstack's installation completes successfully."
echo

$SUDO packstack --allinone \
          --debug \
          --service-workers=2 \
          --default-password="packstack" \
          --os-aodh-install=n \
          --os-ceilometer-install=n \
          --os-gnocchi-install=n \
          --os-swift-install=n \
          --os-manila-install=y \
          --os-horizon-ssl=y \
          --amqp-enable-ssl=y \
          --glance-backend=file \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke dashboard" || export FAILURE=true
