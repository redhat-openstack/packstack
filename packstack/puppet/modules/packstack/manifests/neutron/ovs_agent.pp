class packstack::neutron::ovs_agent ()
{
    $my_ip = choose_my_ip(lookup('HOST_LIST'))
    $my_ip_without_dot = regsubst($my_ip, '[\.\:]', '_', 'G')
    $neutron_tunnel_rule_name = "FIREWALL_NEUTRON_TUNNEL_RULES_${my_ip_without_dot}"
    create_resources(packstack::firewall, lookup($neutron_tunnel_rule_name, undef, undef, {}))

    $neutron_ovs_tunnel_if = lookup('CONFIG_NEUTRON_OVS_TUNNEL_IF', undef, undef, undef)

    $use_subnets_value = lookup('CONFIG_USE_SUBNETS')
    $use_subnets = $use_subnets_value ? {
      'y'     => true,
      default => false,
    }

    if $neutron_ovs_tunnel_if {
      $ovs_agent_vxlan_cfg_neut_ovs_tun_if = force_interface($neutron_ovs_tunnel_if, $use_subnets)
    } else {
      $ovs_agent_vxlan_cfg_neut_ovs_tun_if = undef
    }

    if $ovs_agent_vxlan_cfg_neut_ovs_tun_if != '' {
      $iface = regsubst($ovs_agent_vxlan_cfg_neut_ovs_tun_if, '[\.\-\:]', '_', 'G')
      $localip = inline_template("<%= scope.lookupvar('::ipaddress_${iface}') %>")
    } else {
      $localip = choose_my_ip(lookup('HOST_LIST'))
    }

    $network_hosts =  split(lookup('CONFIG_NETWORK_HOSTS'),',')
    if member($network_hosts, choose_my_ip(lookup('HOST_LIST'))) {
      $bridge_ifaces_param = 'CONFIG_NEUTRON_OVS_BRIDGE_IFACES'
      $bridge_mappings_param = 'CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS'
    } else {
      $bridge_ifaces_param = 'CONFIG_NEUTRON_OVS_BRIDGE_IFACES_COMPUTE'
      $bridge_mappings_param = 'CONFIG_NEUTRON_OVS_BRIDGE_MAPPINGS_COMPUTE'
    }

    if lookup('CREATE_BRIDGES') == 'y' {
      $bridge_uplinks  = lookup($bridge_ifaces_param, { merge => 'unique' })
      $bridge_mappings = lookup($bridge_mappings_param, { merge => 'unique' })
    } else {
      $bridge_uplinks  = []
      $bridge_mappings = []
    }

    class { 'neutron::agents::ml2::ovs':
      bridge_uplinks  => $bridge_uplinks,
      bridge_mappings => $bridge_mappings,
      tunnel_types    => lookup('CONFIG_NEUTRON_OVS_TUNNEL_TYPES', { merge => 'unique' }),
      local_ip        => force_ip($localip),
      vxlan_udp_port  => lookup('CONFIG_NEUTRON_OVS_VXLAN_UDP_PORT', undef, undef, undef),
      l2_population   => lookup('CONFIG_NEUTRON_USE_L2POPULATION'),
      firewall_driver => lookup('FIREWALL_DRIVER'),
    }
}
