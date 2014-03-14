
# We need this before https://review.openstack.org/#/c/67004/ will be merged
if 'openvswitch' in %(CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS)s and !defined(Package['neutron-plugin-ovs']) {
  package {'neutron-plugin-ovs':
    name   => 'openstack-neutron-openvswitch',
    ensure => 'installed',
    before => Class['neutron::plugins::ml2']
  }
}

if 'linuxbridge' in %(CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS)s and !defined(Package['neutron-plugin-linuxbridge']) {
  package {'neutron-plugin-linuxbridge':
    name   => 'openstack-neutron-linuxbridge',
    ensure => 'installed',
    before => Class['neutron::plugins::ml2']
  }
}

class { 'neutron::plugins::ml2':
  type_drivers          => %(CONFIG_NEUTRON_ML2_TYPE_DRIVERS)s,
  tenant_network_types  => %(CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES)s,
  mechanism_drivers     => %(CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS)s,
  flat_networks         => %(CONFIG_NEUTRON_ML2_FLAT_NETWORKS)s,
  network_vlan_ranges   => %(CONFIG_NEUTRON_ML2_VLAN_RANGES)s,
  tunnel_id_ranges      => %(CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES)s,
  vxlan_group           => %(CONFIG_NEUTRON_ML2_VXLAN_GROUP)s,
  vni_ranges            => %(CONFIG_NEUTRON_ML2_VNI_RANGES)s,
  enable_security_group => 'dummy',
}

# For cases where "neutron-db-manage upgrade" command is called we need to fill config file first
if defined(Exec['neutron-db-manage upgrade']) {
  Neutron_plugin_ml2<||> -> File['/etc/neutron/plugin.ini'] -> Exec['neutron-db-manage upgrade']
}
