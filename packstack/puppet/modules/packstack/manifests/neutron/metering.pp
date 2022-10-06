class packstack::neutron::metering ()
{
    class { 'neutron::agents::metering':
      interface_driver => lookup('CONFIG_NEUTRON_METERING_IFCE_DRIVER'),
      debug            => lookup('CONFIG_DEBUG_MODE'),
    }
}
