class { 'neutron::agents::dhcp':
  interface_driver    => hiera('CONFIG_NEUTRON_DHCP_INTERFACE_DRIVER'),
  debug               => hiera('CONFIG_DEBUG_MODE'),
  dnsmasq_config_file => '/etc/neutron/dnsmasq-neutron.conf',
  require             => File['/etc/neutron/dnsmasq-neutron.conf'],
}

file { '/etc/neutron/dnsmasq-neutron.conf':
  content => 'dhcp-option-force=26,1400',
  owner   => 'root',
  group   => 'neutron',
  mode    => '0640',
}

