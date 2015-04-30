class { '::ceilometer::agent::auth':
  auth_url      => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  auth_password => hiera('CONFIG_CEILOMETER_KS_PW'),
}

class { '::ceilometer::agent::compute': }

