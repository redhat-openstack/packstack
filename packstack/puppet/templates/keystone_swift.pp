class { 'swift::keystone::auth':
  address  => '%(CONFIG_SWIFT_PROXY)s',
  password => '%(CONFIG_SWIFT_KS_PW)s',
}
