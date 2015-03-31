class { '::neutron::agents::dhcp':
  interface_driver => hiera('CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'),
  debug            => hiera('CONFIG_DEBUG_MODE'),
}

