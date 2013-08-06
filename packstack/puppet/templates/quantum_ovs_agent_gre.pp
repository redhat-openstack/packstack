if "%(CONFIG_QUANTUM_OVS_TUNNEL_IF)s" {
  $localip = $ipaddress_%(CONFIG_QUANTUM_OVS_TUNNEL_IF)s
} else {
  $localip = '%(CONFIG_QUANTUM_OVS_HOST)s'
}

class { 'quantum::agents::ovs':
  enable_tunneling => true,
  local_ip => $localip,
}
