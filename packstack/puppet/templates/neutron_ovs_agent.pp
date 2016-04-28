
$neutron_ovs_tunnel_if = hiera('CONFIG_NEUTRON_OVS_TUNNEL_IF', undef)
if $neutron_ovs_tunnel_if {
  $ovs_agent_vxlan_cfg_neut_ovs_tun_if = force_interface($neutron_ovs_tunnel_if, $use_subnets)
} else {
  $ovs_agent_vxlan_cfg_neut_ovs_tun_if = undef
}

if $ovs_agent_vxlan_cfg_neut_ovs_tun_if != '' {
  $iface = regsubst($ovs_agent_vxlan_cfg_neut_ovs_tun_if, '[\.\-\:]', '_', 'G')
  $localip = inline_template("<%%= scope.lookupvar('::ipaddress_${iface}') %%>")
} else {
  $localip = $cfg_neutron_ovs_host
}

if $network_host {
  $bridge_ifaces_param = 'CONFIG_NEUTRON_OVS_BRIDGE_IFACES'
  $bridge_mappings_param = 'CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'
} else {
  $bridge_ifaces_param = 'CONFIG_NEUTRON_OVS_BRIDGE_IFACES_COMPUTE'
  $bridge_mappings_param = 'CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS_COMPUTE'
}

if $create_bridges {
  $bridge_uplinks  = hiera_array($bridge_ifaces_param)
  $bridge_mappings = hiera_array($bridge_mappings_param)
} else {
  $bridge_uplinks  = []
  $bridge_mappings = []
}

class { '::neutron::agents::ml2::ovs':
  bridge_uplinks   => $bridge_uplinks,
  bridge_mappings  => $bridge_mappings,
  enable_tunneling => hiera('CONFIG_NEUTRON_OVS_TUNNELING'),
  tunnel_types     => hiera_array('CONFIG_NEUTRON_OVS_TUNNEL_TYPES'),
  local_ip         => force_ip($localip),
  vxlan_udp_port   => hiera('CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT',undef),
  l2_population    => hiera('CONFIG_NEUTRON_USE_L2POPULATION'),
  firewall_driver  => hiera('FIREWALL_DRIVER'),
}
