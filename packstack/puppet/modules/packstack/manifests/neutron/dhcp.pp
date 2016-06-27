class packstack::neutron::dhcp ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_NEUTRON_DHCPIN_RULES', {}))
    create_resources(packstack::firewall, hiera('FIREWALL_NEUTRON_DHCPOUT_RULES', {}))

    class { '::neutron::agents::dhcp':
      interface_driver    => hiera('CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'),
      debug               => hiera('CONFIG_DEBUG_MODE'),
    }
}
