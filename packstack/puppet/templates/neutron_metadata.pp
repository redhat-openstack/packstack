class {'neutron::agents::metadata':
  auth_password => '%(CONFIG_NEUTRON_KS_PW)s',
  auth_url      => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
  auth_region   => '%(CONFIG_KEYSTONE_REGION)s',
  shared_secret => '%(CONFIG_NEUTRON_METADATA_PW)s',
  metadata_ip   => '%(CONFIG_CONTROLLER_HOST)s',
  debug         => %(CONFIG_DEBUG_MODE)s,
}
