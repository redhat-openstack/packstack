class {'quantum::agents::metadata':
  auth_password => '%(CONFIG_QUANTUM_KS_PW)s',
  auth_url      => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
  shared_secret => '%(CONFIG_QUANTUM_METADATA_PW)s',
  metadata_ip   => '%(CONFIG_NOVA_API_HOST)s',
}
