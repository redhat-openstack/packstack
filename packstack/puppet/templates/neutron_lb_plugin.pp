class { 'neutron::plugins::linuxbridge':
  tenant_network_type => '%(CONFIG_NEUTRON_LB_TENANT_NETWORK_TYPE)s',
  network_vlan_ranges => '%(CONFIG_NEUTRON_LB_VLAN_RANGES)s',
  sql_connection      => $neutron_sql_connection
}
