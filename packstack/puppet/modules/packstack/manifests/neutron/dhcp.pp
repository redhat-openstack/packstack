class packstack::neutron::dhcp ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_NEUTRON_DHCPIN_RULES', undef, undef, {}))
    create_resources(packstack::firewall, lookup('FIREWALL_NEUTRON_DHCPOUT_RULES', undef, undef, {}))

    class { 'neutron::agents::dhcp':
      interface_driver => lookup('CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'),
      debug            => lookup('CONFIG_DEBUG_MODE'),
    }
}
