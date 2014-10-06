class { 'neutron::plugins::ovs':
  tenant_network_type => hiera('CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE'),
  network_vlan_ranges => hiera('CONFIG_NEUTRON_OVS_VLAN_RANGES'),
}
