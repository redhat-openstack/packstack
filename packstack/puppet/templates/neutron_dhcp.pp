class { 'neutron::agents::dhcp':
  interface_driver => '%(CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER)s',
}
