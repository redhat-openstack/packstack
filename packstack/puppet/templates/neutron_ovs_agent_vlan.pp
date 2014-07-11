
if '%(CONFIG_NEUTRON_L2_PLUGIN)s' == 'ml2' {
  if ('l2population' in %(CONFIG_NEUTRON_ML2_MECHANISM_DRIVERS)s) {
    $l2population = true
  } else {
    $l2population = false
  }
  class { 'neutron::agents::ml2::ovs':
    bridge_mappings => %(CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS)s,
    l2_population   => $l2population,
  }
} else {
  class { 'neutron::agents::ovs':
    bridge_mappings => %(CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS)s,
  }

  file { 'ovs_neutron_plugin.ini':
    path    => '/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini',
    owner   => 'root',
    group   => 'neutron',
    before  => Service['ovs-cleanup-service'],
    require => Package['neutron-plugin-ovs'],
  }
}
