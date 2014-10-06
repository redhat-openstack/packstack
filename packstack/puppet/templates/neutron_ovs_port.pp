$cfg_neutron_ovs_iface = hiera('CONFIG_NEUTRON_OVS_IFACE')

vs_port { $cfg_neutron_ovs_iface:
  ensure => present,
  bridge => hiera('CONFIG_NEUTRON_OVS_BRIDGE'),
}

