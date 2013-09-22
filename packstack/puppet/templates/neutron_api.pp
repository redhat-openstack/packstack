class { 'neutron::server':
  auth_password => $neutron_user_password,
  auth_host => '%(CONFIG_KEYSTONE_HOST)s',
  enabled => true,
}

