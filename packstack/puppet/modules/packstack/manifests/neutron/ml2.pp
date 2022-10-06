class packstack::neutron::ml2 ()
{
    if lookup('CONFIG_NEUTRON_ML2_VXLAN_GROUP') == '' {
      $vxlan_group_value = undef
    } else {
      $vxlan_group_value = lookup('CONFIG_NEUTRON_ML2_VXLAN_GROUP')
    }

    class { 'neutron::plugins::ml2':
      type_drivers          => lookup('CONFIG_NEUTRON_ML2_TYPE_DRIVERS', { merge => 'unique' }),
      tenant_network_types  => lookup('CONFIG_NEUTRON_ML2_TENANT_NETWORK_TYPES', { merge => 'unique' }),
      mechanism_drivers     => lookup('CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS', { merge => 'unique' }),
      flat_networks         => lookup('CONFIG_NEUTRON_ML2_FLAT_NETWORKS', { merge => 'unique' }),
      network_vlan_ranges   => lookup('CONFIG_NEUTRON_ML2_VLAN_RANGES', { merge => 'unique' }),
      tunnel_id_ranges      => lookup('CONFIG_NEUTRON_ML2_TUNNEL_ID_RANGES', { merge => 'unique' }),
      vxlan_group           => $vxlan_group_value,
      vni_ranges            => lookup('CONFIG_NEUTRON_ML2_VNI_RANGES', { merge => 'unique' }),
      enable_security_group => true,
      extension_drivers     => 'port_security,qos',
      max_header_size       => 38,
    }

    if lookup('CONFIG_NEUTRON_L2_AGENT') == 'ovn' {
      class { 'neutron::plugins::ml2::ovn':
        ovn_nb_connection    => "tcp:${lookup('CONFIG_CONTROLLER_HOST')}:6641",
        ovn_sb_connection    => "tcp:${lookup('CONFIG_CONTROLLER_HOST')}:6642",
        ovn_metadata_enabled => true,
      }
    }

    # For cases where "neutron-db-manage upgrade" command is called
    # we need to fill config file first
    if defined(Exec['neutron-db-manage upgrade']) {
      Neutron_plugin_ml2<||>
      -> File['/etc/neutron/plugin.ini']
      -> Exec['neutron-db-manage upgrade']
    }
}
