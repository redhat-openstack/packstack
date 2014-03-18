class { 'swift::keystone::auth':
  public_address  => '%(CONFIG_SWIFT_PROXY)s',
  password => '%(CONFIG_SWIFT_KS_PW)s',
}
