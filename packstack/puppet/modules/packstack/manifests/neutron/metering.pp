class packstack::neutron::metering ()
{
    class { '::neutron::agents::metering':
      interface_driver => hiera('CONFIG_NEUTRON_METERING_IFCE_DRIVER'),
      debug            => hiera('CONFIG_DEBUG_MODE'),
    }
}
