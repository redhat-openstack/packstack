if "%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s" {
  $localip = $ipaddress_%(CONFIG_NEUTRON_OVS_TUNNEL_IF)s
} else {
  $localip = '%(CONFIG_NEUTRON_OVS_HOST)s'
}

class { 'neutron::agents::ovs':
  enable_tunneling => true,
  local_ip => $localip,
}
