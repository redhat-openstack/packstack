class { 'swift::keystone::auth':
  public_address => hiera('CONFIG_CONTROLLER_HOST'),
  region         => hiera('CONFIG_KEYSTONE_REGION'),
  password       => hiera('CONFIG_SWIFT_KS_PW'),
}
