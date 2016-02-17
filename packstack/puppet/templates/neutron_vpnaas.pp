class { '::neutron::agents::vpnaas':
  enabled           => true,
  vpn_device_driver => 'neutron_vpnaas.services.vpn.device_drivers.libreswan_ipsec.LibreSwanDriver',
}

# FIXME: this is a workaround until
# https://bugs.launchpad.net/puppet-neutron/+bug/1538971 is fixed

file_line { 'vpnaas_service_provider':
  path    => '/etc/neutron/neutron_vpnaas.conf',
  match   => '^service_provider +=.*',
  line    => 'service_provider = VPN:libreswan:neutron_vpnaas.services.vpn.service_drivers.ipsec.IPsecVPNDriver:default',
  require => Class['::neutron::agents::vpnaas'],
  notify  => Service['neutron-server'],
}
