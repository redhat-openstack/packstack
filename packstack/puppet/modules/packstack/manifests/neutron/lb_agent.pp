class packstack::neutron::lb_agent ()
{
    $neutron_lb_interface_mappings = hiera_array('CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS')

    $use_subnets_value = hiera('CONFIG_USE_SUBNETS')
    $use_subnets = $use_subnets_value ? {
      'y'     => true,
      default => false,
    }

    class { '::neutron::agents::ml2::linuxbridge':
      physical_interface_mappings => force_interface($neutron_lb_interface_mappings, $use_subnets),
    }
}
