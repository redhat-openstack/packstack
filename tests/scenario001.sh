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
- tempest (regex: 'smoke')"
echo "tempest will run if packstack's installation completes successfully."
echo

$SUDO packstack ${ADDITIONAL_ARGS} \
          --allinone \
          --cinder-volume-name="aVolume" \
          --debug \
          --service-workers=2 \
          --default-password="packstack" \
          --os-aodh-install=n \
          --os-ceilometer-install=n \
          --os-swift-install=n \
          --os-manila-install=y \
          --os-horizon-ssl=y \
          --amqp-enable-ssl=y \
          --glance-backend=file \
          --os-neutron-l2-agent=ovn \
          --os-neutron-ml2-type-drivers="geneve,flat" \
          --os-neutron-ml2-tenant-network-types="geneve" \
          --provision-uec-kernel-url="/tmp/cirros/cirros-0.3.4-x86_64-vmlinuz" \
          --provision-uec-ramdisk-url="/tmp/cirros/cirros-0.3.4-x86_64-initrd" \
          --provision-uec-disk-url="/tmp/cirros/cirros-0.3.4-x86_64-disk.img" \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke dashboard" || export FAILURE=true
