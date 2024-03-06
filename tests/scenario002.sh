#!/bin/bash
CONTROLLER_NODE=${CONTROLLER_NODE:-}
COMPUTE_NODE=${COMPUTE_NODE:-}

if [ $(id -u) != 0 ]; then
    SUDO='sudo'
fi

echo -e "Generating packstack config for:
- keystone
- glance (swift backend)
- nova
- neutron (ovs+vxlan)
- swift
- trove
- tempest (regex: 'smoke dashboard')"
echo "tempest will run if packstack's installation completes successfully."
echo

if [ -z $COMPUTE_NODE ]; then
  NODE_FLAGS="--allinone"
else
  NODE_FLAGS="--allinone --os-controller-host=$CONTROLLER_NODE --os-network-hosts=$CONTROLLER_NODE --os-compute-hosts=$COMPUTE_NODE"
fi

$SUDO packstack ${ADDITIONAL_ARGS} \
          ${NODE_FLAGS} \
          --debug \
          --os-debug-mode=y \
          --service-workers=2 \
          --default-password="packstack" \
          --os-aodh-install=n \
          --os-ceilometer-install=n \
          --os-cinder-install=n \
          --os-horizon-install=n \
          --glance-backend=swift \
          --os-neutron-l2-agent=openvswitch \
          --os-neutron-ml2-type-drivers="vxlan,flat" \
          --os-neutron-ml2-tenant-network-types="vxlan" \
          --os-neutron-vpnaas-install=n \
          --os-trove-install=y \
          --nova-libvirt-virt-type=qemu \
          --provision-image-url="/tmp/cirros/cirros-$CIRROS_VERSION-$CIRROS_ARCH-disk.img" \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke" || export FAILURE=true
