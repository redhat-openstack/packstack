
$start_l3_agent = hiera('CONFIG_NEUTRON_VPNAAS') ? {
    'y'     => false,
    default => true
}

class { '::neutron::agents::l3':
  interface_driver        => hiera('CONFIG_NEUTRON_L3_INTERFACE_DRIVER'),
  external_network_bridge => hiera('CONFIG_NEUTRON_L3_EXT_BRIDGE'),
  manage_service          => $start_l3_agent,
  enabled                 => $start_l3_agent,
  debug                   => hiera('CONFIG_DEBUG_MODE'),
}

if defined(Class['neutron::services::fwaas']) {
  Class['neutron::services::fwaas'] -> Class['neutron::agents::l3']
}

sysctl::value { 'net.ipv4.ip_forward':
  value => '1',
}
