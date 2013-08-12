vs_bridge { '%(CONFIG_NEUTRON_OVS_BRIDGE)s':
  ensure => present,
  require => Service['neutron-plugin-ovs-service']
}
