class packstack::neutron::ovs_bridge ()
{
  $agent_service = 'neutron-ovs-agent-service'

  $config_neutron_ovs_bridge = hiera('CONFIG_NEUTRON_OVS_BRIDGE')

  vs_bridge { $config_neutron_ovs_bridge:
    ensure  => present,
    require => Service[$agent_service],
  }
}
