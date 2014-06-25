class { 'neutron::agents::metering':
  interface_driver => '%(CONFIG_NEUTRON_METERING_IFCE_DRIVER)s',
  debug            => %(CONFIG_DEBUG_MODE)s,
}
