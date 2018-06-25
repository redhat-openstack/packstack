class packstack::neutron::ml2 ()
{
    if hiera('CONFIG_NEUTRON_ML2_VXLAN_GROUP') == '' {
      $vxlan_group_value = undef
    } else {
      $vxlan_group_value = hiera('CONFIG_NEUTRON_ML2_VXLAN_GROUP')
    }

    class { '::neutron::plugins::ml2':
      type_drivers              => hiera_array('CONFIG_NEUTRON_ML2_TYPE_DRIVERS'),
      tenant_network_types      => hiera_array('CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES'),
      mechanism_drivers         => hiera_array('CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS'),
      flat_networks             => hiera_array('CONFIG_NEUTRON_ML2_FLAT_NETWORKS'),
      network_vlan_ranges       => hiera_array('CONFIG_NEUTRON_ML2_VLAN_RANGES'),
      tunnel_id_ranges          => hiera_array('CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES'),
      vxlan_group               => $vxlan_group_value,
      vni_ranges                => hiera_array('CONFIG_NEUTRON_ML2_VNI_RANGES'),
      enable_security_group     => true,
      firewall_driver           => hiera('FIREWALL_DRIVER'),
      extension_drivers         => 'port_security,qos',
      max_header_size           => 38,
    }

    if hiera('CONFIG_NEUTRON_L2_AGENT') == 'ovn' {
      class {'::neutron::plugins::ml2::ovn':
        ovn_nb_connection => "tcp:${hiera('CONFIG_CONTROLLER_HOST')}:6641",
        ovn_sb_connection => "tcp:${hiera('CONFIG_CONTROLLER_HOST')}:6642",
        ovn_metadata_enabled => true,
      }
    }

    # For cases where "neutron-db-manage upgrade" command is called
    # we need to fill config file first
    if defined(Exec['neutron-db-manage upgrade']) {
      Neutron_plugin_ml2<||> ->
      File['/etc/neutron/plugin.ini'] ->
      Exec['neutron-db-manage upgrade']
    }
}
