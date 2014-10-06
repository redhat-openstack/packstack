
if hiera('CONFIG_NEUTRON_L2_PLUGIN') == 'ml2' {
  class { 'neutron::agents::ml2::ovs':
    bridge_mappings => hiera_array('CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'),
    l2_population   => hiera('CONFIG_NEUTRON_USE_L2POPULATION'),
  }
} else {
  class { 'neutron::agents::ovs':
    bridge_mappings => hiera_array('CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'),
  }

  file { 'ovs_neutron_plugin.ini':
    path    => '/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini',
    owner   => 'root',
    group   => 'neutron',
    before  => Service['ovs-cleanup-service'],
    require => Package['neutron-plugin-ovs'],
  }
}
