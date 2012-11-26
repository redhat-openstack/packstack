class { 'swift::keystone::auth':
  address  => '%(CONFIG_SWIFT_PROXY)s',
  password => 'swift_default_password',
}
