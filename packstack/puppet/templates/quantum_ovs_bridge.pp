vs_bridge { '%(CONFIG_QUANTUM_OVS_BRIDGE)s':
  ensure => present,
  require => Service['quantum-plugin-ovs-service']
}
