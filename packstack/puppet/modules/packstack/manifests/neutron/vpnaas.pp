class packstack::neutron::vpnaas ()
{
    class { 'neutron::agents::vpnaas':
      vpn_device_driver => 'neutron_vpnaas.services.vpn.device_drivers.libreswan_ipsec.LibreSwanDriver',
    }
}
