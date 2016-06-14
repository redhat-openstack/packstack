class packstack::neutron::vpnaas ()
{
    class { '::neutron::agents::vpnaas':
      enabled           => true,
      vpn_device_driver => 'neutron_vpnaas.services.vpn.device_drivers.libreswan_ipsec.LibreSwanDriver',
    } ->
    class { '::neutron::services::vpnaas':
      service_providers => 'VPN:libreswan:neutron_vpnaas.services.vpn.service_drivers.ipsec.IPsecVPNDriver:default',
      notify            => Service['neutron-server'],
    }
}
