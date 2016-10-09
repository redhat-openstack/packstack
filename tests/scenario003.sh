#!/bin/bash
if [ $(id -u) != 0 ]; then
    SUDO='sudo'
fi

echo -e "Generating packstack config for:
- keystone
- glance (file backend)
- nova
- neutron (ovs+vxlan)
- ceilometer
- aodh
- gnocchi
- heat
- tempest (regex: 'smoke TelemetryAlarming')"
echo "tempest will run if packstack's installation completes successfully."
echo

$SUDO packstack ${ADDITIONAL_ARGS} \
          --allinone \
          --debug \
          --service-workers=2 \
          --default-password="packstack" \
          --os-swift-install=n \
          --os-horizon-install=n \
          --glance-backend=file \
          --os-heat-install=y \
          --provision-uec-kernel-url="/tmp/cirros/cirros-0.3.4-x86_64-vmlinuz" \
          --provision-uec-ramdisk-url="/tmp/cirros/cirros-0.3.4-x86_64-initrd" \
          --provision-uec-disk-url="/tmp/cirros/cirros-0.3.4-x86_64-disk.img" \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke TelemetryAlarming" || export FAILURE=true
