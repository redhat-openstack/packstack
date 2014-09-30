class { 'swift::keystone::auth':
  public_address  => '%(CONFIG_CONTROLLER_HOST)s',
  region => '%(CONFIG_KEYSTONE_REGION)s',
  password => '%(CONFIG_SWIFT_KS_PW)s',
}
