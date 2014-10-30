$ovs_bridge_cfg_neut_l2_plugin = hiera('CONFIG_NEUTRON_L2_PLUGIN')

if $ovs_bridge_cfg_neut_l2_plugin == 'ml2' {
  $agent_service = 'neutron-ovs-agent-service'
} else {
  $agent_service = 'neutron-plugin-ovs-service'
}

$config_neutron_ovs_bridge = hiera('CONFIG_NEUTRON_OVS_BRIDGE')

vs_bridge { $config_neutron_ovs_bridge:
  ensure  => present,
  require => Service[$agent_service],
}
