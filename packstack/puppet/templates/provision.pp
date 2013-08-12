class { 'openstack::provision':
  admin_password      => '%(CONFIG_KEYSTONE_ADMIN_PW)s',
  password            => '%(CONFIG_KEYSTONE_DEMO_PW)s',
  configure_tempest   => %(CONFIG_PROVISION_TEMPEST)s,
  setup_ovs_bridge    => %(CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE)s,
  public_bridge_name  => '%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s'
}

firewall { '000 nat':
  chain  => 'POSTROUTING',
  jump   => 'MASQUERADE',
  source => $::openstack::provision::floating_range,
  outiface => $::gateway_device,
  table => 'nat',
  proto => 'all',
}

firewall { '000 forward out':
  chain => 'FORWARD',
  action  => 'accept',
  outiface => '%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s',
  proto => 'all',
}

firewall { '000 forward in':
  chain => 'FORWARD',
  action  => 'accept',
  iniface => '%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s',
  proto => 'all',
}
