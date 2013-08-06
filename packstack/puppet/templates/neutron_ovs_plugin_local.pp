class { 'neutron::plugins::ovs':
  tenant_network_type => '%(CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE)s',
  sql_connection      => $neutron_sql_connection
}
