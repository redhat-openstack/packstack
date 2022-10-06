class packstack::neutron::l3 ()
{
    $start_l3_agent = lookup('CONFIG_NEUTRON_VPNAAS') ? {
        'y'     => false,
        default => true
    }

    class { 'neutron::agents::l3':
      interface_driver => lookup('CONFIG_NEUTRON_L3_INTERFACE_DRIVER'),
      manage_service   => $start_l3_agent,
      enabled          => $start_l3_agent,
      debug            => lookup('CONFIG_DEBUG_MODE'),
    }

    sysctl::value { 'net.ipv4.ip_forward':
      value => '1',
    }
}
