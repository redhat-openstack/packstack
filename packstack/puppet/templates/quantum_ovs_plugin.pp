class { 'quantum::plugins::ovs':
  tenant_network_type => '%(CONFIG_QUANTUM_OVS_TENANT_NETWORK_TYPE)s',
  network_vlan_ranges => '%(CONFIG_QUANTUM_OVS_VLAN_RANGES)s',
  sql_connection      => $quantum_sql_connection
}

if $::operatingsystem != 'Fedora' {
  quantum_config {
    'DEFAULT/ovs_use_veth': value => 'True';
  }
}
