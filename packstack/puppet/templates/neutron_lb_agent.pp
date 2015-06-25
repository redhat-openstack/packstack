
$neutron_lb_interface_mappings = hiera_array('CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS')
class { '::neutron::agents::ml2::linuxbridge':
  physical_interface_mappings => force_interface($neutron_lb_interface_mappings, $use_subnets),
}
