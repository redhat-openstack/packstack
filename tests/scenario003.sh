#!/bin/bash
CONTROLLER_NODE=${CONTROLLER_NODE:-}
COMPUTE_NODE=${COMPUTE_NODE:-}

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
- magnum
- tempest (regex: 'smoke TelemetryAlarming')"
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
          --os-swift-install=n \
          --os-horizon-install=n \
          --glance-backend=file \
          --os-heat-install=y \
          --os-magnum-install=y \
          --nova-libvirt-virt-type=qemu \
          --provision-image-url="/tmp/cirros/cirros-$CIRROS_VERSION-$CIRROS_ARCH-disk.img" \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke TelemetryAlarming" || export FAILURE=true
