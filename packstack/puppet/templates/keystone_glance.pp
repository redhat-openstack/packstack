
class { '::glance::keystone::auth':
  region           => hiera('CONFIG_KEYSTONE_REGION'),
  password         => hiera('CONFIG_GLANCE_KS_PW'),
  public_address   => hiera('CONFIG_STORAGE_HOST_URL'),
  admin_address    => hiera('CONFIG_STORAGE_HOST_URL'),
  internal_address => hiera('CONFIG_STORAGE_HOST_URL'),
}
