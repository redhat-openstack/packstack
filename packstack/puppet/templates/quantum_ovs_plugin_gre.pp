class { 'quantum::plugins::ovs':
  tenant_network_type => '%(CONFIG_QUANTUM_OVS_TENANT_NETWORK_TYPE)s',
  tunnel_id_ranges => '%(CONFIG_QUANTUM_OVS_TUNNEL_RANGES)s',
  sql_connection      => $quantum_sql_connection
}
