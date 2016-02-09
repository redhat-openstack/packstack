class { '::neutron::agents::vpnaas':
  enabled           => true,
  vpn_device_driver => 'neutron_vpnaas.services.vpn.device_drivers.libreswan_ipsec.LibreSwanDriver',
}

