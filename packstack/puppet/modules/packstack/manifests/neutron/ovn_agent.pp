class packstack::neutron::ovn_agent ()
{
    $my_ip = choose_my_ip(lookup('HOST_LIST'))
    $my_ip_without_dot = regsubst($my_ip, '[\.\:]', '_', 'G')
    $neutron_tunnel_rule_name = "FIREWALL_NEUTRON_TUNNEL_RULES_${my_ip_without_dot}"
    create_resources(packstack::firewall, lookup($neutron_tunnel_rule_name, undef, undef, {}))

    $neutron_ovn_tunnel_if = lookup('CONFIG_NEUTRON_OVN_TUNNEL_IF', undef, undef, undef)

    $use_subnets_value = lookup('CONFIG_USE_SUBNETS')
    $use_subnets = $use_subnets_value ? {
      'y'     => true,
      default => false,
    }

    if $neutron_ovn_tunnel_if {
      $ovn_agent_tunnel_cfg_neut_ovs_tun_if = force_interface($neutron_ovn_tunnel_if, $use_subnets)
    } else {
      $ovn_agent_tunnel_cfg_neut_ovs_tun_if = undef
    }

    if $ovn_agent_tunnel_cfg_neut_ovs_tun_if != '' {
      $iface = regsubst($ovn_agent_tunnel_cfg_neut_ovs_tun_if, '[\.\-\:]', '_', 'G')
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

    $ovn_southd = "tcp:${lookup('CONFIG_CONTROLLER_HOST')}:6642"

    class { 'ovn::controller':
      ovn_remote                => $ovn_southd,
      ovn_bridge_mappings       => $bridge_mappings,
      bridge_interface_mappings => $bridge_uplinks,
      ovn_encap_ip              => force_ip($localip),
      hostname                  => $facts['networking']['fqdn'],
      ovn_cms_options           => 'enable-chassis-as-gw',
    }
}
