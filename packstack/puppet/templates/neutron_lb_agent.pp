
$neutron_lb_interface_mappings = hiera('CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS')
class { '::neutron::agents::linuxbridge':
  physical_interface_mappings => force_interface($neutron_lb_interface_mappings, $use_subnets),
}
