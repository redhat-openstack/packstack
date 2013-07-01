class { 'quantum::plugins::linuxbridge':
  tenant_network_type => '%(CONFIG_QUANTUM_LB_TENANT_NETWORK_TYPE)s',
  network_vlan_ranges => '%(CONFIG_QUANTUM_LB_VLAN_RANGES)s',
  sql_connection      => $quantum_sql_connection
}
