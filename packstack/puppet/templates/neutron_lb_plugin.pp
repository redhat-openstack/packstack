class { 'neutron::plugins::linuxbridge':
  tenant_network_type => hiera('CONFIG_NEUTRON_LB_TENANT_NETWORK_TYPE'),
  network_vlan_ranges => hiera('CONFIG_NEUTRON_LB_VLAN_RANGES'),
}
