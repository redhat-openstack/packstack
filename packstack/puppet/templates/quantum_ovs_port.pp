vs_port { '%(CONFIG_QUANTUM_OVS_IFACE)s':
  bridge => '%(CONFIG_QUANTUM_OVS_BRIDGE)s',
  ensure => present
}

