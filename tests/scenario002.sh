#!/bin/bash
if [ $(id -u) != 0 ]; then
    SUDO='sudo'
fi

echo -e "Generating packstack config for:
- keystone
- glance (swift backend)
- nova
- neutron (ovs+vxlan)
- lbaasv2
- swift
- sahara
- trove
- tempest (regex: 'smoke dashboard')"
echo "tempest will run if packstack's installation completes successfully."
echo

$SUDO packstack ${ADDITIONAL_ARGS} \
          --allinone \
          --debug \
          --service-workers=2 \
          --default-password="packstack" \
          --os-aodh-install=n \
          --os-ceilometer-install=n \
          --os-gnocchi-install=n \
          --os-cinder-install=n \
          --os-horizon-install=n \
          --nagios-install=n \
          --glance-backend=swift \
          --os-neutron-lbaas-install=y \
          --os-sahara-install=y \
          --os-trove-install=y \
          --provision-uec-kernel-url="/tmp/cirros/cirros-0.3.4-x86_64-vmlinuz" \
          --provision-uec-ramdisk-url="/tmp/cirros/cirros-0.3.4-x86_64-initrd" \
          --provision-uec-disk-url="/tmp/cirros/cirros-0.3.4-x86_64-disk.img" \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke" || export FAILURE=true
