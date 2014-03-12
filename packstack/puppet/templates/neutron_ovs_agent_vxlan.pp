
if "%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s" {
  $localip = getvar(regsubst("$ipaddress_%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s", '[.-]', '_', 'G'))
} else {
  $localip = '%(CONFIG_NEUTRON_OVS_HOST)s'
}

class { 'neutron::agents::ovs':
  bridge_mappings => %(CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS)s,
  enable_tunneling => true,
  tunnel_types => ['vxlan'],
  local_ip => $localip,
  vxlan_udp_port => %(CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT)s,
}
