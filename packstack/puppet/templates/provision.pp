class { 'openstack::provision':
  admin_password      => '%(CONFIG_KEYSTONE_ADMIN_PW)s',
  configure_tempest   => %(CONFIG_PROVISION_TEMPEST)s,
  setup_ovs_bridge    => %(CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE)s
}
