class packstack::neutron::l3 ()
{
    $start_l3_agent = hiera('CONFIG_NEUTRON_VPNAAS') ? {
        'y'     => false,
        default => true
    }

    class { '::neutron::agents::l3':
      interface_driver => hiera('CONFIG_NEUTRON_L3_INTERFACE_DRIVER'),
      manage_service   => $start_l3_agent,
      enabled          => $start_l3_agent,
      debug            => hiera('CONFIG_DEBUG_MODE'),
    }

    sysctl::value { 'net.ipv4.ip_forward':
      value => '1',
    }
}
