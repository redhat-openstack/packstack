if "%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s" {
  $localip = $ipaddress_%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s
} else {
  $localip = '%(CONFIG_NEUTRON_OVS_HOST)s'
}

class { 'neutron::agents::ovs':
  bridge_mappings => %(CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS)s,
  enable_tunneling => true,
  local_ip => $localip,
}
