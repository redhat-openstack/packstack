$ovs_agent_vxlan_cfg_neut_ovs_tun_if = hiera('CONFIG_NEUTRON_OVS_TUNNEL_IF',undef)

if $ovs_agent_vxlan_cfg_neut_ovs_tun_if != '' {
  $iface = regsubst($ovs_agent_vxlan_cfg_neut_ovs_tun_if, '[\.\-\:]', '_', 'G')
  $localip = inline_template("<%%= scope.lookupvar('::ipaddress_${iface}') %%>")
} else {
  $localip = $cfg_neutron_ovs_host
}

class { 'neutron::agents::ml2::ovs':
  bridge_mappings  => hiera_array('CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'),
  enable_tunneling => hiera('CONFIG_NEUTRON_OVS_TUNNELING'),
  tunnel_types     => hiera_array('CONFIG_NEUTRON_OVS_TUNNEL_TYPES'),
  local_ip         => $localip,
  vxlan_udp_port   => hiera('CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT',undef),
  l2_population    => hiera('CONFIG_NEUTRON_USE_L2POPULATION'),
}
