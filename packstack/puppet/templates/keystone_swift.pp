class { 'swift::keystone::auth':
  public_address  => '%(CONFIG_CONTROLLER_HOST)s',
  password => '%(CONFIG_SWIFT_KS_PW)s',
}
