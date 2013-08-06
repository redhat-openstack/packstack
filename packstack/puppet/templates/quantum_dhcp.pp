class { 'quantum::agents::dhcp':
  interface_driver => '%(CONFIG_QUANTUM_DHCP_INTERFACE_DRIVER)s',
}
