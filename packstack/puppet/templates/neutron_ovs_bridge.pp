if '%(CONFIG_NEUTRON_L2_PLUGIN)s' == 'ml2' {
  $agent_service = 'neutron-ovs-agent-service'
} else {
  $agent_service = 'neutron-plugin-ovs-service'
}

vs_bridge { '%(CONFIG_NEUTRON_OVS_BRIDGE)s':
  ensure  => present,
  require => Service["${agent_service}"]
}
