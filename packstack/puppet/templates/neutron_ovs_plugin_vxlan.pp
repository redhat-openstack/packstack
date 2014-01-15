
class { 'neutron::plugins::ovs':
  tenant_network_type => '%(CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE)s',
  network_vlan_ranges => '%(CONFIG_NEUTRON_OVS_VLAN_RANGES)s',
  tunnel_id_ranges => '%(CONFIG_NEUTRON_OVS_TUNNEL_RANGES)s',
  vxlan_udp_port => %(CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT)s,
}
