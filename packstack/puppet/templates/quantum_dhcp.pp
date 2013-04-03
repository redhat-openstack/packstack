class { 'quantum::agents::dhcp':
  use_namespaces   => '%(CONFIG_QUANTUM_USE_NAMESPACES)s',
  interface_driver => '%(CONFIG_QUANTUM_DHCP_INTERFACE_DRIVER)s',
}
