class { 'neutron::agents::lbaas':
  interface_driver => '%(CONFIG_NEUTRON_LBAAS_INTERFACE_DRIVER)s',
  device_driver => 'neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver',
  user_group => 'haproxy',
}
