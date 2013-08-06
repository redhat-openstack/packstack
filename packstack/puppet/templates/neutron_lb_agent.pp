class {'neutron::agents::linuxbridge':
  physical_interface_mappings => '%(CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS)s',
}
