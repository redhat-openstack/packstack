class packstack::neutron::l3 ()
{
    $start_l3_agent = hiera('CONFIG_NEUTRON_VPNAAS') ? {
        'y'     => false,
        default => true
    }

    $neutron_fwaas_enabled   = str2bool(hiera('CONFIG_NEUTRON_FWAAS'))
    if $neutron_fwaas_enabled {
      $extensions = 'fwaas'
    } else {
      $extensions = undef
    }

    class { '::neutron::agents::l3':
      interface_driver        => hiera('CONFIG_NEUTRON_L3_INTERFACE_DRIVER'),
      manage_service          => $start_l3_agent,
      enabled                 => $start_l3_agent,
      debug                   => hiera('CONFIG_DEBUG_MODE'),
      extensions              => $extensions
    }

    if defined(Class['neutron::services::fwaas']) {
      Class['neutron::services::fwaas'] -> Class['neutron::agents::l3']
    }

    sysctl::value { 'net.ipv4.ip_forward':
      value => '1',
    }
}
