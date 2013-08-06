vs_port { '%(CONFIG_NEUTRON_OVS_IFACE)s':
  bridge => '%(CONFIG_NEUTRON_OVS_BRIDGE)s',
  ensure => present
}

