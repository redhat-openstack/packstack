class { '::swift::keystone::auth':
  public_address => hiera('CONFIG_STORAGE_HOST_URL'),
  region         => hiera('CONFIG_KEYSTONE_REGION'),
  password       => hiera('CONFIG_SWIFT_KS_PW'),
}
