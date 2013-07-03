class { 'quantum::agents::l3':
  use_namespaces          => '%(CONFIG_QUANTUM_USE_NAMESPACES)s',
  interface_driver        => '%(CONFIG_QUANTUM_L3_INTERFACE_DRIVER)s',
  external_network_bridge => %(CONFIG_QUANTUM_L3_EXT_BRIDGE_STR)s,
}
