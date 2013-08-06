class { 'neutron::plugins::ovs':
  tenant_network_type => '%(CONFIG_NEUTRON_OVS_TENANT_NETWORK_TYPE)s',
  tunnel_id_ranges => '%(CONFIG_NEUTRON_OVS_TUNNEL_RANGES)s',
  sql_connection      => $neutron_sql_connection
}
