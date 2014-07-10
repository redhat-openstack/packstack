$neutron_l2_plugin = '%(CONFIG_NEUTRON_L2_PLUGIN)s'

if $neutron_l2_plugin == 'ml2' {
  $agent_service = 'neutron-ovs-agent-service'
} else {
  $agent_service = 'neutron-plugin-ovs-service'
}

vs_bridge { '%(CONFIG_NEUTRON_OVS_BRIDGE)s':
  ensure  => present,
  require => Service["${agent_service}"]
}
