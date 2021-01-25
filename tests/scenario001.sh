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
- cinder (lvm+iscsi)
- manila
- tempest (regex: 'smoke')"
echo "tempest will run if packstack's installation completes successfully."
echo

if [ -z $COMPUTE_NODE ]; then
  NODE_FLAGS="--allinone"
else
  NODE_FLAGS="--allinone --os-controller-host=$CONTROLLER_NODE --os-network-hosts=$CONTROLLER_NODE --os-compute-hosts=$COMPUTE_NODE"
fi

$SUDO packstack ${ADDITIONAL_ARGS} \
          ${NODE_FLAGS} \
          --cinder-volume-name="aVolume" \
          --debug \
          --os-debug-mode=y \
          --service-workers=2 \
          --default-password="packstack" \
          --os-aodh-install=n \
          --os-ceilometer-install=n \
          --os-swift-install=n \
          --os-manila-install=y \
          --os-horizon-ssl=y \
          --amqp-enable-ssl=y \
          --glance-backend=file \
          --nova-libvirt-virt-type=qemu \
          --provision-image-url="/tmp/cirros/cirros-$CIRROS_VERSION-$CIRROS_ARCH-disk.img" \
          --provision-demo=y \
          --provision-tempest=y \
          --run-tempest=y \
          --run-tempest-tests="smoke dashboard" \
          --skip-tempest-tests="test_dashboard_basic_ops" || export FAILURE=true
