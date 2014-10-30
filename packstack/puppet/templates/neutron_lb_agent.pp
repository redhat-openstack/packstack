class {'neutron::agents::linuxbridge':
  physical_interface_mappings => hiera('CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS'),
}
