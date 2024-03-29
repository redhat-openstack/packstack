class packstack::neutron::lb_agent ()
{

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $neutron_lb_interface_mappings = lookup('CONFIG_NEUTRON_LB_INTERFACE_MAPPINGS', { merge => 'unique' })

    $use_subnets_value = lookup('CONFIG_USE_SUBNETS')
    $use_subnets = $use_subnets_value ? {
      'y'     => true,
      default => false,
    }

    if ( 'vxlan' in lookup('CONFIG_NEUTRON_ML2_TYPE_DRIVERS', { merge => 'unique' }) ){
      class { 'neutron::agents::ml2::linuxbridge':
        physical_interface_mappings => force_interface($neutron_lb_interface_mappings, $use_subnets),
        tunnel_types                => ['vxlan'],
        local_ip                    => $bind_host,
      }
    }
    else {
      class { 'neutron::agents::ml2::linuxbridge':
        physical_interface_mappings => force_interface($neutron_lb_interface_mappings, $use_subnets),
      }
    }
}
